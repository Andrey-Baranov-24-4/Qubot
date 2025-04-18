import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN
from operators import *
from db import async_session_maker
from models import User
from sqlalchemy import select
from db import init_db
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from models import Request

# Инициализирую бота и диспетчер Aiogram
bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher(storage=MemoryStorage())

class RegisterState(StatesGroup):
    waiting_for_credentials = State()

class SimulateState(StatesGroup):
    waiting_for_qubit_number = State()


# Отправляю стартовое сообщение пользователю
# Вход: объект сообщения от пользователя
# Выход: сообщение с инструкцией
@dp.message(Command("start"))
async def start(message: types.Message) -> None:
    await message.answer("Добро пожаловать! Отправьте /register для регистрации или /simulate для запуска симуляции. Команда /history для посмотра истории запросов")


# Регистрирую пользователя с логином и паролем
# Вход: сообщение с логином и паролем (через пробел)
# Выход: сообщение об успешной регистрации или ошибке
@dp.message(Command("register"))
async def register(message: types.Message, state: FSMContext) -> None:
    await message.answer("Введите логин и пароль через пробел (пример: user123 password123)")
    await state.set_state(RegisterState.waiting_for_credentials)

@dp.message(RegisterState.waiting_for_credentials)
async def process_registration(message: types.Message, state: FSMContext) -> None:
    try:
        login, password = message.text.strip().split()
        async with async_session_maker() as session:
            # Проверка, существует ли уже пользователь с таким telegram_id
            user_exists = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
            if user_exists:
                await message.answer("Регистрация не требуется. Пользователь уже зарегистрирован.")
                await state.clear()
                return

            # Проверка на существование пользователя с таким логином
            login_exists = await session.scalar(select(User).where(User.username == login))
            if login_exists:
                await message.answer("Пользователь с таким логином уже существует.")
                await state.clear()
                return

            # Регистрация нового пользователя
            from utils import hash_password
            user = User(username=login, password_hash=hash_password(password), telegram_id=message.from_user.id)
            session.add(user)
            await session.commit()
            await message.answer("Регистрация прошла успешно!")
            await state.clear()
    except ValueError:
        await message.answer("Неверный формат. Введите логин и пароль через пробел.")




# Обрабатываю сообщение с числом кубитов от пользователя
# Вход: объект сообщения с текстом от пользователя
# Выход: сообщение с результатом измерения или сообщение об ошибке
@dp.message(Command("simulate"))
async def handle_simulate_command(message: types.Message, state: FSMContext):
    await message.answer("Введите число кубитов от 1 до 10")
    await state.set_state(SimulateState.waiting_for_qubit_number)


@dp.message(SimulateState.waiting_for_qubit_number)
async def run_simulation(message: types.Message, state: FSMContext) -> None:
    try:
        n: int = int(message.text)
        if n <= 0 or n > 10:
            await message.answer("Введите целое число от 1 до 10.")
            return
        result: int = simulate(n)
        result_bin = bin(result)[2:].zfill(2 ** n)

        await message.answer(f"Результат измерения: {result_bin}")
        await state.clear()

        # Сохраняем результат симуляции в таблицу
        async with async_session_maker() as session:
            user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
            if user:
                request = Request(
                    user_id=user.id,
                    content=f"Результат симуляции для {n} кубитов: {result_bin}"  # Сохраняем результат
                )
                session.add(request)
                await session.commit()

    except ValueError:
        await message.answer("Пожалуйста, отправьте целое число.")

@dp.message(Command("history"))
async def history(message: types.Message) -> None:
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
        if not user:
            await message.answer("Вы не зарегистрированы.")
            return

        requests = await session.scalars(select(Request).where(Request.user_id == user.id).order_by(Request.timestamp.desc()))
        history_text = "\n".join(f"{r.timestamp}: {r.content}" for r in requests)
        await message.answer(history_text or "У вас пока нет запросов.")



# Запускаю бота и начинаю слушать входящие сообщения
# Вход: ничего
# Выход: запуск процесса polling
async def main() -> None:
    await dp.start_polling(bot)


# Точка входа в программу
# Запускаю асинхронную функцию main
if __name__ == "__main__":
    async def startup():
        await init_db()  # создаём таблицы
        await dp.start_polling(bot)  # запускаем бота

    asyncio.run(startup())