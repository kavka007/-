import random
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys

# Увеличиваем лимит для обработки больших строк
sys.set_int_max_str_digits(100000)


class RLEEncoder:
    def __init__(self, variant=2):
        self.variant = variant

    def encode(self, data):
        if self.variant == 1:
            return self._encode_variant1(data)
        else:
            return self._encode_variant2(data)

    def _encode_variant1(self, data):
        encoded = bytearray()
        i = 0
        n = len(data)

        while i < n:
            current = data[i]
            count = 1

            while i + count < n and count < 64 and data[i + count] == current:
                count += 1

            encoded.append(0b11000000 | (count - 1))
            encoded.append(current)
            i += count

        return bytes(encoded)

    def _encode_variant2(self, data):
        encoded = []
        i = 0
        n = len(data)

        while i < n:
            current = data[i]
            count = 1

            while i + count < n and data[i + count] == current:
                count += 1

            encoded.append(f"{count}{current} ")
            i += count

        return "".join(encoded).strip()

    def decode(self, encoded_data):
        if self.variant == 1:
            return self._decode_variant1(encoded_data)
        else:
            return self._decode_variant2(encoded_data)

    def _decode_variant1(self, encoded_data):
        decoded = []
        i = 0
        n = len(encoded_data)

        while i < n:
            byte = encoded_data[i]
            if (byte & 0b11000000) == 0b11000000:
                count = (byte & 0b00111111) + 1
                value = encoded_data[i + 1]
                decoded.extend([value] * count)
                i += 2
            else:
                decoded.append(byte)
                i += 1

        return decoded

    def _decode_variant2(self, encoded_data):
        decoded = []
        parts = encoded_data.strip().split()
        for part in parts:
            if len(part) < 2:
                continue
            count_str = part[:-1]
            value_char = part[-1]
            if not count_str.isdigit():
                continue
            count = int(count_str)
            value = 1 if value_char == '1' else 0
            decoded.extend([value] * count)
        return decoded


class AvatarVisualizer:
    def __init__(self, size=(100, 100)):
        self.size = size

    def visualize(self, data, filename):
        data = data[:self.size[0] * self.size[1]]
        if len(data) < self.size[0] * self.size[1]:
            data.extend([0] * (self.size[0] * self.size[1] - len(data)))

        arr = np.array(data, dtype=np.uint8) * 255
        img = Image.fromarray(arr.reshape(self.size), 'L')
        img.save(filename)


class RLEAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RLE Encoder/Decoder")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        self.encoder = RLEEncoder(variant=2)
        self.visualizer = AvatarVisualizer()

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground='#333')

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        header = ttk.Label(main_frame, text="RLE Encoder/Decoder", style='Header.TLabel')
        header.pack(pady=(0, 20))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Сгенерировать random.txt", command=self.generate_random_file).pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Button(btn_frame, text="Запустить весь процесс", command=self.run_full_pipeline).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Кодировать", command=self.encode_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Декодировать", command=self.decode_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Визуализировать", command=self.visualize_data).pack(side=tk.LEFT, padx=5)

        param_frame = ttk.Frame(main_frame)
        param_frame.pack(fill=tk.X, pady=10)

        ttk.Label(param_frame, text="Входной файл:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.input_entry = ttk.Entry(param_frame, width=50)
        self.input_entry.grid(row=0, column=1, padx=5)
        ttk.Button(param_frame, text="Обзор...", command=self.browse_input).grid(row=0, column=2, padx=5)

        ttk.Label(param_frame, text="Выходной файл:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.output_entry = ttk.Entry(param_frame, width=50)
        self.output_entry.grid(row=1, column=1, padx=5)
        ttk.Button(param_frame, text="Обзор...", command=self.browse_output).grid(row=1, column=2, padx=5)

        ttk.Label(param_frame, text="Вариант кодирования:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.variant_var = tk.IntVar(value=2)
        ttk.Radiobutton(param_frame, text="Вариант 1", variable=self.variant_var, value=1).grid(row=2, column=1,
                                                                                                sticky=tk.W)
        ttk.Radiobutton(param_frame, text="Вариант 2", variable=self.variant_var, value=2).grid(row=2, column=2,
                                                                                                sticky=tk.W)

        ttk.Label(main_frame, text="Журнал операций:").pack(anchor=tk.W, pady=(10, 0))
        self.log_text = tk.Text(main_frame, height=15, width=85, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.input_entry.insert(0, "random.txt")
        self.output_entry.insert(0, "encoded.txt")

    def generate_random_file(self):
        try:
            file_path = "random.txt"
            with open(file_path, 'w') as f:
                f.write(" ".join(str(random.randint(0, 1)) for _ in range(10000)))

            self.log_message(f"Файл {file_path} успешно создан (10000 случайных 0 и 1)")
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, file_path)
            messagebox.showinfo("Успех", f"Файл {file_path} успешно создан!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.log_message(f"Ошибка при генерации файла: {str(e)}")

    def browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)

    def browse_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def run_full_pipeline(self):
        try:
            input_file = self.input_entry.get()
            if not input_file:
                raise ValueError("Не указан входной файл")

            # Чтение данных с обработкой больших файлов
            with open(input_file, 'r') as f:
                data = []
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    data.extend(int(x) for x in chunk.split() if x.isdigit())
                data = data[:10000]

            self.log_message(f"Прочитано {len(data)} символов из {input_file}")

            self.visualizer.visualize(data, 'original_avatar.png')
            self.log_message("Создано изображение original_avatar.png")

            self.encoder.variant = self.variant_var.get()
            encoded = self.encoder.encode(data)
            encoded_file = 'encoded.txt'

            if isinstance(encoded, bytes):
                with open(encoded_file, 'wb') as f:
                    f.write(encoded)
            else:
                with open(encoded_file, 'w', encoding='utf-8') as f:
                    f.write(encoded)

            self.log_message(f"Сжатые данные сохранены в {encoded_file}")

            if isinstance(encoded, bytes):
                with open(encoded_file, 'rb') as f:
                    encoded_data = f.read()
            else:
                with open(encoded_file, 'r', encoding='utf-8') as f:
                    encoded_data = f.read()

            decoded_data = self.encoder.decode(encoded_data)[:10000]

            decoded_file = 'decoded.txt'
            with open(decoded_file, 'w', encoding='utf-8') as f:
                f.write(" ".join(map(str, decoded_data)))

            self.log_message(f"Декодированные данные сохранены в {decoded_file}")

            self.visualizer.visualize(decoded_data, 'decoded_avatar.png')
            self.log_message("Создано изображение decoded_avatar.png")

            if len(data) == len(decoded_data) and all(a == b for a, b in zip(data, decoded_data)):
                self.log_message("Проверка: данные полностью совпадают!")
            else:
                self.log_message("Внимание: данные не совпадают!")

            messagebox.showinfo("Успех", "Процесс завершен!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.log_message(f"Ошибка: {str(e)}")

    def encode_data(self):
        try:
            input_file = self.input_entry.get()
            output_file = self.output_entry.get()

            if not input_file or not output_file:
                raise ValueError("Не указаны файлы")

            with open(input_file, 'r') as f:
                data = []
                for line in f:
                    data.extend(int(x) for x in line.split() if x.isdigit())
                data = data[:10000]

            self.encoder.variant = self.variant_var.get()
            encoded = self.encoder.encode(data)

            if isinstance(encoded, bytes):
                with open(output_file, 'wb') as f:
                    f.write(encoded)
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(encoded)

            original_size = len(data)
            encoded_size = len(encoded)
            ratio = original_size / encoded_size if encoded_size > 0 else 0

            self.log_message(f"Закодировано: {output_file}")
            self.log_message(f"Исходный размер: {original_size}")
            self.log_message(f"Сжатый размер: {encoded_size}")
            self.log_message(f"Коэффициент: {ratio:.2f}:1")

            messagebox.showinfo("Успех", "Кодирование завершено!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.log_message(f"Ошибка: {str(e)}")

    def decode_data(self):
        try:
            input_file = self.input_entry.get()
            output_file = self.output_entry.get()

            if not input_file or not output_file:
                raise ValueError("Не указаны файлы")

            if self.variant_var.get() == 1:
                with open(input_file, 'rb') as f:
                    encoded_data = f.read()
            else:
                with open(input_file, 'r', encoding='utf-8') as f:
                    encoded_data = f.read()

            decoded_data = self.encoder.decode(encoded_data)[:10000]

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(" ".join(map(str, decoded_data)))

            self.log_message(f"Декодировано: {output_file}")
            messagebox.showinfo("Успех", "Декодирование завершено!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.log_message(f"Ошибка: {str(e)}")

    def visualize_data(self):
        try:
            input_file = self.input_entry.get()
            output_file = os.path.splitext(self.output_entry.get())[0] + ".png"

            if not input_file:
                raise ValueError("Не указан файл")

            with open(input_file, 'r') as f:
                data = []
                for line in f:
                    data.extend(int(x) for x in line.split() if x.isdigit())
                data = data[:10000]

            self.visualizer.visualize(data, output_file)
            self.log_message(f"Изображение сохранено: {output_file}")
            messagebox.showinfo("Успех", "Визуализация создана!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.log_message(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RLEAppGUI(root)
    root.mainloop()