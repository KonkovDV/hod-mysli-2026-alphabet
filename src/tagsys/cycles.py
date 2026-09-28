"""Бесконечное семейство циклов (теорема 4) и утилиты."""
from .core import TASK

X = "ACBACBBB"          # АВБАВБББ


def family_word(k: int) -> str:
    """X^k A  — цикл периода 4 для любого k>=1."""
    return X * k + "A"


def verify_family(k: int) -> bool:
    w = family_word(k)
    tr = TASK.trace(w, 4)
    return len(tr) == 5 and tr[4] == w and len(set(tr[:4])) == 4


def canonical_cycle(w: str, period: int) -> str:
    """Каноническое имя цикла: лексикографический минимум по орбите."""
    best, cur = w, w
    for _ in range(period - 1):
        cur = TASK.step(cur)
        best = min(best, cur)
    return best
