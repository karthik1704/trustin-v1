from sqlalchemy import create_engine
from collections.abc import AsyncGenerator
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
# from app.config import settings as global_settings

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost/trustin_fa"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

engine = create_async_engine(
    # global_settings.asyncpg_url.unicode_string(),
    SQLALCHEMY_DATABASE_URL,
    future=True,
    echo=True,
)

# expire_on_commit=False will prevent attributes from being expired
# after commit.
AsyncSessionFactory = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
)

# Dependency
async def get_async_db() -> AsyncGenerator:
    print("calling async db")
    async with AsyncSessionFactory() as session:
        # logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        print(session)
        yield session