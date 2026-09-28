"""Воспроизводит все таблицы и рисунки работы. Запуск из корня: python scripts/run_all.py
Для таблицы перебора сначала: make -C csrc && ./csrc/enum 2 22 > results/enumeration.csv 2> results/cycles.csv
"""
import csv, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from tagsys.core import TASK
from tagsys.collatz import collatz_orbit, predicted_halting_steps

R, F = "results", "figures"
os.makedirs(R, exist_ok=True); os.makedirs(F, exist_ok=True)

# 1) Время остановки Б^n и сравнение с Коллатцем
rows = []
for n in range(2, 601):   # прямое моделирование; дальше верна доказанная формула
    r = TASK.run("B" * n)
    orb = collatz_orbit(n)
    rows.append((n, r.steps, len(orb) - 1, max(orb), r.max_len, predicted_halting_steps(n)))
with open(f"{R}/halting_times.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["n", "tag_steps", "collatz_T_steps", "collatz_max", "tag_max_len", "formula"])
    w.writerows(rows)
assert all(a[1] == a[5] for a in rows), "формула числа шагов нарушена!"
n = np.array([a[0] for a in rows]); s = np.array([a[1] for a in rows])
plt.figure(figsize=(7, 4)); plt.scatter(n, s, s=2)
plt.yscale("log"); plt.xlabel("n (слово Б^n)"); plt.ylabel("шагов до остановки")
plt.title("Время остановки: S(n) = Σ (m + m mod 2) по орбите Коллатца"); plt.tight_layout()
plt.savefig(f"{F}/halting_times.png", dpi=160); plt.close()

# 2) Длина слова вдоль траектории Б^27 (пилообразный профиль, как у Коллатца)
w, lens = "B" * 27, []
while w is not None:
    lens.append(len(w)); w = TASK.step(w)
plt.figure(figsize=(8, 3.5)); plt.plot(lens, lw=0.6)
plt.xlabel("шаг"); plt.ylabel("длина слова"); plt.title("Б^27: 40 656 шагов, макс. длина %d" % max(lens))
plt.tight_layout(); plt.savefig(f"{F}/trajectory_27.png", dpi=160); plt.close()

# 3) Пространственно-временная диаграмма (Б^7 и цикл X A)
def spacetime(w0, steps, fname, title):
    tr = TASK.trace(w0, steps); L = max(map(len, tr))
    img = np.full((len(tr), L), -1.0)
    for i, x in enumerate(tr):
        for j, c in enumerate(x.rjust(L)):
            img[i, j] = {"A": 0, "B": 1, "C": 2}.get(c, -1)
    cmap = matplotlib.colors.ListedColormap(["white", "#d62728", "#1f77b4", "#2ca02c"])
    plt.figure(figsize=(6, 0.18 * len(tr) + 1)); plt.imshow(img, cmap=cmap, vmin=-1, vmax=2, aspect="auto")
    plt.title(title + "  (красн. А, син. Б, зел. В)"); plt.xlabel("позиция (выравнивание по правому краю)")
    plt.ylabel("шаг"); plt.tight_layout(); plt.savefig(fname, dpi=160); plt.close()

spacetime("B" * 7, 60, f"{F}/spacetime_B7.png", "Б^7 → Б^11 → Б^17 …")
spacetime("ACBACBBBA", 16, f"{F}/spacetime_cycle.png", "Цикл периода 4: АВБАВБББА")

# 4) Доля циклов по длине (если есть результаты C-перебора)
p = f"{R}/enumeration.csv"
if os.path.exists(p):
    Ls, fr = [], []
    for row in csv.DictReader(open(p)):
        Ls.append(int(row["L"])); fr.append(int(row["cycle"]) / int(row["classes"]))
    plt.figure(figsize=(6, 3.5)); plt.plot(Ls, fr, "o-")
    plt.xlabel("длина слова L"); plt.ylabel("доля классов, уходящих в цикл")
    plt.title("Полный перебор (классы по лемме 1)"); plt.grid(alpha=.3); plt.tight_layout()
    plt.savefig(f"{F}/cycle_fraction.png", dpi=160); plt.close()
print("готово: results/*.csv, figures/*.png")
