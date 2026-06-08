import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Константы ---
W_range = [5, 20]
P_range = [0, 50]


# ========== МОДИФИКАТОРЫ (по методичке стр. 22) ==========
def dil(mu):
    """Растяжение (слегка) - корень кубический (работает и для отрицательных)"""
    return np.sign(mu) * np.abs(mu) ** (1/3)


def con(mu):
    """Концентрация (очень) - квадрат"""
    return mu ** 2


def not_fuzzy(mu):
    """Отрицание (не)"""
    return 1 - mu


# ========== ФУНКЦИИ ПРИНАДЛЕЖНОСТИ ДЛЯ ВЕСА ==========
def mu_W_low(w):
    """Вес ткани: малый"""
    return 0.45 - 0.55 * np.sin(np.pi / 14.5 * (w - 12.3))


def mu_W_medium(w):
    """Вес ткани: средний"""
    return 0.95 - 0.45 * np.sin(np.pi / 14.8 * np.abs(w - 12.7))


def mu_W_high(w):
    """Вес ткани: большой"""
    return 0.55 + 0.45 * np.sin(np.pi / 15.2 * (w - 12.8))


def mu_W_slightly_low(w):
    """Вес ткани: слегка малый (модификатор из методички)"""
    return dil(mu_W_low(w))


# ========== ФУНКЦИИ ПРИНАДЛЕЖНОСТИ ДЛЯ ДАВЛЕНИЯ ==========
def mu_P_low(p):
    val = abs(1 / (1 + 0.35 * p))
    return min(val, 1.0)


def mu_P_medium(p):
    val = abs(1 / (1 + 0.25 * (p - 24.5)))
    return min(val, 1.0)


def mu_P_high(p):
    val = abs(1 / (1 + 0.2 * (p - 44.0)))
    return min(val, 1.0)


# --- Правила из варианта 47 ---
rules = [
    ('А', [('weight', 'малый'), ('pressure', 'малое')], "Вес=малый И Давление=малое"),
    ('А', [('weight', 'малый'), ('pressure', 'среднее')], "Вес=малый И Давление=среднее"),
    ('А', [('weight', 'средний'), ('pressure', 'малое')], "Вес=средний И Давление=малое"),
    ('Б', [('weight', 'малый'), ('pressure', 'большое')], "Вес=малый И Давление=большое"),
    ('Б', [('weight', 'средний'), ('pressure', 'среднее')], "Вес=средний И Давление=среднее"),
    ('Б', [('weight', 'большой'), ('pressure', 'малое')], "Вес=большой И Давление=малое"),
    ('В', [('weight', 'средний'), ('pressure', 'большое')], "Вес=средний И Давление=большое"),
    ('В', [('weight', 'большой'), ('pressure', 'среднее')], "Вес=большой И Давление=среднее"),
    ('В', [('weight', 'большой'), ('pressure', 'большое')], "Вес=большой И Давление=большое"),
    ('Г', [('weight', 'слегка малый'), ('pressure', 'любое')],
     "Вес=слегка малый И (Давление=малое ИЛИ среднее ИЛИ большое)"),
]


def evaluate_rules_with_details(w_val, p_val):
    """Оценка всех правил с использованием min/max"""
    # Степени принадлежности
    mu_w = {
        'малый': mu_W_low(w_val),
        'средний': mu_W_medium(w_val),
        'большой': mu_W_high(w_val),
        'слегка малый': mu_W_slightly_low(w_val)
    }

    mu_p = {
        'малое': mu_P_low(p_val),
        'среднее': mu_P_medium(p_val),
        'большое': mu_P_high(p_val)
    }

    # Для правила Г: максимум по давлениям
    mu_p_any = max(mu_p['малое'], mu_p['среднее'], mu_p['большое'])

    # Результаты по классам
    class_results = {'А': 0.0, 'Б': 0.0, 'В': 0.0, 'Г': 0.0}
    rules_details = {cls: [] for cls in ['А', 'Б', 'В', 'Г']}

    for class_name, conditions, desc in rules:
        if class_name == 'Г' and conditions[0][0] == 'weight' and conditions[1][1] == 'любое':
            # Для правила Г: min(μ_слегка_малый(W), max(μ_давление))
            fire = min(mu_w['слегка малый'], mu_p_any)

            # Формула для красоты
            formula = f"μ = min(μ_слегка_малый(W)={mu_w['слегка малый']:.3f}, max(μ_давление)={mu_p_any:.3f})"
            detailed = f"{formula} = {fire:.3f}"
        else:
            # Обычное правило: минимум по условиям
            values = []
            terms = []
            for var, term in conditions:
                if var == 'weight':
                    val = mu_w[term]
                    terms.append(f"μ_{term}(W)")
                else:
                    val = mu_p[term]
                    terms.append(f"μ_{term}(P)")
                values.append(val)

            fire = min(values)

            formula = f"μ = min({', '.join([f'{t}={v:.3f}' for t, v in zip(terms, values)])})"
            detailed = f"{formula} = {fire:.3f}"

        rules_details[class_name].append({
            'desc': desc,
            'value': fire,
            'formula': formula,
            'detailed': detailed
        })

        if fire > class_results[class_name]:
            class_results[class_name] = fire

    return class_results, mu_w, mu_p, rules_details

def lukasiewicz_rules(mu_values):
        results = []
        n = len(mu_values)

        for i in range(n):
            v = [0] * n
            v[i] = 1
            parts = []
            values = []

            for j in range(n):
                val = 1 - mu_values[j] + v[j]
                parts.append(f"(1 − {mu_values[j]:.3f} + {v[j]})")
                values.append(val)

            mu = min([1] + values)
            formula = "μ = (1 ∩ " + " ∩ ".join(parts) + ")"
            results.append((formula, mu))

        return results


# --- Основное приложение ---
class FuzzyApp:
    def __init__(self, root):
        self.root = root
        root.title("Нечеткий эксперт (вар. 47) - СО СЛЕГКА МАЛЫЙ")
        root.geometry("1500x1000")
        root.configure(bg='#2b2b2b')

        self.w_val = tk.DoubleVar(value=12.5)
        self.p_val = tk.DoubleVar(value=25.0)

        self.setup_ui()
        self.update_plots()
        self.calculate()

    def setup_ui(self):
        title = tk.Label(self.root,
                         text="🧠 Лабораторная №2: Нечеткая логика (вар. 47)",
                         font=('Arial', 16, 'bold'), bg='#2b2b2b', fg='#ffae6a')
        title.pack(pady=5)

        top_frame = tk.Frame(self.root, bg='#2b2b2b')
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # График веса
        weight_frame = tk.LabelFrame(top_frame, text="Вес ткани (W) - с модификатором 'слегка малый'",
                                     font=('Arial', 12, 'bold'),
                                     bg='#2b2b2b', fg='#5aa3b8',
                                     bd=3, relief=tk.GROOVE)
        weight_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.fig_weight, self.ax_weight = plt.subplots(figsize=(5, 3), facecolor='#2b2b2b')
        self.canvas_weight = FigureCanvasTkAgg(self.fig_weight, master=weight_frame)
        self.canvas_weight.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # График давления
        pressure_frame = tk.LabelFrame(top_frame, text="Давление (P)",
                                       font=('Arial', 12, 'bold'),
                                       bg='#2b2b2b', fg='#b85a5a',
                                       bd=3, relief=tk.GROOVE)
        pressure_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.fig_pressure, self.ax_pressure = plt.subplots(figsize=(5, 3), facecolor='#2b2b2b')
        self.canvas_pressure = FigureCanvasTkAgg(self.fig_pressure, master=pressure_frame)
        self.canvas_pressure.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Фрейм для ввода
        input_frame = tk.Frame(self.root, bg='#3c3c3c', bd=2, relief=tk.GROOVE)
        input_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(input_frame, text="Вес ткани W (5-20):", font=('Arial', 11),
                 bg='#3c3c3c', fg='#ffae6a').grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.weight_entry = tk.Entry(input_frame, textvariable=self.w_val,
                                     bg='#2a2a2a', fg='#ffae6a', bd=2,
                                     font=('Arial', 11), width=15)
        self.weight_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(input_frame, text="Давление P (0-50):", font=('Arial', 11),
                 bg='#3c3c3c', fg='#ffae6a').grid(row=1, column=0, padx=10, pady=10, sticky='w')

        self.pressure_entry = tk.Entry(input_frame, textvariable=self.p_val,
                                       bg='#2a2a2a', fg='#ffae6a', bd=2,
                                       font=('Arial', 11), width=15)
        self.pressure_entry.grid(row=1, column=1, padx=10, pady=10)

        calc_btn = tk.Button(input_frame, text="РАССЧИТАТЬ",
                             font=('Arial', 12, 'bold'), bg='#6a4e3a', fg='white',
                             activebackground='#8a6e5a', activeforeground='white',
                             bd=0, padx=30, pady=10, command=self.on_calculate_click)
        calc_btn.grid(row=0, column=2, rowspan=2, padx=20, pady=10)

        # Фрейм для результатов
        result_container = tk.Frame(self.root, bg='#1e1e1e', bd=2, relief=tk.SUNKEN)
        result_container.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)

        self.result_canvas = tk.Canvas(result_container, bg='#1e1e1e', highlightthickness=0)
        scrollbar = tk.Scrollbar(result_container, orient="vertical", command=self.result_canvas.yview)
        self.scrollable_frame = tk.Frame(self.result_canvas, bg='#1e1e1e')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all"))
        )

        self.result_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.result_canvas.configure(yscrollcommand=scrollbar.set)

        self.result_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.result_text = tk.Text(self.scrollable_frame,
                                   font=('Courier New', 10),
                                   bg='#1e1e1e', fg='#a0d6b4',
                                   wrap=tk.WORD, height=30,
                                   bd=0, padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        def on_mousewheel(event):
            self.result_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.result_canvas.bind_all("<MouseWheel>", on_mousewheel)

        self.weight_entry.bind('<Return>', lambda e: self.on_calculate_click())
        self.pressure_entry.bind('<Return>', lambda e: self.on_calculate_click())

    def on_calculate_click(self):
        try:
            w = float(self.weight_entry.get())
            p = float(self.pressure_entry.get())

            if not (5 <= w <= 20):
                messagebox.showerror("Ошибка", "Вес ткани должен быть от 5 до 20!")
                return
            if not (0 <= p <= 50):
                messagebox.showerror("Ошибка", "Давление должно быть от 0 до 50!")
                return

            self.w_val.set(round(w, 2))
            self.p_val.set(round(p, 2))

            self.update_plots()
            self.calculate()

        except ValueError:
            messagebox.showerror("Ошибка", "Введите числа!")

    def update_plots(self):
        w = self.w_val.get()
        p = self.p_val.get()

        # График веса
        self.ax_weight.clear()
        x_w = np.linspace(5, 20, 200)

        self.ax_weight.plot(x_w, [mu_W_low(x) for x in x_w],
                            label='Малый', color='#5aa3b8', linewidth=2)
        self.ax_weight.plot(x_w, [mu_W_medium(x) for x in x_w],
                            label='Средний', color='#f9a65a', linewidth=2)
        self.ax_weight.plot(x_w, [mu_W_high(x) for x in x_w],
                            label='Большой', color='#b85a5a', linewidth=2)
        self.ax_weight.plot(x_w, [mu_W_slightly_low(x) for x in x_w],
                            label='Слегка малый', color='#ffae6a', linewidth=2, linestyle='--')

        self.ax_weight.axvline(x=w, color='white', linestyle='--', alpha=0.7, linewidth=2)
        self.ax_weight.set_xlim(5, 20)
        self.ax_weight.set_ylim(0, 1.05)
        self.ax_weight.set_xlabel('Вес ткани (W)', color='#ffae6a', fontsize=12)
        self.ax_weight.set_ylabel('Принадлежность', color='#ffae6a', fontsize=12)
        self.ax_weight.legend(loc='upper right', facecolor='#2a2a2a', labelcolor='#e0e0e0')
        self.ax_weight.grid(True, linestyle=':', color='#444444')
        self.ax_weight.set_facecolor('#1e1e1e')
        self.ax_weight.tick_params(colors='#aaaaaa')
        self.canvas_weight.draw()

        # График давления
        self.ax_pressure.clear()
        x_p = np.linspace(0, 50, 300)

        self.ax_pressure.plot(x_p, [mu_P_low(x) for x in x_p],
                              label='Малое', color='#5aa3b8', linewidth=2)
        self.ax_pressure.plot(x_p, [mu_P_medium(x) for x in x_p],
                              label='Среднее', color='#f9a65a', linewidth=2)
        self.ax_pressure.plot(x_p, [mu_P_high(x) for x in x_p],
                              label='Большое', color='#b85a5a', linewidth=2)

        self.ax_pressure.axvline(x=p, color='white', linestyle='--', alpha=0.7, linewidth=2)
        self.ax_pressure.set_xlim(0, 50)
        self.ax_pressure.set_ylim(0, 1.05)
        self.ax_pressure.set_xlabel('Давление (P)', color='#ffae6a', fontsize=12)
        self.ax_pressure.set_ylabel('Принадлежность', color='#ffae6a', fontsize=12)
        self.ax_pressure.legend(loc='upper right', facecolor='#2a2a2a', labelcolor='#e0e0e0')
        self.ax_pressure.grid(True, linestyle=':', color='#444444')
        self.ax_pressure.set_facecolor('#1e1e1e')
        self.ax_pressure.tick_params(colors='#aaaaaa')
        self.canvas_pressure.draw()

    def calculate(self):
        w = self.w_val.get()
        p = self.p_val.get()

        results, mu_w, mu_p, rules_details = evaluate_rules_with_details(w, p)

        best_class = max(results, key=results.get)
        best_value = results[best_class]

        output = []
        output.append("=" * 100)
        output.append("ВХОДНЫЕ ДАННЫЕ:")
        output.append(f"  Вес ткани W = {w:.2f}")
        output.append(f"  Давление P = {p:.2f}")
        output.append("=" * 100)

        output.append("\nСТЕПЕНИ ПРИНАДЛЕЖНОСТИ:")
        output.append(f"  μ_малый(W) = {mu_w['малый']:.4f}")
        output.append(f"  μ_средний(W) = {mu_w['средний']:.4f}")
        output.append(f"  μ_большой(W) = {mu_w['большой']:.4f}")
        output.append(f"  μ_слегка_малый(W) = {mu_w['слегка малый']:.4f}")
        output.append("=" * 100)

        output.append("\nВЫЧИСЛЕНИЕ СТЕПЕНЕЙ ИСТИННОСТИ ПО ФОРМУЛЕ ИЗ МЕТОДИЧКИ:")
        output.append("μ = 1 ∩ (1-μ₁+ν₁) ∩ (1-μ₂+ν₂) ∩ (1-μ₃+ν₃) ∩ (1-μ₄+ν₄)")
        output.append("где νⱼ = 1 для терма, соответствующего правилу, и 0 для остальных")
        output.append("-" * 80)

        # Значения μ для всех термов
        mu_vals = [
            mu_w['малый'],
            mu_w['средний'],
            mu_w['большой'],
            mu_w['слегка малый']
        ]

        # Названия термов
        term_names = ['малый', 'средний', 'большой', 'слегка малый']

        # Для каждого правила (каждому терму соответствует своё правило)
        for rule_idx in range(4):
            output.append(f"\n{'=' * 40} ПРАВИЛО {rule_idx + 1} (для терма '{term_names[rule_idx]}') {'=' * 40}")

            # Формируем подстановку
            formula_parts = []
            values = []

            # Для каждого терма вычисляем (1 - μ + ν)
            for j in range(4):
                nu = 1 if j == rule_idx else 0
                val = 1 - mu_vals[j] + nu
                values.append(val)
                formula_parts.append(f"(1 - {mu_vals[j]:.3f} + {nu})")

            # Итоговое значение μ = min(1, все значения)
            fire = min([1] + values)

            # Формула
            formula = "μ = 1 ∩ " + " ∩ ".join(formula_parts)
            output.append(f"  {formula}")
            output.append(f"  = min(1, {', '.join([f'{v:.3f}' for v in values])}) = {fire:.4f}")

            # Показываем, какое значение получилось
            output.append(f"  Результат правила: {fire:.4f}")

        output.append("=" * 100)
        output.append("\nВЫЧИСЛЕНИЕ СТЕПЕНЕЙ ИСТИННОСТИ ПО ПРАВИЛАМ ИЗ ВАРИАНТА 47:")
        output.append("Для правил с И используется min, для ИЛИ - max")

        for class_name in ['А', 'Б', 'В', 'Г']:
            output.append(f"\n{'=' * 40} КЛАСС {class_name} {'=' * 40}")
            max_rule = None
            max_value = -1

            for i, rule in enumerate(rules_details[class_name], 1):
                output.append(f"\n  Правило {i}: {rule['desc']}")
                output.append(f"  {rule['formula']}")
                output.append(f"  Результат: {rule['detailed']}")

                if rule['value'] > max_value:
                    max_value = rule['value']
                    max_rule = rule

            output.append(f"\n  → Максимальная степень для класса {class_name}: {max_value:.4f}")
            if max_rule:
                output.append(f"    (достигнута правилом: {max_rule['desc']})")

        output.append("=" * 100)
        output.append("\nИТОГОВЫЙ РЕЗУЛЬТАТ:")

        if best_value < 0.01:
            output.append("  Не удалось определить класс (все значения слишком низкие)")
        else:
            output.append(f"  Класс аппарата: {best_class}")
            output.append(f"  Уверенность: {best_value:.4f}")
            output.append("\n  Значения по всем классам:")
            for cls, val in sorted(results.items(), key=lambda x: x[1], reverse=True):
                output.append(f"    {cls}: {val:.4f}")

        output.append("=" * 100)

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, "\n".join(output))
        self.result_canvas.yview_moveto(0)


if __name__ == '__main__':
    root = tk.Tk()
    app = FuzzyApp(root)
    root.mainloop()