import numpy as np
import aiogram

# Создаю матрицу оператора Адамара (Hadamard gate)
# Вход: ничего
# Выход: матрица 2x2 типа np.ndarray
async def h() -> np.ndarray:
    return np.array([[1, 1], [1, -1]]) / np.sqrt(2)


# Применяю цепочку квантовых операторов к вектору состояния
# Вход: вектор состояния v и произвольное число квантовых операторов (матриц)
# Выход: новый вектор состояния после применения всех операторов
async def apply(v: np.ndarray, *gates: np.ndarray) -> np.ndarray:
    m: np.ndarray = gates[0]
    gates: tuple[np.ndarray, ...] = gates[1:]
    for gate in gates:
        m = np.kron(gate, m)
    return m.dot(v)


# Выполняю измерение (наблюдение) вектора состояния
# Вход: квантовый вектор состояния v
# Выход: целое число — результат наблюдения (индекс состояния)
async def observe(v: np.ndarray) -> int:
    v2: np.ndarray = np.absolute(v) ** 2
    c: np.ndarray = np.random.choice(v.size, 1, p=v2)
    return int(c[0])


# Провожу квантовую симуляцию с n кубитами: создаю начальное состояние,
# применяю оператор Адамара к каждому кубиту и наблюдаю результат
# Вход: количество кубитов n
# Выход: результат наблюдения в виде целого числа
async def simulate(n: int) -> int:
    state: np.ndarray = np.zeros(2 ** n)
    state[0] = 1  # Создаём начальное состояние
    hadamard_gates = [await h() for _ in range(n)]
    state = await apply(state, *hadamard_gates) # Применяем оператор Адамара ко всем кубитам
    return await observe(state)

