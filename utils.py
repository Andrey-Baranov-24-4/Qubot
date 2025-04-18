import bcrypt
import asyncio


# Хеширую пароль с использованием алгоритма bcrypt (в отдельном потоке, чтобы не блокировать event loop)
# Вход: строка с паролем
# Выход: строку с хешем пароля
async def hash_password(password: str) -> str:
    return await asyncio.to_thread(
        lambda: bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    )
