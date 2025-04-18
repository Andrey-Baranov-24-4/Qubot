from typing import Optional, Sequence
from sqlalchemy import select
from models import User, Request
from db import async_session_maker
from utils import hash_password


# Проверяю, существует ли пользователь с таким Telegram ID
# Вход: целое число, Telegram ID пользователя (telegram_id: int)
# Выход: объект User, если найден, иначе None (Optional[User])
async def user_exists_by_telegram_id(telegram_id: int) -> Optional[User]:
    async with async_session_maker() as session:
        return await session.scalar(select(User).where(User.telegram_id == telegram_id))


# Проверяю, существует ли пользователь с таким логином
# Вход: строка, логин пользователя (login: str)
# Выход: объект User, если найден, иначе None (Optional[User])
async def user_exists_by_login(login: str) -> Optional[User]:
    async with async_session_maker() as session:
        return await session.scalar(select(User).where(User.username == login))


# Создаю нового пользователя с логином, паролем и Telegram ID
# Вход: логин (str), пароль (str), Telegram ID (int)
# Выход: ничего не возвращаю (None), но создаю запись в БД
async def create_user(login: str, password: str, telegram_id: int) -> None:
    password_hashed: str = await hash_password(password)
    async with async_session_maker() as session:
        user: User = User(username=login, password_hash=password_hashed, telegram_id=telegram_id)
        session.add(user)
        await session.commit()


# Получаю пользователя по Telegram ID
# Вход: telegram ID (int)
# Выход: объект User, если найден, иначе None (Optional[User])
async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    async with async_session_maker() as session:
        return await session.scalar(select(User).where(User.telegram_id == telegram_id))


# Сохраняю результат симуляции в таблицу запросов
# Вход: ID пользователя (int), текст результата (str)
# Выход: ничего не возвращаю (None), но создаю запись в БД
async def save_simulation_result(user_id: int, content: str) -> None:
    async with async_session_maker() as session:
        request: Request = Request(user_id=user_id, content=content)
        session.add(request)
        await session.commit()


# Получаю список запросов пользователя, отсортированный по дате (сначала новые)
# Вход: ID пользователя (int)
# Выход: список объектов Request (Sequence[Request])
async def get_user_requests(user_id: int) -> Sequence[Request]:
    async with async_session_maker() as session:
        result = await session.scalars(
            select(Request).where(Request.user_id == user_id).order_by(Request.timestamp.desc())
        )
        return result.all()
