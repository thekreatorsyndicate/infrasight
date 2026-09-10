import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.database.models import Base


def get_database_url() -> str:
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    return "sqlite:///data/live_infrasight.db"


_engine = None
_SessionFactory = None


def init_database(database_url: str = None):
    global _engine, _SessionFactory
    url = database_url or get_database_url()
    _engine = create_engine(url, echo=False, future=True)
    _SessionFactory = sessionmaker(bind=_engine, class_=Session, expire_on_commit=False)
    Base.metadata.create_all(_engine)
    return _engine


def get_engine():
    global _engine
    if _engine is None:
        init_database()
    return _engine


def get_session_factory():
    global _SessionFactory
    if _SessionFactory is None:
        init_database()
    return _SessionFactory


@contextmanager
def session_scope():
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Session:
    session_factory = get_session_factory()
    return session_factory()
