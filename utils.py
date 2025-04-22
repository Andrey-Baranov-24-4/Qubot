import bcrypt
import asyncio


# Хеширую пароль с использованием алгоритма bcrypt
# Вход: строка с паролем
# Выход: строку с хешем пароля
async def hash_password(password: str) -> str:
    return await asyncio.to_thread(
        lambda: bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    )
