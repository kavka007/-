import math
from collections import Counter
import tkinter as tk
from tkinter import messagebox

# Задаем пути к файлам с алфавитами
RUSSIAN_ALPHABET_FILE = 'russian_alphabet.txt'
ENGLISH_ALPHABET_FILE = 'english_alphabet.txt'
CUSTOM_ALPHABET_FILE = 'custom_alphabet.txt'


def read_alphabet(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        alphabet = file.read()
    return alphabet


def calculate_information(message, alphabet):
    alphabet_size = len(alphabet)
    character_counts = Counter(message)
    total_characters = len(message)

    information = 0
    for char, count in character_counts.items():
        if char in alphabet:
            probability = count / total_characters
            information += -math.log2(probability) * count

    return information, alphabet_size


def check_message_language(message, alphabet):
    """Проверяет, что все символы сообщения есть в алфавите"""
    invalid_chars = set()
    for char in message:
        if char not in alphabet and char != ' ' and char != '\n':
            invalid_chars.add(char)
    return invalid_chars


def process_message():
    message = message_input.get("1.0", tk.END).strip()
    if not message:
        messagebox.showwarning("Предупреждение", "Введите сообщение.")
        return

    alphabet = ''
    if language_var.get() == 'Русский':
        alphabet = read_alphabet(RUSSIAN_ALPHABET_FILE)
    elif language_var.get() == 'Английский':
        alphabet = read_alphabet(ENGLISH_ALPHABET_FILE)
    elif language_var.get() == 'Кастомный':
        alphabet = read_alphabet(CUSTOM_ALPHABET_FILE)

    # Проверка на соответствие алфавиту
    invalid_chars = check_message_language(message, alphabet)
    if invalid_chars:
        messagebox.showerror(
            "Ошибка",
            f"Сообщение содержит символы не из выбранного алфавита:\n"
            f"{', '.join(invalid_chars)}\n"
            f"Выберите другой алфавит или измените сообщение."
        )
        return

    info, alphabet_size = calculate_information(message, alphabet)

    result_text.set(f"Длина сообщения: {len(message)}\n"
                    f"Алфавит: {alphabet}\n"
                    f"Мощность алфавита: {alphabet_size}\n"
                    f"Общее количество бит на сообщение: {info:.2f}")


# Основное окно
root = tk.Tk()
root.title("Измерение информации")

# Переменные
language_var = tk.StringVar(value='Русский')
result_text = tk.StringVar()

# Элементы интерфейса
tk.Label(root, text="Выберите язык:").pack()
tk.OptionMenu(root, language_var, 'Русский', 'Английский', 'Кастомный').pack()

tk.Label(root, text="Введите сообщение:").pack()
message_input = tk.Text(root, height=10, width=50)
message_input.pack()

tk.Button(root, text="Измерить информацию", command=process_message).pack()

tk.Label(root, textvariable=result_text, justify=tk.LEFT).pack()

# Запуск приложения
root.mainloop()