"""Все ключевые утверждения работы в виде тестов. Запуск: pytest -q  (или python tests/test_all.py)."""
import os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tagsys.core import TASK, TASK_PARTIAL, Outcome, reverse_to_classic, de_mol_step
from tagsys.collatz import T, macro_step, predicted_halting_steps
from tagsys.cycles import verify_family, family_word
from tagsys.binary import BLOCK, encode, onehot, cyclic_productions, cyclic_step


def test_isomorphism_with_de_mol():
    """Наша система = система De Mol (2008) после переворота слова и переименования."""
    rnd = random.Random(1)
    for _ in range(2000):
        w = "".join(rnd.choice("ABC") for _ in range(rnd.randint(2, 15)))
        nxt = TASK.step(w)
        assert (None if nxt is None else reverse_to_classic(nxt)) == de_mol_step(reverse_to_classic(w))


def test_dead_letters_lemma():
    """Лемма 1: буквы на чётных местах с конца не влияют на траекторию."""
    rnd = random.Random(2)
    for _ in range(500):
        L = rnd.randint(2, 14)
        w = [rnd.choice("ABC") for _ in range(L)]
        v = list(w)
        for i in range(1, L, 2):           # позиции 2,4,6,... с конца
            v[L - 1 - i] = rnd.choice("ABC")
        r1, r2 = TASK.run("".join(w)), TASK.run("".join(v))
        assert (r1.outcome, r1.period) == (r2.outcome, r2.period)
        if r1.outcome == Outcome.HALT:          # время остановки совпадает точно
            assert r1.steps == r2.steps
        # для циклов момент входа mu может отличаться (исходное слово само может лежать
        # на цикле, а изменённое — нет), но не более чем на ceil(L/2): после этого все
        # исходные буквы стёрты и траектории совпадают буква в букву.
        tw, tv = TASK.trace("".join(w), (L + 1) // 2), TASK.trace("".join(v), (L + 1) // 2)
        assert tw[-1] == tv[-1]


def test_halts_only_on_B():
    """Лемма 2: из длины >= 2 остановка только на «Б»; длина < 2 стоит на себе."""
    for w in ("", "A", "B", "C"):
        r = TASK.run(w)
        assert r.outcome == Outcome.HALT and r.final == w and r.steps == 0
    rnd = random.Random(3)
    for _ in range(3000):
        w = "".join(rnd.choice("ABC") for _ in range(rnd.randint(2, 12)))
        r = TASK.run(w)
        if r.outcome == Outcome.HALT:
            assert r.final == "B"


def test_collatz_macro_step():
    """Теорема 3: Б^n -> Б^T(n) ровно за n (чётн.) / n+1 (нечётн.) шагов."""
    for n in range(2, 400):
        m, k = macro_step(n)
        assert m == T(n) and k == (n if n % 2 == 0 else n + 1)


def test_halting_time_formula():
    for n in list(range(2, 300)) + [27, 97, 871]:
        r = TASK.run("B" * n)
        assert r.outcome == Outcome.HALT and r.steps == predicted_halting_steps(n)
    assert TASK.run("B" * 27).steps == 40656


def test_infinite_cycle_family():
    """Теорема 4: X^k A — цикл периода 4 для всех k."""
    for k in range(1, 60):
        assert verify_family(k)
        r = TASK.run(family_word(k))
        assert r.outcome == Outcome.CYCLE and r.period == 4 and r.steps == 0


def test_partial_convention_gives_collatz_1_2_cycle():
    """Бомба «толкования»: если стирать сколько есть, Б^n уходит в цикл Б <-> АВ (аналог 1 <-> 2)."""
    for n in range(1, 200):
        r = TASK_PARTIAL.run("B" * n)
        assert r.outcome == Outcome.CYCLE and r.period == 2 and r.final in ("B", "AC")


def test_block_binary_simulation():
    rnd = random.Random(4)
    for _ in range(2000):
        w = "".join(rnd.choice("ABC") for _ in range(rnd.randint(2, 12)))
        u = encode(w)
        for _ in range(100):
            w2, u2 = TASK.step(w), BLOCK.step(u)
            if w2 is None:
                assert u2 is None
                break
            assert u2 == encode(w2)
            w, u = w2, u2
    assert BLOCK.run("A" * 54).steps == 40656   # n = 27


def test_cyclic_tag_simulation():
    prods, rnd = cyclic_productions(), random.Random(5)
    for _ in range(1000):
        w = "".join(rnd.choice("ABC") for _ in range(rnd.randint(2, 10)))
        u, k = onehot(w), 0
        for _ in range(60):
            w2 = TASK.step(w)
            if w2 is None:
                break
            for _ in range(6):
                u = cyclic_step(u, k, prods); k += 1
            assert u == onehot(w2)
            w = w2


def test_run_normal_form_bijection_and_step():
    """R1: биекция (фаза, серии) ↔ язык L и совпадение шага с tag-системой, |w|≤20."""
    from tagsys.runs import decode, encode, step_state, step_word, word_len

    def compositions(total, parts):
        if parts == 1:
            yield (total,)
            return
        for i in range(total + 1):
            yield from ((i,) + tail for tail in compositions(total - i, parts - 1))

    seen = 0
    for phase in (0, 1):
        for L in range(phase, 21):
            rest_base = L - phase
            for markers in range(0, rest_base // 2 + 1):
                rest = rest_base - 2 * markers
                for runs in compositions(rest, markers + 1):
                    w = decode(phase, runs)
                    assert len(w) == L == word_len(phase, runs)
                    assert encode(w) == (phase, runs)
                    seen += 1
                    if L < 2:
                        assert step_state(phase, runs) is None
                        continue
                    via_runs = step_word(w)
                    via_tag = TASK.step(w)
                    assert via_runs == via_tag
                    if via_tag is not None:
                        assert encode(via_tag) == step_state(phase, runs)
    assert seen > 1000


def test_run_entry_and_macro_and_second_proof_of_T3():
    """Вход в L за ceil(L/2); макроформула правой серии; Б^n через серии = T."""
    from tagsys.runs import (
        apply_steps, consume_right, decode, encode, enters_normal, in_language,
        pure_collatz_via_runs,
    )
    from tagsys.collatz import T
    rnd = random.Random(7)
    for L in range(2, 13):
        nr = (L + 1) // 2
        for code in range(3 ** nr):
            o = ["B"] * L
            x = code
            for i in range(nr):
                o[L - 1 - 2 * i] = "ABC"[x % 3]
                x //= 3
            w = enters_normal("".join(o))
            assert in_language(w)
    for _ in range(400):
        w = "".join(rnd.choice("ABC") for _ in range(rnd.randint(2, 18)))
        assert in_language(enters_normal(w))
    for phase in (0, 1):
        for n in range(0, 25):
            for m in range(0, 25):
                runs = (n, m)
                if (0 if phase == 0 else 1) + n + m + 2 < 2:
                    continue
                # длина = n+m+2+phase
                got = consume_right(phase, runs)
                if got is None:
                    assert TASK.step(decode(phase, runs)) is None
                    continue
                k, pred = got
                sim = apply_steps(phase, runs, k)
                assert sim == pred, (phase, runs, k, sim, pred)
                # промежуточные шаги не нужны: формула говорит ровно про состояние через k шагов
                w = decode(phase, runs)
                for _ in range(k):
                    w = TASK.step(w)
                assert encode(w) == pred
    for n in range(1, 120):
        m, k = pure_collatz_via_runs(n)
        if n == 1:
            assert (m, k) == (1, 0)
        else:
            assert m == T(n) and k == (n if n % 2 == 0 else n + 1)


def test_run_cycle_family_is_repeated_block():
    """Т4 в координатах серий: (1, (0,1,3)*k) имеет период 4."""
    from tagsys.runs import decode, encode, step_state
    for k in range(1, 30):
        # X^k А, X=АВБАВБББ: серии (0,) + (1, 3)*k, фаза 1
        runs = (0,) + (1, 3) * k
        w = decode(1, runs)
        assert w == ("ACBACBBB" * k) + "A"
        st = (1, runs)
        seen = [st]
        for _ in range(3):
            st = step_state(*st)
            seen.append(st)
        assert step_state(*st) == (1, runs)
        assert len(set(seen)) == 4
        assert encode(w) == (1, runs)


def test_sigma_family_period_law():
    """Семейство σ_k: период 20 при k=1 и 40+60k при 2≤k≤8 (перебор; общая формула — гипотеза)."""
    from tagsys.runs import step_state
    for k in range(1, 9):
        runs = (0, 9, 0, 0, 0) + (0, 5, 0, 3) * k
        expect = 20 if k == 1 else 40 + 60 * k
        st = (0, runs)
        for _ in range(expect - 1):
            st = step_state(*st)
            assert st != (0, runs)
        st = step_state(*st)
        assert st == (0, runs)


def test_max_word_length_is_collatz_maximum():
    """Вдоль Б^n максимум длины равен максимуму орбиты T (следствие разбора макрошага)."""
    from tagsys.collatz import collatz_orbit
    for n in list(range(2, 80)) + [27, 97]:
        assert TASK.run("B" * n).max_len == max(collatz_orbit(n))


def test_family_q():
    """Теорема 3': семейство A -> Б^q даёт T_q(n) = n/2 | (qn+q-2)/2."""
    from tagsys.collatz import family_system, T_q
    for q in range(1, 9):
        ts = family_system(q)
        for n in range(2, 120):
            w = "B" * n
            while True:
                w = ts.step(w)
                if set(w) == {"B"}:
                    break
            assert len(w) == T_q(n, q)
    # q=4: Б^3 растёт неограниченно (3 -> 7 -> 15 -> 31 ...: 2n+1)
    assert T_q(3, 4) == 7 and T_q(7, 4) == 15
    # чётное q>=4: нечётное n переходит в большее нечётное
    for q in (4, 6, 8):
        n = 3
        for _ in range(12):
            m = T_q(n, q)
            assert m % 2 == 1 and m > n
            n = m
    # q=2: нечётное Б^n — цикл периода ровно n+1
    ts2 = family_system(2)
    for n in range(3, 80, 2):
        w0 = "B" * n
        w = w0
        for _ in range(n):
            w = ts2.step(w)
            assert w != w0
        w = ts2.step(w)
        assert w == w0
    # q=1: длина чистого слова строго падает, пока не станет 1
    n = 50
    while n > 1:
        m = T_q(n, 1)
        assert m < n
        n = m


if __name__ == "__main__":
    fns = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for f in fns:
        f(); print("OK ", f.__name__)
    print(f"{len(fns)} тестов пройдено")
