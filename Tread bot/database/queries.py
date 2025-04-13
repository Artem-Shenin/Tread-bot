import asyncio
from sqlalchemy import BigInteger, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from .engine_core import engine, a_session
from .models import Admin, Group, Thread, ThreadType

async def load_admins(admins_list) -> None:
    """
    Сохраняет список администраторов в базу данных
    :param admins_list: список объектов ChatMemberAdministrator
    """
    async with a_session() as session:
        try:
            for admin in admins_list:
                # Получаем ID администратора из объекта
                admin_id = admin.user.id
                
                try:
                    # Проверяем, существует ли уже такой админ в базе
                    result = await session.execute(select(Admin).where(Admin.tg_id == str(admin_id)))
                    existing_admin = result.scalars().first()
                    
                    if not existing_admin:
                        # Используем строковое представление ID для избежания проблем с диапазоном
                        new_admin = Admin(tg_id=str(admin_id))
                        session.add(new_admin)
                except Exception as individual_error:
                    print(f"Ошибка при обработке администратора {admin_id}: {individual_error}")
                    continue
                    
            await session.commit()
            print(f"Успешно сохранены {len(admins_list)} администраторов")
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при сохранении администраторов: {e}")

async def get_or_create_group(group_id: int) -> Group:
    """
    Получает или создает группу в базе данных
    :param group_id: ID группы в Telegram
    :return: объект Group
    """
    str_group_id = str(group_id)  # Преобразуем в строку для хранения
    
    async with a_session() as session:
        try:
            # Проверяем, существует ли уже такая группа в базе
            result = await session.execute(select(Group).where(Group.tg_id == str_group_id))
            existing_group = result.scalars().first()
            
            if existing_group:
                return existing_group
            
            # Если группы нет, создаем новую
            new_group = Group(tg_id=str_group_id)
            session.add(new_group)
            await session.commit()
            await session.refresh(new_group)  # Обновляем объект, чтобы получить ID
            
            print(f"Создана новая группа с ID {new_group.id} (Telegram ID: {group_id})")
            return new_group
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при создании группы {group_id}: {e}")
            raise

async def add_or_update_thread(group_id: int, thread_id: int, thread_type: str) -> Thread:
    """
    Добавляет или обновляет тред в базе данных
    :param group_id: ID группы в Telegram
    :param thread_id: ID треда в Telegram
    :param thread_type: тип треда ("объявления" или "обсуждение")
    :return: объект Thread
    """
    str_thread_id = str(thread_id)  # Преобразуем в строку для хранения
    
    # Проверяем корректность типа треда
    if thread_type not in [t.value for t in ThreadType]:
        thread_type = ThreadType.UNKNOWN.value
    
    async with a_session() as session:
        try:
            # Получаем или создаем группу
            group = await get_or_create_group(group_id)
            
            # Проверяем, существует ли уже такой тред в базе
            result = await session.execute(
                select(Thread).where(
                    (Thread.thread_id == str_thread_id) & 
                    (Thread.group_id == group.id)
                )
            )
            existing_thread = result.scalars().first()
            
            if existing_thread:
                # Если тред существует, обновляем его тип
                existing_thread.thread_type = thread_type
                await session.commit()
                print(f"Обновлен тред {thread_id} в группе {group_id}, тип: {thread_type}")
                return existing_thread
            
            # Если треда нет, создаем новый
            new_thread = Thread(
                thread_id=str_thread_id,
                thread_type=thread_type,
                group_id=group.id
            )
            session.add(new_thread)
            await session.commit()
            await session.refresh(new_thread)  # Обновляем объект, чтобы получить ID
            
            print(f"Создан новый тред с ID {new_thread.id} (Telegram ID: {thread_id}) в группе {group_id}, тип: {thread_type}")
            return new_thread
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при создании/обновлении треда {thread_id} в группе {group_id}: {e}")
            raise

async def get_threads_for_group(group_id: int) -> list[dict]:
    """
    Получает список тредов для указанной группы
    :param group_id: ID группы в Telegram
    :return: список словарей с информацией о тредах
    """
    str_group_id = str(group_id)
    
    async with a_session() as session:
        try:
            # Сначала находим группу
            group_result = await session.execute(select(Group).where(Group.tg_id == str_group_id))
            group = group_result.scalars().first()
            
            if not group:
                return []
            
            # Затем получаем все треды для этой группы
            threads_result = await session.execute(
                select(Thread).where(Thread.group_id == group.id)
            )
            threads = threads_result.scalars().all()
            
            # Преобразуем в список словарей для удобства использования
            return [
                {
                    "id": thread.id,
                    "thread_id": thread.thread_id,
                    "thread_type": thread.thread_type
                }
                for thread in threads
            ]
        except Exception as e:
            print(f"Ошибка при получении тредов для группы {group_id}: {e}")
            return []
