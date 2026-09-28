"""Связь с отображением Коллатца T(n) = n/2 (чётн.), (3n+1)/2 (нечётн.)."""
from __future__ import annotations
from typing import List, Tuple
from .core import TASK


def T(n: int) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def collatz_orbit(n: int, limit: int = 10**6) -> List[int]:
    out = [n]
    while out[-1] != 1 and len(out) < limit:
        out.append(T(out[-1]))
    return out


def macro_step(n: int) -> Tuple[int, int]:
    """Б^n -> Б^m: возвращает (m, число шагов). Теорема 3: m=T(n), шагов n (чётн.) / n+1 (нечётн.)."""
    w, k = "B" * n, 0
    while True:
        w = TASK.step(w)
        k += 1
        if w is None:
            raise ValueError("остановка до получения чистого слова")
        if set(w) == {"B"}:
            return len(w), k


def predicted_halting_steps(n: int) -> int:
    """Точная формула числа шагов до остановки слова Б^n (при условии, что орбита Коллатца
    доходит до 1): S(n) = sum_{m in orbit, m != 1} (m + (m mod 2))."""
    return sum(m + (m % 2) for m in collatz_orbit(n) if m != 1)


def family_system(q: int):
    """Семейство A -> Б^q, Б -> АВ, В -> Б  (задача: q = 3)."""
    from .core import TagSystem
    return TagSystem({"A": "B" * q, "B": "AC", "C": "B"})


def T_q(n: int, q: int) -> int:
    """Теорема 3': Б^n -> Б^{T_q(n)},  T_q(n) = n/2 (чётн.), (q n + q - 2)/2 (нечётн.).
    q=3: 3n+1 (Коллатц); q=4: 2n+1 (любое нечётное растёт неограниченно — доказуемо);
    q=5: 5n+3 (эвристически расходится почти всегда). Эвристический дрейф ln-длины за
    макрошаг = ½·ln(q/4): отрицателен только при q < 4, т.е. q=3 — единственный
    нетривиальный «сходящийся» случай."""
    return n // 2 if n % 2 == 0 else (q * n + q - 2) // 2
