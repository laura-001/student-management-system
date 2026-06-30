from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.models import Course
from schemas.course import CourseCreate, CourseUpdate


def list_courses(
    db: Session,
    *,
    department_id: int | None = None,
    year_of_study: int | None = None,
    semester: int | None = None,
    active_only: bool = True,
) -> list[Course]:
    query = db.query(Course)
    if active_only:
        query = query.filter(Course.is_active == True)
    if department_id is not None:
        query = query.filter(Course.department_id == department_id)
    if year_of_study is not None:
        query = query.filter(Course.year_of_study == year_of_study)
    if semester is not None:
        query = query.filter(Course.semester == semester)
    return query.order_by(Course.course_code).all()


def get_course(db: Session, course_id: int) -> Course | None:
    return db.query(Course).filter(Course.id == course_id).first()


def create_course(db: Session, payload: CourseCreate) -> Course:
    data = payload.model_dump()
    course = Course(**data)
    db.add(course)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(course)
    return course


def update_course(db: Session, course: Course, payload: CourseUpdate) -> Course:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(course)
    return course


def deactivate_course(db: Session, course: Course) -> Course:
    course.is_active = False
    db.commit()
    db.refresh(course)
    return course
