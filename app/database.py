import contextlib
from typing import AsyncIterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from dotenv import load_dotenv
from .settings import Debug
load_dotenv()
import os

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


class DatabaseSessionManager:
    def __init__(self, host: str):
        self._engine = create_async_engine(host)
        self._sessionmaker = async_sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(SQLALCHEMY_DATABASE_URL)





async def get_db():
    async with sessionmanager.session() as session:
        yield session
