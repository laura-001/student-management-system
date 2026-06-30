from sqlalchemy.orm import Session

from database.models import Student, User


def add_student(
    db: Session,
    user: User,
    student_number: str,
    year_of_study: int | None = None,
) -> Student:
    student = Student(
        user_id=user.id,
        student_number=student_number,
        year_of_study=year_of_study,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_all_students(db: Session) -> list[Student]:
    return db.query(Student).all()
