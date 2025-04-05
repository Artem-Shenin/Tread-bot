from aiogram import types
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher

# Глобальный словарь для хранения тредов
threads = {}

async def is_admin(message: types.Message, bot: Bot) -> bool:
    chat_id = message.chat.id
    user_id = message.from_user.id
    admins = await bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in admins)

async def cmd_start(message: types.Message, bot: Bot):
    if not await is_admin(message, bot):
        await message.reply("Эта команда только для администратора.")
        return

    chat = message.chat
    admins = await bot.get_chat_administrators(chat.id)
    
    # Формирование информации
    chat_data = f"📋 Информация о чате:\n"
    chat_data += f"ID чата: {chat.id}\n"
    chat_data += f"Тип чата: {'Супергруппа' if chat.type == 'supergroup' else 'Не супергруппа'}\n"
    
    admins_info = "\n👥 Администраторы:\n"
    for admin in admins:
        admins_info += f"- {admin.user.id} | {admin.user.full_name}\n"

    threads_info = "\n🧵 Треды:\n"
    for thread_id, thread_name in threads.items():
        threads_info += f"- {thread_id} | {thread_name}\n"

    await message.answer(chat_data + admins_info + threads_info)
    
    # Вывод в консоль
    print("📋 Информация о чате:")
    print(f"ID чата: {chat.id}")
    print(f"Тип чата: {'Супергруппа' if chat.type == 'supergroup' else 'Не супергруппа'}")
    print("\n👥 Администраторы:")
    for admin in admins:
        print(f"- {admin.user.id} | {admin.user.full_name}")
    print("\n🧵 Треды:")
    for thread_id, thread_name in threads.items():
        print(f"- {thread_id} | {thread_name}")

async def cmd_set_announcement(message: types.Message, bot: Bot):
    if not await is_admin(message, bot):
        await message.reply("Эта команда только для администратора.")
        return

    if message.message_thread_id:
        threads[message.message_thread_id] = "объявления"
        await message.reply("Этот тред установлен как 'объявления'.")
    else:
        await message.reply("Эта команда должна быть использована в треде.")

async def cmd_set_discussion(message: types.Message, bot: Bot):
    if not await is_admin(message, bot):
        await message.reply("Эта команда только для администратора.")
        return

    if message.message_thread_id:
        threads[message.message_thread_id] = "обсуждение"
        await message.reply("Этот тред установлен как 'обсуждение'.")
    else:
        await message.reply("Эта команда должна быть использована в треде.")

async def handle_message(message: types.Message):
    """Сохранение тредов при получении сообщений"""
    if message.message_thread_id and message.message_thread_id not in threads:
        threads[message.message_thread_id] = "неизвестный"

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_set_announcement, Command("set_announcement"))
    dp.message.register(cmd_set_discussion, Command("set_discussion"))
    dp.message.register(handle_message)