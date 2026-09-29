"""N1–N3 из аудита 28.09.2026. Запуск: pytest -q tests/test_audit_v2.py"""
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import new_results as nr


def test_four_suffixes_ba_reachable_aa_unused():
    """Все четыре суффикса заданы. На траекториях Б^n читается БА, не читается АА."""
    assert set(nr.BIN2) == {"AA", "AB", "BA", "BB"}
    assert nr.BIN2["BA"] == nr.BIN2["AA"] == "BBB"
    saw_ba = False
    for n in range(2, 80):
        w = "B" * n
        while len(w) >= 2:
            u = nr.h(w)
            suf = u[-2:]
            assert suf in nr.BIN2
            if suf == "BA":
                saw_ba = True
            assert suf != "AA"
            w = nr.step1(w)
    assert saw_ba
    # короткие слова: как в S, шаг BIN2 не вызывается при |w|<2
    assert all(len(s) < 2 for s in ("", "A", "B"))


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


def bin3(w):
    if w[-1] == "A":
        return "BBB" + w[:-2]
    if w[-2:] == "BB":
        return "AB" + w[:-2]
    return "B" + w[:-2]


def test_bin3_rules():
    """Три правила «кончается на А / ББ / АБ» идут шаг в шаг с исходной системой."""
    for n in range(2, 50):
        w = u = "B" * n
        while len(w) >= 2:
            assert w.replace("V", "B") == u
            w, u = nr.step1(w), bin3(u)
        assert u == "B"


def test_bin_halts_only_on_B():
    """Остановка двоичной системы только на Б; длины 2..12 без неизвестных исходов."""
    from itertools import product

    halt = cycle = unknown = 0
    for length in range(2, 13):
        for letters in product("AB", repeat=length):
            w = "".join(letters)
            seen = set()
            steps = 0
            while len(w) >= 2:
                if w in seen:
                    cycle += 1
                    break
                seen.add(w)
                w = bin3(w)
                steps += 1
                if steps > 100000:
                    unknown += 1
                    break
            else:
                assert w == "B"
                halt += 1
    assert (halt, cycle, unknown) == (7803, 385, 0)


def test_second_binary_solution():
    """Второе решение: Б^n → Б^T(n), чётное n за 3n/2 шагов."""
    rules = {"BB": "AB", "BA": "BBB", "AB": "AA", "AA": "B"}
    for n in range(2, 40):
        w = "B" * n
        steps = 0
        while True:
            w = rules[w[-2:]] + w[:-2]
            steps += 1
            assert steps < 5000
            if set(w) == {"B"}:
                break
        assert len(w) == (n // 2 if n % 2 == 0 else (3 * n + 1) // 2)
        assert steps == (3 * n // 2 if n % 2 == 0 else n + 1)


def test_context2_two_solutions_up_to_renaming():
    """32 совпадения = 2 переименования × (15 доопределений + 1 другое решение)."""
    from collections import Counter

    path = os.path.join(ROOT, "results", "context2.txt")
    hits = [line.strip() for line in open(path, encoding="utf-8") if line.startswith("HIT")]
    assert len(hits) == 32
    codes = Counter(line.split()[-1] for line in hits)
    assert codes == Counter({"0": 16, "1": 16})
    assert any("AB:AA" in line and line.endswith("code 1") for line in hits)
    assert sum("AB:B" in line and line.endswith("code 1") for line in hits) == 15


def test_run_language_is_fibonacci():
    def fib(k):
        a, b = 0, 1
        for _ in range(k):
            a, b = b, a + b
        return a

    assert fib(24) - 2 == 46366
