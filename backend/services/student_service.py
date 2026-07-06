from sqlalchemy.orm import Session

from database.models import Student


def get_student_by_user_id(db: Session, user_id: int) -> Student | None:
    return db.query(Student).filter(Student.user_id == user_id).first()
