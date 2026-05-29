#core/dependencies.py
#Fast API dependencies for database sessions and authentication

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.security import verify_access_token
from database.connection import get_db
from database import models

# OAuth2 scheme for token extraction from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = "Invalid or expired token. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_access_token(token)

    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("user_id")
     
    if user_id is None:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id,models.User.is_active == True).first()

    if user is None:
        raise credentials_exception
    
    return user
