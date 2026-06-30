from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from core.permissions import permissions_for_role
from core.security import create_access_token, hash_password, verify_password
from database.models import Admin, Lecturer, Student, User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_with_profile(db: Session, user_id: int) -> User | None:
    return (
        db.query(User)
        .options(joinedload(User.student), joinedload(User.admin), joinedload(User.lecturer))
        .filter(User.id == user_id)
        .first()
    )


def _next_profile_number(db: Session, model, field_name: str, prefix: str) -> str:
    field = getattr(model, field_name)
    for number in range(1, 1_000_000):
        candidate = f"{prefix}-{number:06d}"
        if db.query(model).filter(field == candidate).first() is None:
            return candidate
    raise ValueError(f"Could not generate a unique {field_name}.")


def next_student_number(db: Session) -> str:
    return _next_profile_number(db, Student, "student_number", "STU")


def next_lecturer_number(db: Session) -> str:
    return _next_profile_number(db, Lecturer, "lecturer_number", "LEC")


def create_student_user(db: Session, full_name: str, email: str, password: str) -> User:
    user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role="student",
        is_active=True,
    )
    db.add(user)
    db.flush()
    db.add(Student(user_id=user.id, student_number=next_student_number(db)))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(user)
    return user


def create_staff_user(
    db: Session,
    *,
    full_name: str,
    email: str,
    password: str,
    role: str,
) -> User:
    user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def issue_token(user: User) -> str:
    return create_access_token({"user_id": user.id, "role": user.role})


def profile_payload(user: User) -> dict:
    return {
        "user": user,
        "student": user.student if user.role == "student" else None,
        "admin": user.admin if user.role == "admin" else None,
        "lecturer": user.lecturer if user.role == "lecturer" else None,
        "permissions": permissions_for_role(user.role),
    }
