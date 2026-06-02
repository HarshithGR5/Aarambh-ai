from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
from .config import settings
import logging

logger = logging.getLogger(__name__)

# echo=False — suppresses duplicate SQL logs from SQLAlchemy's internal handler.
# The root logger in main.py already handles all app-level logging.
# To enable SQL query debugging: logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
