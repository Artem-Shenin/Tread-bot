import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from .engine import engine  # Use relative import
from .models import metadata_obj, Admins

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(metadata_obj.create_all)
           

if __name__ == "__main__":
    asyncio.run(create_tables())
