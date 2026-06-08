import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
import math


class RSACryptoApp:
    def __init__(self, root):
        self.root = root
        root.title("RSA Cryptography")

        self.p = 0
        self.q = 0
        self.n = 0
        self.phi = 0
        self.e_key = 65537 # заменено с e на e_key
        self.d = 0

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Текстовые поля
        self.text_original = tk.Text(self.root, height=10, width=50)
        self.text_original.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.text_decrypted = tk.Text(self.root, height=10, width=50)
        self.text_decrypted.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        # Кнопки
        self.btn_encrypt = tk.Button(self.root, text="Зашифровать", command=self.encrypt_file)
        self.btn_encrypt.grid(row=2, column=0, pady=5)

        self.btn_decrypt = tk.Button(self.root, text="Расшифровать", command=self.decrypt_file)
        self.btn_decrypt.grid(row=2, column=1, pady=5)

    def gcd(self, a, b):
        while b != 0:
            a, b = b, a % b
        return a

    def modinv(self, a, m):
        g, x, y = self.extended_gcd(a, m)
        if g != 1:
            return None  # Обратного элемента не существует
        else:
            return x % m

    def extended_gcd(self, a, b):
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = self.extended_gcd(b % a, a)
            return (g, x - (b // a) * y, y)

    def is_prime(self, num):
        if num < 2:
            return False
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                return False
        return True

    def generate_keys(self):
        self.p = 383
        self.q = 509

        if not self.is_prime(self.p) or not self.is_prime(self.q):
            raise ValueError("p или q не являются простыми числами")

        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)

        self.e_key = 65537
        if self.gcd(self.e_key, self.phi) != 1:
            self.e_key = 3
            while self.gcd(self.e_key, self.phi) != 1:
                self.e_key += 2

        self.d = self.modinv(self.e_key, self.phi)
        if self.d is None:
            raise ValueError("Не удалось найти обратный элемент для e по модулю phi")

    def encrypt_number(self, m):
        return pow(m, self.e_key, self.n)

    def decrypt_number(self, c):
        return pow(c, self.d, self.n)

    def encrypt_file(self):
        try:
            input_file = "1.txt"
            encrypted_file = "2.txt"
            keys_file = "keys.txt"

            if not Path(input_file).exists():
                messagebox.showerror("Ошибка", f"Файл {input_file} не найден.")
                return

            self.generate_keys()

            # Сохраняем ключи
            with open(keys_file, 'w', encoding='utf-8') as f:
                f.write(f"p={self.p}\nq={self.q}\nn={self.n}\nphi={self.phi}\ne={self.e_key}\nd={self.d}")

            # Читаем исходный файл
            with open(input_file, 'r', encoding='utf-8') as f:
                original_message = f.read()

            self.text_original.delete(1.0, tk.END)
            self.text_original.insert(tk.END, original_message)

            # Шифруем каждый символ
            encrypted_numbers = []
            for char in original_message:
                m = ord(char)
                if m > self.n:
                    messagebox.showerror(
                        "Ошибка",
                        f"Код символа '{char}' ({m}) больше n={self.n}.\n"
                        "Числа p и q должны быть больше, чтобы n было больше кода символа."
                    )
                    return
                encrypted_numbers.append(str(self.encrypt_number(m)))

            # Сохраняем зашифрованный текст
            encrypted_text = " ".join(encrypted_numbers)
            with open(encrypted_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_text)

            messagebox.showinfo("Успех", "Сообщение успешно зашифровано и сохранено в файл 2.txt")

        except Exception as ex:
            messagebox.showerror("Ошибка", f"Ошибка при шифровании: {str(ex)}")

    def decrypt_file(self):
        try:
            encrypted_file = "2.txt"
            decrypted_file = "3.txt"
            keys_file = "keys.txt"

            if not Path(encrypted_file).exists():
                messagebox.showerror("Ошибка", f"Файл {encrypted_file} не найден.")
                return
            if not Path(keys_file).exists():
                messagebox.showerror("Ошибка", f"Файл с ключами {keys_file} не найден.")
                return

            # Читаем ключи
            with open(keys_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            temp_e_key = 0
            for line in lines:
                parts = line.strip().split('=')
                if len(parts) != 2:
                    continue
                key = parts[0].strip()
                val = parts[1].strip()
                if key == "p":
                    self.p = int(val)
                elif key == "q":
                    self.q = int(val)
                elif key == "n":
                    self.n = int(val)
                elif key == "phi":
                    self.phi = int(val)
                elif key == "d":
                    self.d = int(val)
                elif key == "e":
                    temp_e_key = int(val)

            self.e_key = temp_e_key

            # Читаем зашифрованный текст
            with open(encrypted_file, 'r', encoding='utf-8') as f:
                encrypted_text = f.read()

            encrypted_parts = encrypted_text.split()

            decrypted_chars = []
            for part in encrypted_parts:
                part = part.strip()
                if not part:
                    continue

                try:
                    c = int(part)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Ошибка разбора зашифрованного числа: '{part}'")
                    return

                m = self.decrypt_number(c)

                if m > 0x10FFFF or m < 0:  # Максимальное значение для Unicode
                    messagebox.showerror("Ошибка",
                                         f"Расшифрованное число {m} не может быть преобразовано в символ.")
                    return

                decrypted_chars.append(chr(m))

            decrypted_message = "".join(decrypted_chars)

            # Сохраняем расшифрованный текст
            with open(decrypted_file, 'w', encoding='utf-8') as f:
                f.write(decrypted_message)

            self.text_decrypted.delete(1.0, tk.END)
            self.text_decrypted.insert(tk.END, decrypted_message)

            messagebox.showinfo("Успех", "Расшифровка прошла успешно!")

        except Exception as ex:
            messagebox.showerror("Ошибка", f"Ошибка при расшифровке: {str(ex)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RSACryptoApp(root)
    root.mainloop()