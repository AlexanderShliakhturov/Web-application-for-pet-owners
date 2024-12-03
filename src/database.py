import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import URL, create_engine, text
from src.config import settings


sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=False
)

session_factory = sessionmaker(sync_engine)

class Base(DeclarativeBase):
    pass
    repr_cols_num = 3
    repr_cols = tuple() 

    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"



async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True
)

async_session_factory = async_sessionmaker(async_engine)







    