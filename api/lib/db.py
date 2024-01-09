import contextlib
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from api.settings import settings


db_url = f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}/{settings.db_name}"
engine = create_async_engine(db_url, future=True, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@contextlib.asynccontextmanager
async def obtain_session():
    session = async_session()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db():
    async with obtain_session() as session:
        yield session


DependsDB = Annotated[AsyncSession, Depends(get_db)]
