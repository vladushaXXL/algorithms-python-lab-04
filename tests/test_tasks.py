import pytest

from core.parallel_gen import parallel_password_generator, run_benchmark
from core.tasks import (
    CHARS,
    abs_range_generator,
    get_first_abs_values,
    get_first_three_products,
    get_passwords,
    pairwise_multiply_iterator,
    parse_int_list,
    password_generator,
)


# --- Тесты Задачи 1 ---
def test_abs_range_standard():
    assert get_first_abs_values(-5, 5) == [5, 4, 3, 2]


def test_abs_range_shorter_than_four():
    # Диапазон [-1; 0] содержит всего 2 числа
    assert get_first_abs_values(-1, 0) == [1, 0]


def test_abs_range_invalid_bounds():
    with pytest.raises(ValueError):
        list(abs_range_generator(5, 5))
    with pytest.raises(ValueError):
        list(abs_range_generator(10, 2))


def test_abs_range_invalid_types():
    with pytest.raises(TypeError):
        abs_range_generator("1", 5)  # type: ignore
    with pytest.raises(TypeError):
        abs_range_generator(True, 5)


# --- Тесты Задачи 2 ---
def test_password_generator_format():
    passwords = get_passwords(count=5, length=12)
    assert len(passwords) == 5
    for pwd in passwords:
        assert len(pwd) == 12
        assert all(ch in CHARS for ch in pwd)


def test_password_generator_is_infinite():
    gen = password_generator(length=12)
    generated = [next(gen) for _ in range(100)]
    assert len(generated) == 100


def test_password_generator_invalid_args():
    with pytest.raises(ValueError):
        next(password_generator(length=0))
    with pytest.raises(ValueError):
        next(password_generator(length=12, chars=""))
    with pytest.raises(ValueError):
        get_passwords(count=-1)


# --- Тесты Задачи 3 ---
def test_parse_int_list_valid():
    assert parse_int_list("1 -2 3 40") == [1, -2, 3, 40]


def test_parse_int_list_invalid():
    with pytest.raises(ValueError):
        parse_int_list("")
    with pytest.raises(ValueError):
        parse_int_list("1 2 abc")


def test_pairwise_multiply_first_three():
    result = get_first_three_products([2, 4, 6, 8], [3, 5, 7, 9])
    assert result == [6, 20, 42]


def test_pairwise_multiply_not_enough_elements():
    with pytest.raises(ValueError):
        get_first_three_products([1, 2], [3, 4, 5])


def test_pairwise_multiply_invalid_types():
    with pytest.raises(TypeError):
        pairwise_multiply_iterator([1, "2", 3], [4, 5, 6])  # type: ignore


# --- Тесты параллельного генератора (Well-done) ---
def test_parallel_password_generator():
    passwords = list(parallel_password_generator(total_count=100, length=12, workers=2, chunk_size=25))
    assert len(passwords) == 100
    assert all(len(p) == 12 and all(c in CHARS for c in p) for p in passwords)


def test_parallel_generator_invalid_args():
    with pytest.raises(ValueError):
        list(parallel_password_generator(total_count=0))
    with pytest.raises(ValueError):
        list(parallel_password_generator(total_count=10, length=0))


def test_benchmark_execution():
    res = run_benchmark(total_count=10_000, workers=2)
    assert res.total_count == 10_000
    assert res.sequential_time > 0
    assert res.parallel_time > 0
    assert len(res.sample_passwords) == 5