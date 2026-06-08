import numpy as np
import matplotlib.pyplot as plt

a = 1.3e-2
dx = 0.1
dt = 0.01
tau_max = 100
Nx = 21
Nt = int(tau_max / dt)

x = np.linspace(0, 2, Nx)  # область [0;2]
tau = np.arange(0, tau_max+dt, dt)

T = 25 - 5 * x

def f1(tau): return 0.001 * tau**2 + 5 * np.cos(tau) + 20
def f2(tau): return 2 / (0.1 * tau + 0.1)

Fo = a * dt / dx**2
print(f"Число Фурье (Fo) = {Fo:.4f}")
if Fo > 0.5:
    print("⚠️ Предупреждение: схема неустойчива!")

results = {0: T.copy()}

for n in range(1, Nt+1):
    T_new = T.copy()
    for i in range(1, Nx-1):
        T_new[i] = T[i] + Fo * (T[i+1] - 2*T[i] + T[i-1])
    T_new[0] = f1(n*dt)
    T_new[-1] = f2(n*dt)
    T = T_new

    if n % 1000 == 0:
        results[n*dt] = T.copy()

plt.figure(figsize=(10,6))
for t, profile in results.items():
    plt.plot(x, profile, label=f"τ={t:.0f}")
plt.xlabel("x")
plt.ylabel("T(x, τ)")
plt.title("Решение уравнения теплопроводности (вариант 24)")
plt.legend()
plt.grid()
plt.show()
