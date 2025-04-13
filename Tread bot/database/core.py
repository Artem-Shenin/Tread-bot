import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import inspect
from database.engine_core import engine
from database.models import Admin

async def create_tables():
    # Проверяем существование таблиц
    async with engine.begin() as conn:
        from database.engine_core import Base
        # Получаем инспектор для проверки существования таблиц
        inspector = await conn.run_sync(inspect)
        
        # Получаем список всех существующих таблиц
        existing_tables = await conn.run_sync(lambda sync_conn: inspector.get_table_names())
        
        # Проверяем, существуют ли все необходимые таблицы
        tables_to_create = False
        for table in Base.metadata.tables.keys():
            if table not in existing_tables:
                tables_to_create = True
                break
        
        # Создаем таблицы только если какая-то из них отсутствует
        if tables_to_create:
            print("Создание отсутствующих таблиц...")
            await conn.run_sync(Base.metadata.create_all)
        else:
            print("Все таблицы уже существуют, пропускаем создание")
           

if __name__ == "__main__":
    asyncio.run(create_tables())