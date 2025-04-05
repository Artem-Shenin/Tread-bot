from sqlalchemy.ext.asyncio import create_async_engine,  AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
import os

from dotenv import load_dotenv
import asyncio
load_dotenv()

engine = create_async_engine(
    url=os.getenv("DB_URL"),
    echo=True,  # Set to True for detailed logging
    pool_size=3,
    max_overflow=5)


class Base(DeclarativeBase):
    pass

session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,  
    autoflush=False
    )
async def get_version():
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            return result.scalar()

if __name__ == "__main__":
    asyncio.run(get_version())