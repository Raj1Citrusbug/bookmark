# Standard library imports
from functools import lru_cache

# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeBase
from tenacity import RetryError, retry, stop_after_attempt, wait_fixed

# Local application imports
from app.config.settings import app_settings
from app.config.logger import logger

Base: type[DeclarativeBase] = declarative_base()

ASYNC_DATABASE_URL = f"postgresql+asyncpg://{app_settings.DB_USERNAME}:{app_settings.DB_PASSWORD}@{app_settings.DB_HOST}:{app_settings.DB_PORT}/{app_settings.DB_NAME}"


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def create_engine_with_retry():
    """
    Creates a SQLAlchemy async engine with the given database connection
    settings, and retries up to 3 times with a 5 second wait
    between retries if the connection fails.

    Returns:
        sqlalchemy.ext.asyncio.AsyncEngine: The created async engine.
    """
    return create_async_engine(
        url=ASYNC_DATABASE_URL,
        echo=app_settings.DB_ECHO,
        pool_size=app_settings.DATABASE_POOL_SIZE,
        max_overflow=app_settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=app_settings.DATABASE_POOL_TIMEOUT,
        pool_recycle=app_settings.DATABASE_POOL_RECYCLE,
        future=True,
    )


@lru_cache()
def get_async_engine():
    """
    Gets a SQLAlchemy async engine with the given database connection
    settings, and retries up to 3 times with a 5 second wait
    between retries if the connection fails.

    Returns:
        sqlalchemy.ext.asyncio.AsyncEngine: The created async engine.
    Raises:
        RetryError: If the database connection fails after retries.
    """
    try:
        return create_engine_with_retry()
    except RetryError as e:
        logger.error("Database connection failed after retries.")
        raise e


AsyncSessionLocal = sessionmaker(
    bind=get_async_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=app_settings.DB_AUTOFLUSH,
    autocommit=app_settings.DB_AUTOCOMMIT,
)


async def get_async_db() -> AsyncSession:
    """
    Asynchronous context manager that yields an AsyncSession object.

    This function is intended to be used as an asynchronous context manager.
    It will yield an AsyncSession object that can be used to interact with the database.
    The session will automatically be committed if no exceptions occur, and rolled back if an exception does occur.
    The session will also be closed when the context manager is exited.

    Yields:
        AsyncSession: An AsyncSession object that can be used to interact with the database.
    Raises:
        Exception: If an exception occurs while using the session, it will be logged and re-raised.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
