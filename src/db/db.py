from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from utils.database import build_database_url
from app.config import settings
from app.logging_config import get_logger

logger = get_logger()


# Initialize database engine and session factory
def setup_database():
    db_url = build_database_url()
    
    # Mask password in connection log
    safe_url = db_url.split('@')[1] if '@' in db_url else 'unknown'
    logger.info("Connecting to database: %s", safe_url)

    # Configure database engine
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": 3600,
        "future": True,
    }

    if settings.is_development():
        engine_kwargs["echo"] = settings.DEBUG

    db_engine = create_engine(db_url, **engine_kwargs)
    session_local = sessionmaker(
        bind=db_engine,
        autoflush=False,
        autocommit=False,
        future=True
    )

    logger.info("Database engine configured (pool_size=%s, max_overflow=%s)", settings.DB_POOL_SIZE, settings.DB_MAX_OVERFLOW)
    return session_local, db_engine


# Initialize database session at application startup
SessionLocal, engine = setup_database()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
