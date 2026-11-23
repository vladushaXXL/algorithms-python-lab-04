from random import choice
from string import ascii_lowercase, ascii_uppercase
from typing import Generator, Iterator, List

CHARS = ascii_lowercase + ascii_uppercase + "0123456789!?@#$*"


# --- Задача 1 ---
def abs_range_generator(a: int, b: int) -> Generator[int, None, None]:
    """Генератор модулей целых чисел в диапазоне [a; b] (a < b)."""
    if not isinstance(a, int) or not isinstance(b, int) or isinstance(a, bool) or isinstance(b, bool):
        raise TypeError("Границы диапазона a и b должны быть целыми числами.")
    if a >= b:
        raise ValueError(f"Некорректный диапазон: требуется a < b (получено a={a}, b={b}).")

    return (abs(x) for x in range(a, b + 1))


def get_first_abs_values(a: int, b: int, limit: int = 4) -> List[int]:
    """Возвращает первые limit значений (или меньше, если диапазон короче)."""
    if limit < 0:
        raise ValueError("Параметр limit не может быть отрицательным.")

    gen = abs_range_generator(a, b)
    result: List[int] = []
    for _ in range(limit):
        try:
            result.append(next(gen))
        except StopIteration:
            break
    return result


# --- Задача 2 ---
def password_generator(length: int = 12, chars: str = CHARS) -> Generator[str, None, None]:
    """Бесконечная функция-генератор случайных паролей заданной длины."""
    if not isinstance(length, int) or isinstance(length, bool) or length <= 0:
        raise ValueError("Длина пароля должна быть положительным целым числом.")
    if not chars:
        raise ValueError("Строка допустимых символов не может быть пустой.")

    while True:
        yield "".join(choice(chars) for _ in range(length))


def get_passwords(count: int = 5, length: int = 12) -> List[str]:
    """Извлекает указанное количество паролей из генератора."""
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ValueError("Количество паролей должно быть неотрицательным целым числом.")

    gen = password_generator(length=length)
    return [next(gen) for _ in range(count)]


# --- Задача 3 ---
def parse_int_list(raw_text: str) -> List[int]:
    """Парсит строку с целыми числами через пробел в список int."""
    if not isinstance(raw_text, str):
        raise TypeError("Ожидалась строка с числами.")

    tokens = raw_text.strip().split()
    if not tokens:
        raise ValueError("Список чисел не может быть пустым.")

    try:
        return [int(token) for token in tokens]
    except ValueError as exc:
        raise ValueError("Все элементы должны быть целыми числами.") from exc


def pairwise_multiply_iterator(list1: List[int], list2: List[int]) -> Iterator[int]:
    """Возвращает итератор попарных произведений через zip и map."""
    if not isinstance(list1, list) or not isinstance(list2, list):
        raise TypeError("Входные аргументы должны быть списками.")
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in list1 + list2):
        raise TypeError("Списки должны содержать только целые числа.")

    return map(lambda pair: pair[0] * pair[1], zip(list1, list2))


def get_first_three_products(list1: List[int], list2: List[int], count: int = 3) -> List[int]:
    """Извлекает первые count (по умолчанию 3) произведения через next()."""
    if count < 0:
        raise ValueError("Количество извлекаемых элементов не может быть отрицательным.")

    min_len = min(len(list1), len(list2))
    if min_len < count:
        raise ValueError(
            f"Недостаточно элементов для извлечения {count} значений "
            f"(минимальная длина списков: {min_len})."
        )

    iterator = pairwise_multiply_iterator(list1, list2)
    return [next(iterator) for _ in range(count)]