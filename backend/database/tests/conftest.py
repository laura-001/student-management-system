import os
import sys

# make `backend` package importable so `import database` works
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from database.connection import Base


@pytest.fixture(scope="session")
def engine():
    # in-memory SQLite for fast tests; enable FK support
    engine = create_engine("sqlite:///:memory:", echo=False, future=True)

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # create all tables from SQLAlchemy metadata
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db_session(engine):
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
