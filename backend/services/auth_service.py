from sqlalchemy.orm import Session

from core.security import hash_password, verify_password
from database.models import User


def register_user(db: Session, full_name: str, email: str, password: str, role: str) -> User:
    user = User(
        full_name=full_name,
        email=email.lower(),
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email.lower(), User.is_active.is_(True)).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None
