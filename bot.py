import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN
from operators import simulate
from db import init_db
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from cors import *

bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher(storage=MemoryStorage())


class RegisterState(StatesGroup):
    waiting_for_credentials = State()


class SimulateState(StatesGroup):
    waiting_for_qubit_number = State()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Добро пожаловать! Отправьте /register для регистрации или /simulate для запуска симуляции. "
        "Команда /history для посмотра истории запросов")


@dp.message(Command("register"))
async def register(message: types.Message, state: FSMContext):
    await message.answer("Введите логин и пароль через пробел (пример: user123 password123)")
    await state.set_state(RegisterState.waiting_for_credentials)


@dp.message(RegisterState.waiting_for_credentials)
async def process_registration(message: types.Message, state: FSMContext):
    try:
        login, password = message.text.strip().split()
        if await user_exists_by_telegram_id(message.from_user.id):
            await message.answer("Пользователь уже зарегистрирован.")
        elif await user_exists_by_login(login):
            await message.answer("Пользователь с таким логином уже существует.")
        else:
            await create_user(login, password, message.from_user.id)
            await message.answer("Регистрация прошла успешно!")
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат. Введите логин и пароль через пробел.")


@dp.message(Command("simulate"))
async def handle_simulate_command(message: types.Message, state: FSMContext):
    await message.answer("Введите число кубитов от 1 до 10")
    await state.set_state(SimulateState.waiting_for_qubit_number)


@dp.message(SimulateState.waiting_for_qubit_number)
async def run_simulation(message: types.Message, state: FSMContext):
    try:
        n = int(message.text)
        if n <= 0 or n > 10:
            await message.answer("Введите целое число от 1 до 10.")
            return
        result = await simulate(n)
        result_bin = bin(result)[2:].zfill(2 ** n)
        await message.answer(f"Результат измерения: {result_bin}")

        user = await get_user_by_telegram_id(message.from_user.id)
        if user:
            await save_simulation_result(user.id, f"Результат симуляции для {n} кубитов: {result_bin}")

        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, отправьте целое число.")


@dp.message(Command("history"))
async def history(message: types.Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Вы не зарегистрированы.")
        return

    requests = await get_user_requests(user.id)
    history_text = "\n".join(f"{r.timestamp}: {r.content}" for r in requests)
    await message.answer(history_text or "У вас пока нет запросов.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    async def startup():
        await init_db()
        await dp.start_polling(bot)


    asyncio.run(startup())
