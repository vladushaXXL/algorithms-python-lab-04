import os
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.parallel_gen import BenchmarkResult, run_benchmark
from core.tasks import (
    get_first_abs_values,
    get_first_three_products,
    get_passwords,
    parse_int_list,
)


class BenchmarkWorker(QThread):
    finished_signal = Signal(object)
    error_signal = Signal(str)

    def __init__(self, total_count: int, workers: int):
        super().__init__()
        self.total_count = total_count
        self.workers = workers

    def run(self):
        try:
            result = run_benchmark(total_count=self.total_count, workers=self.workers)
            self.finished_signal.emit(result)
        except Exception as exc:
            self.error_signal.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа №4 — Вариант 13 (Well-done)")
        self.resize(650, 460)
        self._worker: BenchmarkWorker | None = None

        tabs = QTabWidget()
        tabs.addTab(self._create_task1_tab(), "Задача 1: Модули")
        tabs.addTab(self._create_task2_tab(), "Задача 2: Пароли")
        tabs.addTab(self._create_task3_tab(), "Задача 3: zip + map")
        tabs.addTab(self._create_benchmark_tab(), "Well-done: Бенчмарк")
        self.setCentralWidget(tabs)

    # --- Вкладка 1 ---
    def _create_task1_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        desc = QLabel(
            "Генератор модулей целых чисел в диапазоне [a; b] (a < b).\n"
            "Выводит первые 4 значения (или меньше, если диапазон короче)."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        form = QFormLayout()
        self.input_a = QLineEdit("-5")
        self.input_b = QLineEdit("5")
        form.addRow("Число a:", self.input_a)
        form.addRow("Число b:", self.input_b)
        layout.addLayout(form)

        btn = QPushButton("Сгенерировать")
        btn.clicked.connect(self._run_task1)
        layout.addWidget(btn)

        self.output_task1 = QTextEdit()
        self.output_task1.setReadOnly(True)
        layout.addWidget(self.output_task1)
        return widget

    def _run_task1(self):
        try:
            a = int(self.input_a.text().strip())
            b = int(self.input_b.text().strip())
            values = get_first_abs_values(a, b, limit=4)
            self.output_task1.setPlainText(
                f"Диапазон: [{a}; {b}]\n"
                f"Первые значения модулей (до 4 шт.): {values}"
            )
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка ввода", str(exc))

    # --- Вкладка 2 ---
    def _create_task2_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        desc = QLabel(
            "Бесконечная функция-генератор случайных паролей длиной 12 символов.\n"
            "По умолчанию выводится 5 паролей."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        form = QFormLayout()
        self.spin_pwd_count = QSpinBox()
        self.spin_pwd_count.setRange(1, 100)
        self.spin_pwd_count.setValue(5)
        form.addRow("Количество паролей:", self.spin_pwd_count)
        layout.addLayout(form)

        btn = QPushButton("Сгенерировать пароли")
        btn.clicked.connect(self._run_task2)
        layout.addWidget(btn)

        self.output_task2 = QTextEdit()
        self.output_task2.setReadOnly(True)
        layout.addWidget(self.output_task2)
        return widget

    def _run_task2(self):
        try:
            count = self.spin_pwd_count.value()
            passwords = get_passwords(count=count, length=12)
            lines = [f"{i}. {pwd}" for i, pwd in enumerate(passwords, start=1)]
            self.output_task2.setPlainText("\n".join(lines))
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))

    # --- Вкладка 3 ---
    def _create_task3_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        desc = QLabel(
            "Попарное перемножение двух списков целых чисел через zip и map.\n"
            "Извлекает первые 3 значения с помощью next()."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        form = QFormLayout()
        self.input_list1 = QLineEdit("2 4 6 8 10")
        self.input_list2 = QLineEdit("3 5 7 9 11")
        form.addRow("Список 1 (через пробел):", self.input_list1)
        form.addRow("Список 2 (через пробел):", self.input_list2)
        layout.addLayout(form)

        btn = QPushButton("Вычислить первые 3 произведения")
        btn.clicked.connect(self._run_task3)
        layout.addWidget(btn)

        self.output_task3 = QTextEdit()
        self.output_task3.setReadOnly(True)
        layout.addWidget(self.output_task3)
        return widget

    def _run_task3(self):
        try:
            list1 = parse_int_list(self.input_list1.text())
            list2 = parse_int_list(self.input_list2.text())
            products = get_first_three_products(list1, list2, count=3)
            self.output_task3.setPlainText(
                f"Список 1: {list1}\n"
                f"Список 2: {list2}\n"
                f"Первые 3 произведения (через next): {products}"
            )
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка ввода", str(exc))

    # --- Вкладка 4: Бенчмарк ---
    def _create_benchmark_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        desc = QLabel(
            "Сравнение производительности последовательного и параллельного "
            "(ProcessPoolExecutor) генераторов паролей."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        form = QFormLayout()
        self.spin_bench_count = QSpinBox()
        self.spin_bench_count.setRange(50_000, 2_000_000)
        self.spin_bench_count.setSingleStep(50_000)
        self.spin_bench_count.setValue(300_000)

        self.spin_workers = QSpinBox()
        cpu_count = os.cpu_count() or 4
        self.spin_workers.setRange(1, max(16, cpu_count))
        self.spin_workers.setValue(cpu_count)

        form.addRow("Количество паролей:", self.spin_bench_count)
        form.addRow("Число процессов:", self.spin_workers)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        self.btn_bench = QPushButton("Запустить бенчмарк")
        self.btn_bench.clicked.connect(self._run_benchmark)
        btn_row.addWidget(self.btn_bench)
        layout.addLayout(btn_row)

        self.output_bench = QTextEdit()
        self.output_bench.setReadOnly(True)
        layout.addWidget(self.output_bench)
        return widget

    def _run_benchmark(self):
        self.btn_bench.setEnabled(False)
        self.output_bench.setPlainText("Выполняется замер производительности, подождите...")

        self._worker = BenchmarkWorker(
            total_count=self.spin_bench_count.value(),
            workers=self.spin_workers.value(),
        )
        self._worker.finished_signal.connect(self._on_benchmark_finished)
        self._worker.error_signal.connect(self._on_benchmark_error)
        self._worker.start()

    def _on_benchmark_finished(self, result: BenchmarkResult):
        self.btn_bench.setEnabled(True)
        samples = "\n".join(f"  - {pwd}" for pwd in result.sample_passwords)
        self.output_bench.setPlainText(
            f"Сгенерировано паролей: {result.total_count:,}\n"
            f"Процессов: {result.workers}\n"
            f"Последовательный генератор: {result.sequential_time:.4f} сек\n"
            f"Параллельный генератор:     {result.parallel_time:.4f} сек\n"
            f"Ускорение:                  x{result.speedup:.2f}\n\n"
            f"Примеры сгенерированных паролей:\n{samples}"
        )

    def _on_benchmark_error(self, message: str):
        self.btn_bench.setEnabled(True)
        self.output_bench.setPlainText("")
        QMessageBox.critical(self, "Ошибка бенчмарка", message)