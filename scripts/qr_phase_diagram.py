"""Проверка макрошага семейства (q, r) и рисунок фазовой диаграммы чистого слоя."""
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tagsys.family_qr import F, first_return

QMAX, RMAX, NMAX = 8, 4, 120


def pure_class(q, r):
    """Строгий класс исхода Б^n, n≥2, на чистом слое. Дрейф сюда не входит."""
    if r >= 2 and (q, r) == (1, 2):
        return "период"
    if r >= 2:
        return "рост"
    if q == 1:
        return "остановка"
    if q == 2:
        return "цикл"
    if q == 3:
        return "коллатц"
    if q % 2 == 0:
        return "рост"
    return "не решено"


def main():
    bad = []
    rows = []
    for q in range(1, QMAX + 1):
        for r in range(1, RMAX + 1):
            ok = 0
            for n in range(2, NMAX + 1):
                got = first_return(n, q, r)
                exp = F(n, q, r)
                if got != exp:
                    bad.append((q, r, n, got, exp))
                else:
                    ok += 1
            ev = "сжатие" if r == 1 else ("сохранение" if r == 2 else "рост")
            od_num = q * r
            od = "сжатие" if od_num < 2 else ("сохранение" if od_num == 2 else "рост")
            rows.append((q, r, ok, ev, od, pure_class(q, r)))
    os.makedirs("results", exist_ok=True)
    os.makedirs("figures", exist_ok=True)
    with open("results/qr_phase.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["q", "r", "n_checked_ok", "even_branch", "odd_branch", "pure_class"])
        wr.writerows(rows)
    print("mismatches:", len(bad))
    if bad:
        print(bad[:10])
        raise SystemExit(1)
    draw(rows)
    print("wrote results/qr_phase.csv and figures/qr_phase.png")


def draw(rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    colors = {
        "остановка": "#4C78A8",
        "цикл": "#54A24B",
        "период": "#88D27A",
        "рост": "#E45756",
        "коллатц": "#F2C14E",
        "не решено": "#F58518",
    }
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    for q, r, _ok, _ev, _od, kind in rows:
        ax.add_patch(
            Rectangle((q - 0.5, r - 0.5), 1, 1, facecolor=colors[kind], edgecolor="white", lw=1.2)
        )
        if (q, r) == (3, 1):
            ax.add_patch(
                Rectangle((q - 0.5, r - 0.5), 1, 1, fill=False, edgecolor="black", lw=2.0)
            )
    ax.set_xlim(0.5, QMAX + 0.5)
    ax.set_ylim(0.5, RMAX + 0.5)
    ax.set_xticks(range(1, QMAX + 1))
    ax.set_yticks(range(1, RMAX + 1))
    ax.set_xlabel("q  (А пишет Б^q)")
    ax.set_ylabel("r  (Б пишет (АВ)^r)")
    ax.set_aspect("equal")
    handles = [
        Rectangle((0, 0), 1, 1, facecolor=colors[k], edgecolor="white", label=k)
        for k in ("остановка", "цикл", "период", "рост", "коллатц", "не решено")
    ]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1), frameon=False)
    ax.set_title("Чистый слой: слова из одних Б. Рамка — условие задачи")
    fig.tight_layout()
    fig.savefig("figures/qr_phase.png", dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
