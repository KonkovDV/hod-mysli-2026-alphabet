"""Ядро: 2-tag система из условия и общий класс tag-систем.

Условие (чтение ПОСЛЕДНЕЙ буквы, стирание двух последних, дописывание в НАЧАЛО):
    ...А -> стереть 2, в начало БББ
    ...Б -> стереть 2, в начало АВ
    ...В -> стереть 2, в начало Б
Внутри используем латиницу A,B,C (= А,Б,В), чтобы не путать кириллицу/латиницу в коде.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

ALPHABET_TASK = "ABC"
CYR = str.maketrans("ABC", "АБВ")
LAT = str.maketrans("АБВ", "ABC")


def to_cyr(w: str) -> str:
    return w.translate(CYR)


def to_lat(w: str) -> str:
    return w.translate(LAT)


class Outcome(str, Enum):
    HALT = "halt"        # слово стало короче числа удаления (остановка)
    CYCLE = "cycle"      # состояние повторилось
    UNKNOWN = "unknown"  # превышены лимиты (НЕ означает «растёт бесконечно»!)


@dataclass(frozen=True)
class RunResult:
    outcome: Outcome
    steps: int                 # до остановки / до первого входа в цикл (mu)
    period: int = 0            # lambda для цикла
    final: Optional[str] = None
    max_len: int = 0


class TagSystem:
    """Tag-система «справа налево».

    read: сколько последних букв определяют правило (1 для классической tag-системы;
          2 для блочного двухбуквенного аналога).
    delete: сколько букв стирается с конца.
    halt_mode: 'strict'  — если длина < delete, остановка (толкование по умолчанию);
               'partial' — стираем сколько есть (альтернативное толкование, см. PITFALLS).
    """

    def __init__(self, rules: Dict[str, str], delete: int = 2, read: int = 1,
                 halt_mode: str = "strict"):
        self.rules, self.delete, self.read, self.halt_mode = dict(rules), delete, read, halt_mode

    def step(self, w: str) -> Optional[str]:
        if len(w) < self.read or (self.halt_mode == "strict" and len(w) < self.delete):
            return None
        key = w[-self.read:]
        if key not in self.rules:
            return None
        return self.rules[key] + w[: max(0, len(w) - self.delete)]

    def trace(self, w: str, n: int) -> List[str]:
        out = [w]
        for _ in range(n):
            nxt = self.step(out[-1])
            if nxt is None:
                break
            out.append(nxt)
        return out

    def run(self, w: str, max_steps: int = 10**7, max_len: int = 10**6) -> RunResult:
        """Точный прогон с детекцией цикла алгоритмом Брента (O(1) доп. памяти по словам)."""
        power = lam = 1
        tortoise, hare = w, w
        steps, mlen = 0, len(w)
        while True:
            nxt = self.step(hare)
            if nxt is None:
                return RunResult(Outcome.HALT, steps, 0, hare, mlen)
            hare, steps = nxt, steps + 1
            mlen = max(mlen, len(hare))
            if tortoise == hare:
                # нашли период lam; найдём mu (первый вход в цикл)
                t = h = w
                for _ in range(lam):
                    h = self.step(h)
                mu = 0
                while t != h:
                    t, h, mu = self.step(t), self.step(h), mu + 1
                return RunResult(Outcome.CYCLE, mu, lam, t, mlen)
            if steps > max_steps or len(hare) > max_len:
                return RunResult(Outcome.UNKNOWN, steps, 0, None, mlen)
            if power == lam:
                tortoise, power, lam = hare, power * 2, 0
            lam += 1


TASK = TagSystem({"A": "BBB", "B": "AC", "C": "B"}, delete=2, read=1)
TASK_PARTIAL = TagSystem({"A": "BBB", "B": "AC", "C": "B"}, delete=2, read=1, halt_mode="partial")


def reverse_to_classic(w: str) -> str:
    """Изоморфизм с классической записью Поста/Де Мол: переворот слова и A->c, B->a, C->b.
    Классическая система De Mol (2008): a->bc, b->a, c->aaa (читаем первую, стираем 2, в конец)."""
    return w[::-1].translate(str.maketrans("ABC", "cab"))


DE_MOL = {"a": "bc", "b": "a", "c": "aaa"}


def de_mol_step(u: str) -> Optional[str]:
    if len(u) < 2:
        return None
    return u[2:] + DE_MOL[u[0]]
