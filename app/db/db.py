"""Module for Session initialization."""
from contextlib import contextmanager

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import url_object


def get_engine() -> Engine:
    """Create and return engine

    Returns:
        Engine instance
    """
    return create_engine(url_object)


@contextmanager
def db_session():
    """Creates context manager with SQLAlchemy session."""
    engine = get_engine()
    session_generator = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    session = session_generator()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()
