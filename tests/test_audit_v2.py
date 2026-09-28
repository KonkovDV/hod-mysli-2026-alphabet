"""N1–N3 из аудита 28.09.2026. Запуск: pytest -q tests/test_audit_v2.py"""
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import new_results as nr


def test_bin2_stepwise():
    """Б^n в исходной системе и в BIN2 совпадают на каждом шаге, включая S(27)."""
    assert nr.check_N1_N2(80)
    assert nr.S(27, nr.step1) == nr.S(27, nr.step2) == 40656


def test_A_followed_by_V():
    """На траектории Б^n буква А, не стоящая в конце, всегда сопровождается В."""
    for n in range(2, 60):
        w = "B" * n
        while len(w) >= 2:
            assert nr.invariant(w)
            w = nr.step1(w)


def _simulates(prod, X, nmax=20, sg=1):
    def T(n):
        return n // 2 if n % 2 == 0 else (3 * n + sg) // 2

    for n in range(2, nmax + 1):
        w = X * n
        steps = 0
        target = T(n)
        while True:
            if len(w) < 2 or steps > 8000 or len(w) > 800:
                return False
            w = prod[w[-1]] + w[:-2]
            steps += 1
            if w and set(w) == {X}:
                if len(w) != target:
                    return False
                break
    return True


def test_uniqueness_small():
    """Продукции длины ≤2 не содержат БББ, поэтому при n≤20 полный перебор пуст.
    Шесть переименований системы жюри при полных продукциях проходят n≤40."""
    from itertools import product

    prods = [""]
    for length in range(1, 3):
        prods += ["".join(t) for t in product("ABV", repeat=length)]
    found = 0
    for a, b, v in product(prods, repeat=3):
        prod = {"A": a, "B": b, "V": v}
        for X in "ABV":
            if _simulates(prod, X, nmax=20):
                found += 1
    assert found == 0
    assert len(nr.renamings()) == 6
    for prod, X in nr.renamings():
        assert _simulates(prod, X, nmax=40)
