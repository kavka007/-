import os
from collections import defaultdict
from decimal import Decimal, getcontext
import tkinter as tk
from tkinter import messagebox, filedialog, ttk


class ArithmeticCoding:
    def __init__(self):
        self.freq_table = {}  # Таблица частот символов
        self.message_length = 0  # Длина сообщения
        self.symbol_codes = {}  # Коды символов

    def build_frequency_table(self, message):
        freq = defaultdict(int)
        for c in message:
            freq[c] += 1
        return dict(sorted(freq.items()))

    def calculate_symbol_codes(self, message):
        total = sum(self.freq_table.values())
        symbols = sorted(self.freq_table.keys())

        probs = {s: Decimal(self.freq_table[s]) / total for s in symbols}
        cumul = {}
        cumul_sum = Decimal(0)

        for s in symbols:
            cumul[s] = cumul_sum
            cumul_sum += probs[s]

        self.symbol_codes = {
            s: (cumul[s] + (cumul[s] + probs[s])) / Decimal(2)
            for s in symbols
        }

    def display_frequency_table(self):
        result = "Символ\tЧастота\tВероятность\tКод символа\n"
        total = sum(self.freq_table.values())

        for char, count in self.freq_table.items():
            prob = Decimal(count) / total
            code = self.symbol_codes.get(char, Decimal(0))
            symbol = "\\n" if char == '\n' else char if char != '\t' else '\\t'
            result += f"{symbol}\t{count}\t{prob:.6f}\t\t{code:.15f}\n"

        return result

    def arithmetic_encode(self, message, freq_table):
        total = sum(freq_table.values())
        symbols = sorted(freq_table.keys())

        # Создаем таблицу вероятностей и кумулятивных вероятностей
        probs = {s: Decimal(freq_table[s]) / total for s in symbols}
        cumul = {}
        cumul_sum = Decimal(0)

        for s in symbols:
            cumul[s] = cumul_sum
            cumul_sum += probs[s]

        # Инициализация
        low = Decimal(0)
        high = Decimal(1)

        for c in message:
            # Вычисляем новые границы
            range_ = high - low
            high = low + range_ * (cumul[c] + probs[c])
            low = low + range_ * cumul[c]

        # Возвращаем среднее значение в качестве кода
        return (low + high) / Decimal(2)

    def encode_file(self, input_path, output_path):
        if not os.path.exists(input_path):
            return "Файл не найден.", ""

        with open(input_path, 'r', encoding='utf-8') as f:
            message = f.read()

        self.message_length = len(message)
        self.freq_table = self.build_frequency_table(message)
        self.calculate_symbol_codes(message)

        code = self.arithmetic_encode(message, self.freq_table)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"{code}\n")
            f.write(f"{self.message_length}\n")
            for char, count in self.freq_table.items():
                f.write(f"{ord(char)}:{count}\n")

        return "Кодирование завершено.", self.display_frequency_table()

    def arithmetic_decode(self, encoded_value, freq_table, message_length):
        total = sum(freq_table.values())
        symbols = sorted(freq_table.keys())

        # Создаем таблицу вероятностей и кумулятивных вероятностей
        probs = {s: Decimal(freq_table[s]) / total for s in symbols}
        cumul = {}
        cumul_sum = Decimal(0)

        for s in symbols:
            cumul[s] = cumul_sum
            cumul_sum += probs[s]

        # Инициализация
        value = Decimal(encoded_value)
        message = []

        # Основное исправление: используем тот же алгоритм, что и при кодировании
        low = Decimal(0)
        high = Decimal(1)

        for _ in range(message_length):
            # Находим символ, соответствующий текущему значению
            for s in symbols:
                current_low = low + (high - low) * cumul[s]
                current_high = low + (high - low) * (cumul[s] + probs[s])

                if current_low <= value < current_high:
                    message.append(s)
                    low, high = current_low, current_high
                    break

        return ''.join(message)

    def decode_file(self, input_path, output_path, original_path=None):
        if not os.path.exists(input_path):
            return "Файл не найден."

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Чтение закодированного значения
            encoded_value = lines[0].strip()

            # Чтение длины сообщения
            message_length = int(lines[1].strip())

            # Чтение таблицы частот
            freq_table = {}
            for line in lines[2:]:
                if ':' in line:
                    char_code, count = line.strip().split(':')
                    freq_table[chr(int(char_code))] = int(count)

            # Декодирование
            decoded_message = self.arithmetic_decode(encoded_value, freq_table, message_length)

            # Запись декодированного сообщения
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(decoded_message)

            # Проверка с оригиналом, если он указан
            if original_path and os.path.exists(original_path):
                with open(original_path, 'r', encoding='utf-8') as f:
                    original_message = f.read()

                if original_message == decoded_message:
                    return "Декодирование завершено. Сообщение совпадает с оригиналом."
                else:
                    return "Декодирование завершено. Сообщение НЕ совпадает с оригиналом."

            return "Декодирование завершено."

        except Exception as e:
            return f"Ошибка при декодировании: {str(e)}"

class ArithmeticCodingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Арифметическое кодирование")

        self.ac = ArithmeticCoding()
        getcontext().prec = 500

        self.create_main_window()

    def create_main_window(self):
        self.main_frame = tk.Frame(self.root, padx=20, pady=20)
        self.main_frame.pack()

        tk.Label(self.main_frame,
                 text="Арифметическое кодирование/декодирование",
                 font=("Arial", 14)).pack(pady=10)

        tk.Button(self.main_frame,
                  text="Кодировать файл",
                  command=self.open_encode_window,
                  width=20).pack(pady=5)

        tk.Button(self.main_frame,
                  text="Декодировать файл",
                  command=self.open_decode_window,
                  width=20).pack(pady=5)

        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        tk.Label(self.main_frame,
                 textvariable=self.status_var,
                 bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, pady=10)

    def open_encode_window(self):
        self.encode_window = tk.Toplevel(self.root)
        self.encode_window.title("Кодирование файла")
        self.encode_window.geometry("800x600")

        main_frame = tk.Frame(self.encode_window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.table_frame = tk.Frame(main_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(self.table_frame, columns=("Символ", "Частота", "Вероятность", "Код"), show="headings")
        self.tree.heading("Символ", text="Символ")
        self.tree.heading("Частота", text="Частота")
        self.tree.heading("Вероятность", text="Вероятность")
        self.tree.heading("Код", text="Код символа")
        self.tree.column("Символ", width=100, anchor=tk.CENTER)
        self.tree.column("Частота", width=100, anchor=tk.CENTER)
        self.tree.column("Вероятность", width=150, anchor=tk.CENTER)
        self.tree.column("Код", width=250, anchor=tk.CENTER)
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        tk.Button(button_frame,
                  text="Выбрать исходный файл",
                  command=self.select_input_file).pack(side=tk.LEFT, padx=5)

        self.input_file_label = tk.Label(button_frame, text="Файл не выбран")
        self.input_file_label.pack(side=tk.LEFT, padx=5)

        self.encode_button = tk.Button(button_frame,
                                       text="Выполнить кодирование",
                                       command=self.perform_encoding,
                                       state=tk.DISABLED)
        self.encode_button.pack(side=tk.LEFT, padx=5)

        self.input_file_path = ""
        self.output_file_path = ""

    def select_input_file(self):
        path = filedialog.askopenfilename(
            title="Выберите исходный файл",
            filetypes=[("Текстовые файлы", "*.txt")]
        )
        if path:
            self.input_file_path = path
            self.input_file_label.config(text=os.path.basename(path))
            self.encode_button.config(state=tk.NORMAL)

    def perform_encoding(self):
        if not self.input_file_path:
            messagebox.showerror("Ошибка", "Файл не выбран")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt")],
            title="Сохранить закодированный файл"
        )

        if output_path:
            try:
                result, freq_table = self.ac.encode_file(self.input_file_path, output_path)
                self.status_var.set(result)

                for i in self.tree.get_children():
                    self.tree.delete(i)

                with open(self.input_file_path, 'r', encoding='utf-8') as f:
                    message = f.read()

                total = sum(self.ac.freq_table.values())
                for char, count in self.ac.freq_table.items():
                    prob = Decimal(count) / total
                    code = self.ac.symbol_codes.get(char, Decimal(0))
                    symbol = "\\n" if char == '\n' else char if char != '\t' else '\\t'
                    self.tree.insert("", tk.END, values=(
                        symbol,
                        count,
                        f"{prob:.6f}",
                        f"{code:.15f}"
                    ))

                messagebox.showinfo("Успех", "Файл успешно закодирован")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при кодировании: {str(e)}")

    def open_decode_window(self):
        self.decode_window = tk.Toplevel(self.root)
        self.decode_window.title("Декодирование файла")
        self.decode_window.geometry("600x300")

        main_frame = tk.Frame(self.decode_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Button(main_frame,
                  text="Выбрать закодированный файл",
                  command=self.select_encoded_file).pack(pady=5)

        self.encoded_file_label = tk.Label(main_frame, text="Файл не выбран")
        self.encoded_file_label.pack(pady=5)

        tk.Button(main_frame,
                  text="Выполнить декодирование",
                  command=self.perform_decoding).pack(pady=5)

        self.encoded_file_path = ""

    def select_encoded_file(self):
        path = filedialog.askopenfilename(
            title="Выберите закодированный файл",
            filetypes=[("Текстовые файлы", "*.txt")]
        )
        if path:
            self.encoded_file_path = path
            self.encoded_file_label.config(text=os.path.basename(path))

    def perform_decoding(self):
        if not self.encoded_file_path:
            messagebox.showerror("Ошибка", "Файл не выбран")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt")],
            title="Сохранить декодированный файл"
        )

        if output_path:
            try:
                original_path = filedialog.askopenfilename(
                    title="Выберите оригинальный файл для проверки (необязательно)",
                    filetypes=[("Текстовые файлы", "*.txt")]
                )

                if original_path:
                    result = self.ac.decode_file(self.encoded_file_path, output_path, original_path)
                else:
                    result = self.ac.decode_file(self.encoded_file_path, output_path)

                self.status_var.set(result)
                messagebox.showinfo("Успех", "Файл успешно декодирован")
                self.decode_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при декодировании: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ArithmeticCodingApp(root)
    root.mainloop()