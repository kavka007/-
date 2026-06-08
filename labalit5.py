import numpy as np
import matplotlib.pyplot as plt

a = 1.3e-1
dx = 0.3
dt = 0.01
tau_max = 100
Nx = 21
Nt = int(tau_max / dt)


x = np.linspace(0, 2, Nx)
tau = np.arange(0, tau_max+dt, dt)

# Начальное условие φ(x)
def phi(x): return 25 - 5 * x
T = phi(x)

# Граничные условия
def f1(tau): return 0.001 * tau**2 + 5 * np.cos(tau) + 20
def f2(tau): return 2 / (0.1 * tau + 0.1)

# Проверка устойчивости
Fo = a * dt / dx**2
print(f"Число Фурье (Fo) = {Fo:.4f}")
if Fo > 0.5:
    print("⚠️ Предупреждение: схема неустойчива!")

# Массив для хранения решения
T_all = np.zeros((Nt+1, Nx))
T_all[0, :] = T.copy()

# Основной цикл по времени
for n in range(1, Nt+1):
    T_new = T.copy()
    for i in range(1, Nx-1):
        T_new[i] = T[i] + Fo * (T[i+1] - 2*T[i] + T[i-1])
    # граничные условия
    T_new[0] = f1(n*dt)
    T_new[-1] = f2(n*dt)
    T = T_new
    T_all[n, :] = T.copy()

X, Y = np.meshgrid(x, tau)
Z = T_all

fig = plt.figure(figsize=(12,7))
ax = fig.add_subplot(111, projection='3d')

# Поверхность
surf = ax.plot_surface(X, Y, Z, cmap="PRGn_r", edgecolor="none", alpha=0.9)

# Линии граничных условий
ax.plot(np.zeros_like(tau), tau, f1(tau), color="red", linewidth=2, label="f1(τ), левая граница")
ax.plot(np.ones_like(tau)*2, tau, f2(tau), color="blue", linewidth=2, label="f2(τ), правая граница")

# Линия начального условия φ(x)
ax.plot(x, np.zeros_like(x), phi(x), color="black", linewidth=2, linestyle="--", label="φ(x), начальное условие")

# Подписи
ax.set_xlabel("x (координата)")
ax.set_ylabel("τ (время)")
ax.set_zlabel("T (температура)")
ax.set_title("Эволюция T(x, τ) с начальными и граничными условиями (вариант 24)")
fig.colorbar(surf, shrink=0.5, aspect=8)
ax.legend()

plt.show()
