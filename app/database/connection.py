import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.models.base import Base
from app.utils.config import config_manager
from app.utils.logger import logger

# Declare global engine and sessionmaker
_engine = None
_SessionFactory = None

def get_db_path() -> str:
    """Retrieves absolute path of the database file."""
    db_relative_path = config_manager.get("db_path", "tracker.db")
    # Resolve relative to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(project_root, db_relative_path)

def get_engine():
    """Returns the global database engine, initializing it if necessary."""
    global _engine
    if _engine is None:
        db_path = get_db_path()
        logger.info(f"Initializing database engine at: {db_path}")
        _engine = create_engine(f"sqlite:///{db_path}", echo=False)
    return _engine

def init_db():
    """Initializes the database and creates tables if they do not exist."""
    engine = get_engine()
    try:
        # Create all tables defined in Base
        Base.metadata.create_all(engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")
        raise

def get_session_factory():
    """Returns the global SessionFactory, initializing it if necessary."""
    global _SessionFactory
    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = sessionmaker(bind=engine)
    return _SessionFactory

@contextmanager
def get_db_session():
    """Context manager for SQLAlchemy database sessions."""
    init_db()  # Ensures tables exist before opening session
    factory = get_session_factory()
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction error: {e}")
        raise
    finally:
        session.close()
