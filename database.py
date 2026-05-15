from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os
import logging

load_dotenv()

engine = create_async_engine(os.getenv("DATABASE_URL"))
session_local = async_sessionmaker(
    engine, autoflush=False, autocommit=False, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    db = session_local()
    try:
        yield db
    except Exception as e:
        logging.exception(e)
        raise
    finally:
        await db.close()
