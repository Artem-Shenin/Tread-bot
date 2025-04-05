import asyncio
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers import register_handlers
from database.core import create_tables
#sys.path.insert(1, os.path.join(sys.path[0], '..'))

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Регистрация хендлеров
register_handlers(dp)

async def main():
    await create_tables()  # Create tables first
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())  # Call the function with parentheses
