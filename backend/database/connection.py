#PostgreSQL database connection using SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from core.config import settings

# Create the SQLAlchemy engine with connection pooling and pre-ping to ensure connections are alive
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,)
#session_local is a factory for creating new SQLAlchemy sessions. It is configured to not autocommit and not autoflush, and it binds to the engine we created.
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base is the base class for all our database models. We will inherit from this class when defining our models.
Base = declarative_base()

# Dependency function to get a database session. This will be used in our FastAPI routes to provide a database session for each request.
def get_db():
    db = session_local()
    try:
        yield db
    except Exception as e:
        print(f"Database error: {e}")
        db.rollback()
    finally:       
        db.close()

#Utility function to create all tables in models.py
def init_db():
    from . import models 
    Base.metadata.create_all(bind=engine)
