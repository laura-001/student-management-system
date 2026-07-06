from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from database.models import Lecturer, User
from schemas.lecturer import LecturerCreate, LecturerUpdate
from services.auth_service import create_staff_user, next_lecturer_number


def create_lecturer(db: Session, payload: LecturerCreate) -> Lecturer:
    user = create_staff_user(
        db,
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        role="lecturer",
    )
    lecturer = Lecturer(
        user_id=user.id,
        lecturer_number=payload.lecturer_number or next_lecturer_number(db),
        department_id=payload.department_id,
        title=payload.title,
    )
    db.add(lecturer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(lecturer)
    return lecturer


def list_lecturers(db: Session) -> list[Lecturer]:
    return db.query(Lecturer).options(joinedload(Lecturer.user)).order_by(Lecturer.lecturer_number).all()


def get_lecturer(db: Session, user_id: int) -> Lecturer | None:
    return (
        db.query(Lecturer)
        .options(joinedload(Lecturer.user))
        .filter(Lecturer.user_id == user_id)
        .first()
    )


def update_lecturer(db: Session, lecturer: Lecturer, payload: LecturerUpdate) -> Lecturer:
    data = payload.model_dump(exclude_unset=True)
    user_fields = {"full_name", "email", "is_active"}
    for field in user_fields & data.keys():
        setattr(lecturer.user, field, data[field])
    for field in {"lecturer_number", "department_id", "title"} & data.keys():
        setattr(lecturer, field, data[field])
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(lecturer)
    return lecturer


def deactivate_lecturer(db: Session, lecturer: Lecturer) -> Lecturer:
    lecturer.user.is_active = False
    db.commit()
    db.refresh(lecturer)
    return lecturer
