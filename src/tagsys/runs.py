"""Нормальная форма tag-системы: фаза и длины серий Б.

После не более чем ceil(|w|/2) шагов любое слово (если процесс не остановился раньше)
лежит в языке L = L0 ∪ L1 и больше из него не выходит.

  L0:  Б^{n0} (АВ Б^{n1}) ... (АВ Б^{nk})     — фаза 0
  L1:  (слово из L0) + А                      — фаза 1

Код внутри — латиница: Б=B, А=A, В=C, маркер «АВ» = AC.

Состояние (phase, runs), runs = (n0, ..., nk), ni ≥ 0, взаимно однозначно с L.
Один шаг системы на L задаётся правилами R1–R5 (доказаны разбором последних букв;
проверка на всех словах L длины ≤ 20 — tests/test_all.py).
"""
from __future__ import annotations
from typing import List, Optional, Sequence, Tuple

from .core import TASK

State = Tuple[int, Tuple[int, ...]]


def word_len(phase: int, runs: Sequence[int]) -> int:
    if not runs:
        raise ValueError("пустой вектор серий")
    return sum(runs) + 2 * (len(runs) - 1) + phase


def decode(phase: int, runs: Sequence[int]) -> str:
    """(фаза, серии) → слово. Обратная к encode на языке L."""
    if phase not in (0, 1):
        raise ValueError(phase)
    if len(runs) == 0:
        raise ValueError("пустой вектор серий")
    if any(n < 0 for n in runs):
        raise ValueError(runs)
    parts = ["B" * runs[0]]
    for n in runs[1:]:
        parts.append("AC")
        parts.append("B" * n)
    w = "".join(parts)
    if phase == 1:
        w += "A"
    return w


def encode(w: str) -> Optional[State]:
    """Слово языка L → (фаза, серии). Иначе None.

    Фаза 1 тогда и только тогда, когда слово оканчивается на одиночную А,
    не входящую в маркер AC. Разбиение по маркеру AC единственно.
    """
    if w.endswith("A"):
        phase = 1
        body = w[:-1]
    else:
        phase = 0
        body = w
    # body должен принадлежать L0 = B*(AC B*)*
    i, n = 0, len(body)
    runs: List[int] = []
    bcount = 0
    started = False
    while i < n:
        if body[i] == "B":
            bcount += 1
            i += 1
            continue
        if body[i:i + 2] == "AC":
            runs.append(bcount)
            bcount = 0
            started = True
            i += 2
            continue
        return None
    runs.append(bcount)
    if not started and not runs:
        runs = [0]
    return phase, tuple(runs)


def in_language(w: str) -> bool:
    return encode(w) is not None


def step_state(phase: int, runs: Sequence[int]) -> Optional[State]:
    """Один шаг на состоянии. None — остановка (длина слова < 2).

    R1. φ=0, nk≥2:        (0, 0, n0, ..., nk-2)
    R2. φ=0, nk=1, k≥1:   (1, 0, n0, ..., n_{k-1})
    R3. φ=0, nk=0, k≥1:   (0, n0+1, n1, ..., n_{k-1})
    R4. φ=1, nk≥1:        k=0 → (0, n0+2);  k≥1 → (0, n0+3, ..., nk-1)
    R5. φ=1, nk=0, k≥1:   (1, n0+3, n1, ..., n_{k-1})
    """
    r = list(runs)
    if not r:
        raise ValueError("пустой вектор серий")
    if word_len(phase, r) < 2:
        return None
    k = len(r) - 1
    nk = r[-1]
    if phase == 0:
        if nk >= 2:
            return 0, tuple([0] + r[:-1] + [nk - 2])
        if nk == 1:
            # слово «Б»: k=0, n0=1
            if k == 0:
                return None
            return 1, tuple([0] + r[:-1])
        # nk == 0, слово кончается на AC
        return 0, tuple([r[0] + 1] + r[1:-1])
    # phase == 1
    if nk >= 1:
        if k == 0:
            return 0, (r[0] + 2,)
        return 0, tuple([r[0] + 3] + r[1:-1] + [nk - 1])
    return 1, tuple([r[0] + 3] + r[1:-1])


def step_word(w: str) -> Optional[str]:
    """Шаг, записанный на словах языка L. Совпадает с TASK.step."""
    st = encode(w)
    if st is None:
        raise ValueError("слово не в L: " + w)
    nxt = step_state(*st)
    if nxt is None:
        return None
    return decode(*nxt)


def consume_right(phase: int, runs: Sequence[int]) -> Optional[Tuple[int, State]]:
    """Съесть правую серию: замкнутая формула макрошага.

    Возвращает (число шагов, новое состояние) либо None, если слово уже короче 2.
    Правая серия m = runs[-1], левый список R = runs[:-1] (может быть пуст,
    тогда состояние — одна серия).

    Фаза 0, m = 2t, t≥1:  за t+1 шагов → (0, (1, 0, ..., 0) + R)  с (t-1) нулями.
    Фаза 0, m = 2t+1 ≥ 3, либо m=1 и R непуст:
                          за t+1 шагов → (1, (0, ..., 0) + R) с (t+1) нулями.
    Фаза 0, m = 0:        за 1 шаг    → (0, (R[0]+1, R[1], ...))
    Фаза 1, m ≥ 1, R пуст: за 1 шаг   → (0, (m+2,))
    Фаза 1, m ≥ 1, R непуст: за 1 шаг → (0, (R[0]+3, ..., m-1))
    Фаза 1, m = 0:        за 1 шаг    → (1, (R[0]+3, R[1], ...))
    """
    r = tuple(runs)
    if word_len(phase, r) < 2:
        return None
    if phase == 0:
        m = r[-1]
        R = r[:-1]
        if m == 0:
            return 1, (0, (R[0] + 1,) + R[1:])
        if m % 2 == 0:
            t = m // 2
            return t + 1, (0, (1,) + (0,) * (t - 1) + R)
        t = m // 2
        if m == 1 and len(R) == 0:
            return None
        return t + 1, (1, (0,) * (t + 1) + R)
    m = r[-1]
    R = r[:-1]
    if m >= 1:
        if len(R) == 0:
            return 1, (0, (m + 2,))
        return 1, (0, (R[0] + 3,) + R[1:] + (m - 1,))
    return 1, (1, (R[0] + 3,) + R[1:])


def apply_steps(phase: int, runs: Sequence[int], steps: int) -> Optional[State]:
    st: Optional[State] = (phase, tuple(runs))
    for _ in range(steps):
        if st is None:
            return None
        st = step_state(*st)
    return st


def enters_normal(w: str) -> str:
    """Слово через не более ceil(|w|/2) шагов: оно уже в L (для |w|≥2).

    Если процесс остановился раньше, возвращается слово остановки.
    """
    steps = (len(w) + 1) // 2
    cur = w
    for _ in range(steps):
        nxt = TASK.step(cur)
        if nxt is None:
            return cur
        cur = nxt
    return cur


def pure_collatz_via_runs(n: int) -> Tuple[int, int]:
    """Второе вычисление макрошага Б^n через правила серий.

    Возвращает (длина чистого слова Б, число шагов). Для n=1 остановка: (1, 0).
    """
    if n < 1:
        raise ValueError(n)
    if n == 1:
        return 1, 0
    phase, runs = 0, (n,)
    steps = 0
    # крутимся, пока не получим фазу 0 и одну серию (чистое Б^m), но не раньше
    # чем сделан хотя бы один макропроход; практически — пока не вернёмся к одной серии фазы 0
    seen_start = True
    for _ in range(n + 5):
        got = consume_right(phase, runs)
        if got is None:
            return runs[0] if phase == 0 and len(runs) == 1 else -1, steps
        k, (phase, runs) = got
        steps += k
        if phase == 0 and len(runs) == 1 and not seen_start:
            return runs[0], steps
        seen_start = False
        # после первого consume чётного n мы ещё не в одной серии, если t>1
        if phase == 0 and len(runs) == 1:
            return runs[0], steps
        # фаза 1, одна серия: ещё один шаг правила R4 доводит до чистого Б
        if phase == 1 and len(runs) == 1:
            nxt = step_state(phase, runs)
            if nxt is None:
                break
            phase, runs = nxt
            steps += 1
            if phase == 0 and len(runs) == 1:
                return runs[0], steps
    raise RuntimeError(f"не свернулось: n={n} state={(phase, runs)} steps={steps}")
