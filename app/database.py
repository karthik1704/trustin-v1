from sqlalchemy import create_engine
from collections.abc import AsyncGenerator
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
# from app.config import settings as global_settings
from dotenv import load_dotenv
from .settings import Debug
import os
load_dotenv()

username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')



def get_database_url():
    print(Debug)
    if Debug:
        return f"postgresql+psycopg://postgres:postgres@localhost/trustin_fa"
    else:

        return f"postgresql+psycopg://{username}:{password}@{host}/{db_name}"



SQLALCHEMY_DATABASE_URL = get_database_url()


engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
print(engine)
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