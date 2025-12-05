from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from settings import settings
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String
from typing import Annotated

engine = create_async_engine(settings.DATABASE_ASYNC_URL, echo=True)

async_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    """ Dependency for getting async session """
    try:
        session: AsyncSession = async_session_factory()
        yield session
    finally:
        await session.close()    

class Base(DeclarativeBase):
    pass
