from sqlalchemy import select
from models import User, Request
from db import async_session_maker
from utils import hash_password

async def user_exists_by_telegram_id(telegram_id: int):
    async with async_session_maker() as session:
        return await session.scalar(select(User).where(User.telegram_id == telegram_id))

async def user_exists_by_login(login: str):
    async with async_session_maker() as session:
        return await session.scalar(select(User).where(User.username == login))

async def create_user(login: str, password: str, telegram_id: int):
    password_hashed = await hash_password(password)
    async with async_session_maker() as session:
        user = User(username=login, password_hash=password_hashed, telegram_id=telegram_id)
        session.add(user)
        await session.commit()

async def get_user_by_telegram_id(telegram_id: int):
    async with async_session_maker() as session:
        return await session.scalar(select(User).where(User.telegram_id == telegram_id))

async def save_simulation_result(user_id: int, content: str):
    async with async_session_maker() as session:
        request = Request(user_id=user_id, content=content)
        session.add(request)
        await session.commit()

async def get_user_requests(user_id: int):
    async with async_session_maker() as session:
        return await session.scalars(select(Request).where(Request.user_id == user_id).order_by(Request.timestamp.desc()))
