# handlers.py
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Dispatcher
from db_utils import *
from operators import simulate


# Класс состояния регистрации
class RegisterState(StatesGroup):
    waiting_for_credentials: State = State()


# Класс состояния симуляции
class SimulateState(StatesGroup):
    waiting_for_qubit_number: State = State()


def register_handlers(dp: Dispatcher) -> None:
    # Обработчик команды /start
    # Вход: сообщение от пользователя
    # Выход: отправка приветственного текста
    @dp.message(Command("start"))
    async def start(message: types.Message) -> None:
        await message.answer(
            "Добро пожаловать! Отправьте /register для регистрации или /simulate для запуска симуляции. "
            "Команда /history для просмотра истории запросов"
        )

    # Обработчик команды /register
    # Вход: сообщение, контекст состояния
    # Выход: перевод в состояние ожидания логина и пароля
    @dp.message(Command("register"))
    async def register(message: types.Message, state: FSMContext) -> None:
        await message.answer("Введите логин и пароль через пробел (пример: user123 password123)")
        await state.set_state(RegisterState.waiting_for_credentials)

    # Обработка ввода логина и пароля
    # Вход: сообщение, состояние
    # Выход: регистрация пользователя, сообщение об успехе или ошибке
    @dp.message(RegisterState.waiting_for_credentials)
    async def process_registration(message: types.Message, state: FSMContext) -> None:
        try:
            login: str
            password: str
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

    # Обработчик команды /simulate
    # Вход: сообщение, состояние
    # Выход: перевод в состояние ожидания числа кубитов
    @dp.message(Command("simulate"))
    async def handle_simulate_command(message: types.Message, state: FSMContext) -> None:
        await message.answer("Введите число кубитов от 1 до 10")
        await state.set_state(SimulateState.waiting_for_qubit_number)

    # Обработка симуляции
    # Вход: сообщение с числом кубитов, состояние
    # Выход: результат симуляции и его сохранение
    @dp.message(SimulateState.waiting_for_qubit_number)
    async def run_simulation(message: types.Message, state: FSMContext) -> None:
        try:
            n: int = int(message.text)
            if n <= 0 or n > 10:
                await message.answer("Введите целое число от 1 до 10.")
                return

            result: int = await simulate(n)
            result_bin: str = bin(result)[2:].zfill(2 ** n)

            await message.answer(f"Результат измерения: {result_bin}")

            user = await get_user_by_telegram_id(message.from_user.id)
            if user:
                await save_simulation_result(user.id, f"Результат симуляции для {n} кубитов: {result_bin}")

            await state.clear()

        except ValueError:
            await message.answer("Пожалуйста, отправьте целое число.")

    # Обработчик команды /history
    # Вход: сообщение
    # Выход: история запросов пользователя
    @dp.message(Command("history"))
    async def history(message: types.Message) -> None:
        user = await get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("Вы не зарегистрированы.")
            return

        requests = await get_user_requests(user.id)
        history_text: str = "\n".join(f"{r.timestamp}: {r.content}" for r in requests)
        await message.answer(history_text or "У вас пока нет запросов.")
