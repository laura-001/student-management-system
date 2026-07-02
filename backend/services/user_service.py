from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from database.models import User
from schemas.user import UserUpdate


def list_users(
    db: Session,
    *,
    role: str | None = None,
    active_only: bool | None = None,
) -> list[User]:
    query = db.query(User).options(joinedload(User.student), joinedload(User.admin), joinedload(User.lecturer))
    if role is not None:
        query = query.filter(User.role == role)
    if active_only is not None:
        query = query.filter(User.is_active == active_only)
    return query.order_by(User.id).all()


def get_user(db: Session, user_id: int) -> User | None:
    return (
        db.query(User)
        .options(joinedload(User.student), joinedload(User.admin), joinedload(User.lecturer))
        .filter(User.id == user_id)
        .first()
    )


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(user)
    return user


def set_user_active(db: Session, user: User, is_active: bool) -> User:
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user
