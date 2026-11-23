import os
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from random import choice
from typing import Generator, List, Tuple

from core.tasks import CHARS, password_generator


@dataclass
class BenchmarkResult:
    total_count: int
    workers: int
    sequential_time: float
    parallel_time: float
    speedup: float
    sample_passwords: List[str]


def _generate_chunk(args: Tuple[int, int, str]) -> List[str]:
    """Генерирует порцию паролей в отдельном процессе."""
    count, length, chars = args
    return ["".join(choice(chars) for _ in range(length)) for _ in range(count)]


def parallel_password_generator(
    total_count: int,
    length: int = 12,
    workers: int | None = None,
    chunk_size: int = 10_000,
) -> Generator[str, None, None]:
    """Параллельная версия генератора паролей с использованием пула процессов."""
    if total_count <= 0:
        raise ValueError("Количество паролей должно быть больше 0.")
    if length <= 0:
        raise ValueError("Длина пароля должна быть больше 0.")
    if chunk_size <= 0:
        raise ValueError("Размер чанка должен быть больше 0.")

    max_workers = workers or max(1, os.cpu_count() or 2)
    if max_workers <= 0:
        raise ValueError("Количество процессов должно быть больше 0.")

    chunks: List[Tuple[int, int, str]] = []
    remaining = total_count
    while remaining > 0:
        current = min(chunk_size, remaining)
        chunks.append((current, length, CHARS))
        remaining -= current

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for batch in executor.map(_generate_chunk, chunks):
            yield from batch


def run_benchmark(
    total_count: int = 200_000,
    length: int = 12,
    workers: int | None = None,
) -> BenchmarkResult:
    """Сравнивает производительность последовательного и параллельного генераторов."""
    if total_count <= 0:
        raise ValueError("Количество паролей для бенчмарка должно быть больше 0.")

    used_workers = workers or max(2, os.cpu_count() or 2)

    # 1. Последовательная версия
    start_seq = time.perf_counter()
    seq_gen = password_generator(length=length)
    seq_result = [next(seq_gen) for _ in range(total_count)]
    seq_time = time.perf_counter() - start_seq

    # 2. Параллельная версия
    chunk_size = max(5_000, total_count // (used_workers * 4))
    start_par = time.perf_counter()
    par_result = list(
        parallel_password_generator(
            total_count=total_count,
            length=length,
            workers=used_workers,
            chunk_size=chunk_size,
        )
    )
    par_time = time.perf_counter() - start_par

    speedup = seq_time / par_time if par_time > 0 else 0.0

    return BenchmarkResult(
        total_count=total_count,
        workers=used_workers,
        sequential_time=seq_time,
        parallel_time=par_time,
        speedup=speedup,
        sample_passwords=par_result[:5],
    )