from aiogram import types
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher
from database.queries import load_admins, get_or_create_group, add_or_update_thread, get_threads_for_group
from database.models import ThreadType

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
    
    # Сохраняем группу в базу данных
    try:
        await get_or_create_group(chat.id)
    except Exception as e:
        print(f"Ошибка при сохранении группы: {e}")
    
    # Получаем треды из базы данных
    db_threads = await get_threads_for_group(chat.id)
    
    # Формирование информации
    chat_data = f"📋 Информация о чате:\n"
    chat_data += f"ID чата: {chat.id}\n"
    chat_data += f"Тип чата: {'Супергруппа' if chat.type == 'supergroup' else 'Не супергруппа'}\n"
    
    admins_info = "\n👥 Администраторы:\n"
    for admin in admins:
        admins_info += f"- {admin.user.id} | {admin.user.full_name}\n"

    threads_info = "\n🧵 Треды из базы данных:\n"
    if db_threads:
        for thread in db_threads:
            threads_info += f"- {thread['thread_id']} | {thread['thread_type']}\n"
    else:
        threads_info += "Нет сохраненных тредов\n"

    await message.answer(chat_data + admins_info + threads_info)
    
    # Вывод в консоль
    print("📋 Информация о чате:")
    print(f"ID чата: {chat.id}")
    print(f"Тип чата: {'Супергруппа' if chat.type == 'supergroup' else 'Не супергруппа'}")
    print("\n👥 Администраторы:")
    for admin in admins:
        print(f"- {admin.user.id} | {admin.user.full_name}")
    print("\n🧵 Треды из базы данных:")
    if db_threads:
        for thread in db_threads:
            print(f"- {thread['thread_id']} | {thread['thread_type']}")
    else:
        print("Нет сохраненных тредов")
    
    # Сохраняем администраторов
    await load_admins(admins)
    
async def cmd_set_announcement(message: types.Message, bot: Bot):
    if not await is_admin(message, bot):
        await message.reply("Эта команда только для администратора.")
        return

    if message.message_thread_id:
        try:
            # Сохраняем тред в базу данных
            await add_or_update_thread(
                group_id=message.chat.id,
                thread_id=message.message_thread_id,
                thread_type=ThreadType.ANNOUNCEMENT.value
            )
            await message.reply("Этот тред установлен как 'объявления' и сохранен в базе данных.")
        except Exception as e:
            await message.reply(f"Ошибка при сохранении треда: {e}")
    else:
        await message.reply("Эта команда должна быть использована в треде.")

async def cmd_set_discussion(message: types.Message, bot: Bot):
    if not await is_admin(message, bot):
        await message.reply("Эта команда только для администратора.")
        return

    if message.message_thread_id:
        try:
            # Сохраняем тред в базу данных
            await add_or_update_thread(
                group_id=message.chat.id,
                thread_id=message.message_thread_id,
                thread_type=ThreadType.DISCUSSION.value
            )
            await message.reply("Этот тред установлен как 'обсуждение' и сохранен в базе данных.")
        except Exception as e:
            await message.reply(f"Ошибка при сохранении треда: {e}")
    else:
        await message.reply("Эта команда должна быть использована в треде.")

async def handle_message(message: types.Message):
    """Сохранение тредов при получении сообщений"""
    if message.message_thread_id:
        try:
            # Проверяем, существует ли тред в базе данных
            threads = await get_threads_for_group(message.chat.id)
            thread_exists = any(int(thread['thread_id']) == message.message_thread_id for thread in threads)
            
            # Если треда нет в базе, добавляем его как "неизвестный"
            if not thread_exists:
                await add_or_update_thread(
                    group_id=message.chat.id,
                    thread_id=message.message_thread_id,
                    thread_type=ThreadType.UNKNOWN.value
                )
        except Exception as e:
            print(f"Ошибка при обработке сообщения в треде {message.message_thread_id}: {e}")

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_set_announcement, Command("set_announcement"))
    dp.message.register(cmd_set_discussion, Command("set_discussion"))
    dp.message.register(handle_message)
