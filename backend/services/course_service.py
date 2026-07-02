from sqlalchemy.orm import Session

from database.models import Course


def add_course(
    db: Session,
    course_code: str,
    course_name: str,
    credit_units: int,
    year_of_study: int,
    semester: int,
    department_id: int | None = None,
    total_slots: int = 60,
) -> Course:
    course = Course(
        course_code=course_code,
        course_name=course_name,
        department_id=department_id,
        credit_units=credit_units,
        year_of_study=year_of_study,
        semester=semester,
        total_slots=total_slots,
        available_slots=total_slots,
        is_active=True,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def get_all_courses(db: Session) -> list[Course]:
    return db.query(Course).filter(Course.is_active.is_(True)).all()
