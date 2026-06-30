from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from database.models import Course, Registration, User
from dsa import HashTable, Queue


def _registration_index(registrations: list[Registration]) -> HashTable[tuple[int, int], Registration]:
    index: HashTable[tuple[int, int], Registration] = HashTable()
    for registration in registrations:
        index.set((registration.student_id, registration.course_id), registration)
    return index


def _course_waitlist(db: Session, course_id: int) -> Queue[Registration]:
    waitlisted = (
        db.query(Registration)
        .options(joinedload(Registration.course))
        .filter(Registration.course_id == course_id, Registration.status == "waitlisted")
        .order_by(Registration.registered_at.asc(), Registration.id.asc())
        .all()
    )
    return Queue(waitlisted)


def list_student_registrations(db: Session, student_id: int) -> list[Registration]:
    return (
        db.query(Registration)
        .options(joinedload(Registration.course))
        .filter(Registration.student_id == student_id)
        .order_by(Registration.registered_at.desc())
        .all()
    )


def get_registration(db: Session, registration_id: int) -> Registration | None:
    return (
        db.query(Registration)
        .options(joinedload(Registration.course))
        .filter(Registration.id == registration_id)
        .first()
    )


def register_for_course(db: Session, user: User, course_id: int) -> Registration:
    course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
    if course is None:
        raise ValueError("Course not found.")

    student_registrations = (
        db.query(Registration)
        .filter(Registration.student_id == user.student.user_id)
        .all()
    )
    registration_index = _registration_index(student_registrations)
    if registration_index.contains((user.student.user_id, course_id)):
        raise IntegrityError("duplicate registration", params=None, orig=None)

    status = "active" if course.available_slots > 0 else "waitlisted"
    if status == "active":
        course.available_slots -= 1

    registration = Registration(student_id=user.student.user_id, course_id=course.id, status=status)
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return get_registration(db, registration.id)


def drop_registration(db: Session, registration: Registration) -> Registration:
    if registration.status == "active":
        registration.status = "dropped"
        registration.dropped_at = datetime.now(timezone.utc)
        waitlist = _course_waitlist(db, registration.course_id)
        promoted = waitlist.dequeue()
        if promoted is not None:
            promoted.status = "active"
        elif registration.course is not None and registration.course.available_slots < registration.course.total_slots:
            registration.course.available_slots += 1
    elif registration.status == "waitlisted":
        registration.status = "dropped"
        registration.dropped_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(registration)
    return registration
