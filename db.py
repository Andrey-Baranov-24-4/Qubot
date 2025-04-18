from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models import *
from config import DATABASE_URL

# Подключаем базу данных
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Запускаем генерацию таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
