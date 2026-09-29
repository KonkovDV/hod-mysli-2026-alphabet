"""Двухбуквенные аналоги.

Главный полный ответ на вопрос 3: блочный код.
    Б->AA, А->AB, В->BA; читаем 2 последние, стираем 4.
    Точно симулирует исходную систему шаг-в-шаг на любом слове (гомоморфизм).
    Пара BB не встречается: это не код ни одной буквы.

Частичное сжатие без буквы В (только траектории Б^n): см. scripts/new_results.py,
    четыре суффикса BA, BB, AB, AA.

Циклическая tag-система (Cook, 2004) над {0,1} = {А,Б}: 6 продукций; каждые 6 шагов
    эмулируют 1 шаг исходной системы. Это не классическая tag-система.
"""
from __future__ import annotations
from typing import List, Optional
from .core import TagSystem

ENC = {"B": "AA", "A": "AB", "C": "BA"}
BLOCK = TagSystem({"AA": "ABBA", "AB": "AAAAAA", "BA": "AA"}, delete=4, read=2)


def encode(w: str) -> str:
    return "".join(ENC[c] for c in w)


# --- циклическая tag-система, записанная «справа налево» ---
ONEHOT = {"A": "001", "B": "010", "C": "100"}  # символ -> 3 бита; запись справа налево,
# поэтому первым читается ПРАВЫЙ бит: у А единица на позиции 0 (продукция Q_A), у Б — 1, у В — 2
PRODS_3 = {"A": "BBB", "B": "AC", "C": "B"}


def onehot(w: str) -> str:
    return "".join(ONEHOT[c] for c in w)


def cyclic_productions() -> List[str]:
    """(Q_A, Q_B, Q_C, '', '', '') где Q_x = onehot(P(x)).  m*n = 2*3 = 6 продукций."""
    return [onehot(PRODS_3[c]) for c in "ABC"] + ["", "", ""]


def cyclic_step(w: str, k: int, prods: List[str]) -> Optional[str]:
    """Шаг k: читаем последний бит; если 1 — дописываем в начало prods[k mod 6]; стираем последний бит."""
    if not w:
        return None
    p = prods[k % len(prods)] if w[-1] == "1" else ""
    return p + w[:-1]
