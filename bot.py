import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from db import init_db
from handlers import register_handlers

# Инициализация бота и диспетчера
bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher(storage=MemoryStorage())


# Основная функция запуска бота
async def main() -> None:
    register_handlers(dp)  # Регистрация всех хендлеров
    await init_db()  # Инициализация базы данных
    await dp.start_polling(bot)  # Запуск бота


if __name__ == "__main__":
    asyncio.run(main())
