"""Новые результаты аудита 28.09.2026.

N1. Двухбуквенная система «читаем 2 последние, стираем 2» шаг в шаг повторяет исходную.
N2. Инвариант «за каждой А, кроме возможной последней, сразу идёт В».
Запуск: python scripts/new_results.py
Кодировка файла: A=А, B=Б, V=В. В основном коде репозитория В — это C.
"""
ORIG = {"A": "BBB", "B": "AV", "V": "B"}
BIN2 = {"BA": "BBB", "BB": "AB", "AB": "B", "AA": "BBB"}
# Четыре суффикса заданы явно. БА — чтение А (h заканчивается на БА).
# АА на траекториях Б^n не встречается; правило доопределено, чтобы шаг был тотальным.


def T(n):
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def step1(w):
    return ORIG[w[-1]] + w[:-2]


def step2(w):
    return BIN2[w[-2:]] + w[:-2]


def h(w):
    return w.replace("V", "B")


def invariant(w):
    """А, не стоящая в конце, сразу сопровождается В. В появляется только в паре АВ."""
    return all(w[i + 1] == "V" for i in range(len(w) - 1) if w[i] == "A")


def check_N1_N2(N=100):
    for n in range(2, N):
        w = u = "B" * n
        while len(w) >= 2:
            if not invariant(w):
                raise AssertionError((n, w))
            if h(w) != u:
                raise AssertionError((n, w, u))
            w, u = step1(w), step2(u)
        if h(w) != u or u != "B":
            raise AssertionError((n, w, u))
    for n in range(2, N):
        u = "B" * n
        while True:
            u = step2(u)
            if set(u) == {"B"}:
                break
        if len(u) != T(n):
            raise AssertionError((n, len(u), T(n)))
    return True


def S(n, step):
    w = "B" * n
    k = 0
    while len(w) >= 2:
        w = step(w)
        k += 1
    return k


def renamings():
    """Шесть переименований системы жюри. Кодовая буква — образ Б."""
    letters = "ABV"
    from itertools import permutations

    out = []
    for pi in permutations(letters):
        rename = dict(zip("ABV", pi))

        def apply(s, rename=rename):
            return "".join(rename[c] for c in s)

        prod = {apply(x): apply(ORIG[x]) for x in "ABV"}
        out.append((prod, rename["B"]))
    return out


if __name__ == "__main__":
    print("N1+N2 (n<100):", check_N1_N2())
    print("S(27): orig =", S(27, step1), " bin2 =", S(27, step2))
