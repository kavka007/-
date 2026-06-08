import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

# Настраиваем стиль matplotlib
plt.style.use('dark_background')


# --- Функции активации ---
def sigmoid(x):
    x = np.clip(x, -500, 500)
    return 1 / (1 + np.exp(-x))


def sigmoid_derivative(x):
    return x * (1 - x)


# --- Класс нейронной сети ---
class NeuralNetwork:
    def __init__(self, n_inputs, n_hidden, n_outputs, learning_rate, x0_value):
        self.n_inputs = n_inputs
        self.n_hidden = n_hidden
        self.n_outputs = n_outputs
        self.lr = learning_rate
        self.x0 = x0_value  # 1 или -1

        # Инициализация весов малыми случайными числами
        self.W1 = np.random.uniform(low=-0.05, high=0.05, size=(n_hidden, n_inputs + 1))  # +1 для X0
        self.W2 = np.random.uniform(low=-0.05, high=0.05, size=(n_outputs, n_hidden + 1))  # +1 для X0

    def forward(self, X):
        """
        X: вектор входов [x1, x2, x3, x4] (без X0)
        """
        # Добавляем X0 к входу
        X_with_bias = np.append(self.x0, X)

        # Вход -> Скрытый слой
        self.hidden_input = np.dot(self.W1, X_with_bias)
        self.hidden_output = sigmoid(self.hidden_input)

        # Добавляем X0 к скрытому слою
        self.hidden_with_bias = np.append(self.x0, self.hidden_output)

        # Скрытый -> Выход
        self.output_input = np.dot(self.W2, self.hidden_with_bias)
        self.final_output = sigmoid(self.output_input)

        return self.final_output

    def backward(self, X, y_true, output):
        # Добавляем X0 к входу для обратного прохода
        X_with_bias = np.append(self.x0, X)

        # Ошибка на выходе
        output_delta = (y_true - output) * sigmoid_derivative(output)

        # Градиенты для выходного слоя
        grad_W2 = output_delta.reshape(-1, 1) * self.hidden_with_bias.reshape(1, -1)

        # Ошибка на скрытом слое
        hidden_delta = np.dot(self.W2[:, 1:].T, output_delta) * sigmoid_derivative(self.hidden_output)

        # Градиенты для скрытого слоя
        grad_W1 = hidden_delta.reshape(-1, 1) * X_with_bias.reshape(1, -1)

        return grad_W1, grad_W2

    def train_step(self, X, y_true):
        """Один шаг обучения на одном примере"""
        output = self.forward(X)
        g1, g2 = self.backward(X, y_true, output)
        self.W1 += self.lr * g1
        self.W2 += self.lr * g2
        return 0.5 * (y_true - output) ** 2

    def compute_mse(self, X_data, y_data):
        """Вычислить MSE на всех данных"""
        total_error = 0
        for i in range(len(X_data)):
            output = self.forward(X_data[i])
            total_error += (y_data[i] - output) ** 2
        return total_error / len(X_data)

    def get_W1(self):
        return self.W1.copy()

    def get_W2(self):
        return self.W2.copy()


# --- Данные для варианта 4 ---
# --- Данные для варианта 4 (правильные) ---
def get_data():
    samples = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 1, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 1, 1, 1],
        [1, 1, 0, 0, 1],
        [1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    samples = np.array(samples)
    inputs = samples[:, :4]
    targets = samples[:, 4]
    return inputs, targets


# --- Графический интерфейс ---
class NetworkApp:
    def __init__(self, root):
        self.root = root
        root.title("🧠 НЕЙРОСЕТЕВОЙ АНАЛИЗ ДАННЫХ")
        root.geometry("1400x800")
        root.configure(bg='#f0f0f0')

        # Данные
        self.X, self.y = get_data()
        self.network = None
        self.trained = False
        self.error_history = []
        self.stop_training = False

        self.setup_ui()

    def setup_ui(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === ВЕРХНЯЯ ПАНЕЛЬ (Параметры) ===
        params_frame = ttk.LabelFrame(main_frame, text="Параметры сети", padding=10)
        params_frame.pack(fill=tk.X, pady=(0, 10))

        # Строка 1
        row1 = ttk.Frame(params_frame)
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(row1, text="Скрытых нейронов:", width=15).pack(side=tk.LEFT, padx=(0,5))
        self.neuron_var = tk.IntVar(value=3)
        neuron_spin = ttk.Spinbox(row1, from_=3, to=4, textvariable=self.neuron_var, width=10)
        neuron_spin.pack(side=tk.LEFT, padx=(0,20))

        ttk.Label(row1, text="Скорость обучения (η):", width=15).pack(side=tk.LEFT, padx=(0,5))
        self.lr_var = tk.DoubleVar(value=0.5)
        lr_entry = ttk.Entry(row1, textvariable=self.lr_var, width=10)
        lr_entry.pack(side=tk.LEFT, padx=(0,20))

        ttk.Label(row1, text="X0:", width=5).pack(side=tk.LEFT, padx=(0,5))
        self.x0_var = tk.StringVar(value="1")
        x0_combo = ttk.Combobox(row1, textvariable=self.x0_var, values=["1", "-1"], width=5, state="readonly")
        x0_combo.pack(side=tk.LEFT)

        # Строка 2
        row2 = ttk.Frame(params_frame)
        row2.pack(fill=tk.X, pady=2)

        ttk.Label(row2, text="Макс. эпох:", width=15).pack(side=tk.LEFT, padx=(0,5))
        self.epochs_var = tk.IntVar(value=500)
        epochs_entry = ttk.Entry(row2, textvariable=self.epochs_var, width=10)
        epochs_entry.pack(side=tk.LEFT, padx=(0,20))

        ttk.Label(row2, text="Целевая ошибка:", width=15).pack(side=tk.LEFT, padx=(0,5))
        self.target_err_var = tk.DoubleVar(value=0.01)
        target_entry = ttk.Entry(row2, textvariable=self.target_err_var, width=10)
        target_entry.pack(side=tk.LEFT, padx=(0,20))

        # Кнопка обучения
        self.train_btn = ttk.Button(row2, text="🚀 Обучить сеть", command=self.start_training)
        self.train_btn.pack(side=tk.LEFT, padx=(20,0))

        # Статус
        self.status_label = ttk.Label(row2, text="Сеть не обучена", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=(20,0))

        # Прогресс
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0,10))

        # === ОСНОВНАЯ ЧАСТЬ (Вкладки) ===
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка 1: График
        self.tab_chart = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_chart, text="График MSE")
        self.setup_chart_tab()

        # Вкладка 2: Результаты
        self.tab_results = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_results, text="Результаты")
        self.setup_results_tab()

        # Вкладка 3: Веса W1
        self.tab_w1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_w1, text="Веса W1")
        self.setup_w1_tab()

        # Вкладка 4: Веса W2
        self.tab_w2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_w2, text="Веса W2")
        self.setup_w2_tab()

        # === НИЖНЯЯ ПАНЕЛЬ (Лог и тестирование) ===
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10,0))

        # Лог
        log_frame = ttk.LabelFrame(bottom_frame, text="Лог обучения", padding=5)
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=60, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Тестирование
        test_frame = ttk.LabelFrame(bottom_frame, text="Тестирование", padding=5)
        test_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        test_inputs = ttk.Frame(test_frame)
        test_inputs.pack(pady=5)

        self.test_vars = []
        labels = ['X1:', 'X2:', 'X3:', 'X4:']
        for i, lbl in enumerate(labels):
            ttk.Label(test_inputs, text=lbl).grid(row=0, column=i*2, padx=(5,0))
            var = tk.StringVar(value="0")
            entry = ttk.Entry(test_inputs, textvariable=var, width=6)
            entry.grid(row=0, column=i*2+1, padx=(0,5))
            self.test_vars.append(var)

        self.test_btn = ttk.Button(test_frame, text="Вычислить", command=self.do_test, state=tk.DISABLED)
        self.test_btn.pack(pady=5)

        self.test_result = ttk.Label(test_frame, text="Результат: —", font=('Arial', 10, 'bold'))
        self.test_result.pack()

    def setup_chart_tab(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 4), facecolor='#f0f0f0')
        self.ax.set_facecolor('#ffffff')
        self.ax.tick_params(colors='#333333')
        self.ax.xaxis.label.set_color('#333333')
        self.ax.yaxis.label.set_color('#333333')
        self.ax.title.set_color('#333333')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_chart)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_results_tab(self):
        columns = ('X1', 'X2', 'X3', 'X4', 'Желаемый', 'Выход сети', 'Округлённый', 'Ошибка')
        self.tree_results = ttk.Treeview(self.tab_results, columns=columns, show='headings', height=15)

        for col in columns:
            self.tree_results.heading(col, text=col)
            self.tree_results.column(col, width=90, anchor=tk.CENTER)

        scroll = ttk.Scrollbar(self.tab_results, orient=tk.VERTICAL, command=self.tree_results.yview)
        self.tree_results.configure(yscrollcommand=scroll.set)

        self.tree_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_w1_tab(self):
        columns = ['Нейрон', 'w(X0)'] + [f'w(X{i})' for i in range(1, 5)]
        self.tree_w1 = ttk.Treeview(self.tab_w1, columns=columns, show='headings', height=10)

        for col in columns:
            self.tree_w1.heading(col, text=col)
            self.tree_w1.column(col, width=100, anchor=tk.CENTER)

        scroll = ttk.Scrollbar(self.tab_w1, orient=tk.VERTICAL, command=self.tree_w1.yview)
        self.tree_w1.configure(yscrollcommand=scroll.set)

        self.tree_w1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_w2_tab(self):
        self.tree_w2 = ttk.Treeview(self.tab_w2, show='headings', height=5)
        scroll = ttk.Scrollbar(self.tab_w2, orient=tk.VERTICAL, command=self.tree_w2.yview)
        self.tree_w2.configure(yscrollcommand=scroll.set)

        self.tree_w2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def log(self, message, color=None):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def start_training(self):
        # Проверка параметров
        try:
            hidden = self.neuron_var.get()
            lr = self.lr_var.get()
            max_epochs = self.epochs_var.get()
            target_err = self.target_err_var.get()
            x0 = 1.0 if self.x0_var.get() == "1" else -1.0

            if hidden not in [3, 4]:
                messagebox.showerror("Ошибка", "Нейронов должно быть 3 или 4")
                return
            if lr <= 0:
                messagebox.showerror("Ошибка", "Скорость обучения должна быть > 0")
                return
            if max_epochs < 1:
                messagebox.showerror("Ошибка", "Эпох должно быть > 0")
                return
            if target_err <= 0:
                messagebox.showerror("Ошибка", "Целевая ошибка должна быть > 0")
                return
        except:
            messagebox.showerror("Ошибка", "Неверные параметры")
            return

        # Отключаем кнопки
        self.train_btn.config(state=tk.DISABLED)
        self.test_btn.config(state=tk.DISABLED)
        self.progress.start(10)
        self.status_label.config(text="Обучение...", foreground="orange")
        self.log_text.delete(1.0, tk.END)

        self.trained = False
        self.error_history = []
        self.stop_training = False

        self.network = NeuralNetwork(4, hidden, 1, lr, x0)

        self.log("▶ Начало обучения")
        self.log(f"   Нейронов: {hidden} | η={lr} | X0={x0}")

        # Запускаем обучение в отдельном потоке
        def train_thread():
            epoch = 1
            while epoch <= max_epochs and not self.stop_training:
                # Перемешиваем данные
                indices = np.random.permutation(len(self.X))
                total_error = 0

                for idx in indices:
                    err = self.network.train_step(self.X[idx], self.y[idx])
                    total_error += err

                mse = (total_error / len(self.X)).item()  # .item() превращает numpy-скаляр в число
                self.error_history.append(mse)

                if epoch % 500 == 0 or epoch == 1:
                    self.root.after(0, lambda e=epoch, m=mse: self.log(f"   Эпоха {e:6}: MSE = {m:.8f}"))

                if mse <= target_err:
                    self.root.after(0, lambda e=epoch, m=mse: self.log(f"   Эпоха {e:6}: MSE = {m:.8f}"))
                    break

                epoch += 1

            self.root.after(0, lambda: self.training_complete(epoch, mse))

        thread = threading.Thread(target=train_thread)
        thread.daemon = True
        thread.start()

    def training_complete(self, epochs, final_mse):
        self.progress.stop()
        self.train_btn.config(state=tk.NORMAL)
        self.test_btn.config(state=tk.NORMAL)
        self.trained = True

        self.status_label.config(text=f"✔ Обучено за {epochs} эпох | MSE = {final_mse:.8f}", foreground="green")

        self.log(f"\n✔ Завершено за {epochs} эпох")
        self.log(f"   Итоговая MSE: {final_mse:.8f}")

        # Заполняем таблицы
        self.fill_results()
        self.fill_w1_table()
        self.fill_w2_table()

        # Обновляем график
        self.update_chart()

    def fill_results(self):
        for row in self.tree_results.get_children():
            self.tree_results.delete(row)

        for i in range(len(self.X)):
            output = self.network.forward(self.X[i]).item()
            error = self.y[i] - output
            rounded = 1 if output >= 0.5 else 0

            values = list(self.X[i]) + [self.y[i], f"{output:.6f}", rounded, f"{error:.6f}"]
            self.tree_results.insert('', tk.END, values=values)

    def fill_w1_table(self):
        for row in self.tree_w1.get_children():
            self.tree_w1.delete(row)

        W1 = self.network.get_W1()
        for j in range(W1.shape[0]):
            values = [f"N{j+1}"] + [f"{W1[j, k]:.6f}" for k in range(W1.shape[1])]
            self.tree_w1.insert('', tk.END, values=values)

    def fill_w2_table(self):
        for row in self.tree_w2.get_children():
            self.tree_w2.delete(row)

        W2 = self.network.get_W2()
        hidden = self.neuron_var.get()

        # Настраиваем колонки
        columns = ['Нейрон', 'w(X0)'] + [f'w(N{i+1})' for i in range(hidden)]
        self.tree_w2['columns'] = columns
        for col in columns:
            self.tree_w2.heading(col, text=col)
            self.tree_w2.column(col, width=100, anchor=tk.CENTER)

        values = ['Out'] + [f"{W2[0, k]:.6f}" for k in range(W2.shape[1])]
        self.tree_w2.insert('', tk.END, values=values)

    def update_chart(self):
        self.ax.clear()
        self.ax.plot(self.error_history, color='#0078d7', linewidth=1.5)
        self.ax.set_title('Ошибка обучения (MSE)', color='#333333')
        self.ax.set_xlabel('Эпоха', color='#333333')
        self.ax.set_ylabel('MSE', color='#333333')
        self.ax.grid(True, alpha=0.3, color='#cccccc')
        self.ax.set_facecolor('#f8f8f8')
        self.canvas.draw()

    def do_test(self):
        if not self.trained:
            return

        try:
            x = [float(var.get()) for var in self.test_vars]
            for v in x:
                if v < 0 or v > 1:
                    messagebox.showwarning("Предупреждение", "Значения должны быть от 0 до 1")
                    return

            output = self.network.forward(np.array(x)).item()
            rounded = 1 if output >= 0.5 else 0
            self.test_result.config(text=f"Результат: {rounded}  (вероятность: {output:.6f})")

        except ValueError:
            messagebox.showerror("Ошибка", "Введите числа!")


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkApp(root)
    root.mainloop()