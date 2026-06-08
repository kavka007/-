import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Генератор иррациональных чисел
class IrrationalNumberGenerator:
    def __init__(self, lambda1, lambda2):
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.n = 0

    def next(self):
        val = (self.n * self.lambda1 * self.n * self.lambda2) % 1
        self.n += 1
        return val

class EventGenerator:
    def __init__(self, rng, N, Ns, M0, sigma0_sq, alpha0):
        self.M0 = M0
        self.sigma0_sq = sigma0_sq
        self.alpha0 = alpha0

        self.N = N
        self.Ns = Ns

        self.rng = rng
        self.gen_rand_numbers()

        A1_init, A2_init = 3, 10
        self.A1_opt, self.A2_opt = self.optimize_generator(A1_init, A2_init)


    def gen_rand_numbers(self):
        numbers = [self.rng.next() for _ in range(self.N)]
        self.numbers = numbers
        # Параметры исходного ряда
        Mx = np.mean(numbers)
        self.sigma_x_sq = np.var(numbers)
        print(f"Начальное математическое ожидание Mx: {Mx}")
        print(f"Начальная дисперсия sigma_x^2: {self.sigma_x_sq}")

        # Центрирование
        self.centered_numbers = np.array(numbers) - Mx

    def optimize_generator(self, A1, A2):
        bounds = [(0.1, 20), (0.1, 50)]
        res = minimize(self.evaluate_params, [A1, A2],
                       bounds=bounds, method='L-BFGS-B', options={'maxiter': 100})
        return res.x

    def __process_z(self, centered_np, N, Ns, A1, A2):
        result = []
        for k in range(N - Ns):
            s = 0
            for i in range(k, k + Ns):
                s += (centered_np[i] *
                      math.sqrt(self.sigma0_sq / (self.sigma_x_sq * self.alpha0 * A2)) *
                      A1 * math.exp(-A2 * self.alpha0 * (i - k)))
            zk = s / Ns + self.M0
            result.append(zk)
        return np.array(result)

    # Целевая функция ошибки
    def evaluate_params(self, x):
        A1, A2 = x
        if A2 <= 0:
            return np.inf

        z_test = self.__process_z(self.centered_numbers, self.N, self.Ns, A1, A2)
        Mz_test = np.mean(z_test)
        sigma_z_sq_test = np.var(z_test)

        Kz_test = [np.mean((z_test[:len(z_test) - S] - Mz_test) *
                           (z_test[S:] - Mz_test)) for S in range(10)]

        Kz_filtered = np.clip(np.abs(Kz_test[1:]), 1e-10, None)
        ln_Kz_test = np.log(Kz_filtered)
        coeffs_test = np.polyfit(np.arange(1, 10), ln_Kz_test, 1)
        alpha_z_test = -coeffs_test[0]

        err_M = abs(Mz_test - self.M0) / abs(self.M0)
        err_sigma = abs(sigma_z_sq_test - self.sigma0_sq) / abs(self.sigma0_sq)
        err_alpha = abs(alpha_z_test - self.alpha0) / abs(self.alpha0)

        return err_M + 1 * err_sigma + 1 * err_alpha

    def process_z(self, N, Ns):
        return self.__process_z(self.centered_numbers, N, Ns, self.A1_opt, self.A2_opt)

if __name__ == "__main__":
    # ----------------------------
    # НАЧАЛЬНЫЕ УСЛОВИЯ
    # ----------------------------
    N = 200
    lambda1 = math.e
    lambda2 = math.sqrt(3)
    M0 = 15
    sigma0_sq = 36
    alpha0 = 0.5
    Ns = 20

    rng = IrrationalNumberGenerator(lambda1, lambda2)

    genEvents = EventGenerator(rng, N, Ns, M0, sigma0_sq, alpha0)

    # ----------------------------
    # ПОЛУЧЕНИЕ ИТОГОВОГО РЯДА
    # ----------------------------
    z_opt = genEvents.process_z(N, Ns)
    Mz_opt = np.mean(z_opt)
    sigma_z_sq_opt = np.var(z_opt)

    Kz_opt = [np.mean((z_opt[:len(z_opt) - S] - Mz_opt) *
                      (z_opt[S:] - Mz_opt)) for S in range(10)]

    ln_Kz_opt = np.log(np.clip(np.abs(Kz_opt[1:]), 1e-10, None))
    coeffs_opt = np.polyfit(np.arange(1, 10), ln_Kz_opt, 1)
    alpha_z_opt = -coeffs_opt[0]

    # ----------------------------
    # ВЫВОД РЕЗУЛЬТАТОВ
    # ----------------------------
    print(f"\nОптимизированные параметры: A1 = {genEvents.A1_opt}, A2 = {genEvents.A2_opt}")
    print(f"Математическое ожидание Mz = {Mz_opt}")
    print(f"Дисперсия sigma_z^2 = {sigma_z_sq_opt}")
    print(f"Оценка alpha_z = {alpha_z_opt}\n")

    # ----------------------------
    # ГРАФИКИ (улучшенный внешний вид)
    # ----------------------------
    plt.style.use('seaborn-v0_8-darkgrid')   # Глобальный стиль

    fig, axs = plt.subplots(3, 1, figsize=(12, 16))

    # Общие параметры
    title_kwargs = dict(fontsize=16, fontweight='bold')
    label_kwargs = dict(fontsize=14)
    tick_params = dict(labelsize=12)

    # --- График 1 ---
    axs[0].plot(range(N), genEvents.numbers, label="Иррациональные числа",
                color='#1f77b4', linewidth=2)
    axs[0].set_title("Исходные иррациональные числа", **title_kwargs)
    axs[0].set_xlabel("Индекс", **label_kwargs)
    axs[0].set_ylabel("Значение", **label_kwargs)
    axs[0].tick_params(**tick_params)
    axs[0].legend(fontsize=12)

    # --- График 2 ---
    axs[1].plot(range(len(z_opt)), z_opt,
                color='#ff7f0e', linewidth=2.2, label="Случайный процесс z(k)")
    axs[1].set_title("Случайный процесс z(k)", **title_kwargs)
    axs[1].set_xlabel("k", **label_kwargs)
    axs[1].set_ylabel("z(k)", **label_kwargs)
    axs[1].tick_params(**tick_params)
    axs[1].legend(fontsize=12)

    # --- График 3 ---
    axs[2].plot(range(10), Kz_opt, 'o-', markersize=6, linewidth=2,
                color='#2ca02c', label="Корреляционная функция Kz(S)")
    axs[2].plot(range(10),
                sigma_z_sq_opt * np.exp(-alpha_z_opt * np.arange(10)),
                '--', linewidth=2.2, color='#d62728',
                label="Экспоненциальная аппроксимация")
    axs[2].set_title("Корреляционная функция и экспоненциальная аппроксимация", **title_kwargs)
    axs[2].set_xlabel("S", **label_kwargs)
    axs[2].set_ylabel("Kz(S)", **label_kwargs)
    axs[2].tick_params(**tick_params)
    axs[2].legend(fontsize=12)

    plt.tight_layout()
    plt.show()

