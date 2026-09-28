"""Двухпараметрическое семейство A->B^q, B->(AC)^r, C->B (А->Б^q, Б->(АВ)^r, В->Б).
Гипотеза (проверяется здесь, доказывается индукцией в paper):
  для n>=2 первое возвращение Б^n к чистому слову Б^m даёт
    m = r*n/2             (n чётно)
    m = (q*r*n+q*r-2)/2   (n нечётно)
  за (r+1)*ceil(n/2) микрошагов (при r=1: n и n+1, как в теореме 3).
  ВНИМАНИЕ: формула шагов r*n / r*(n+1), предложенная ИИ-ассистентом, НЕВЕРНА при r>=2
  (опровергнута этим скриптом) -- хороший пример для раздела об ошибках ИИ.
"""
from .core_min import make_rules, step

def first_return(n, q, r, max_steps=10**6):
    rules = make_rules(q, r); w = "B"*n
    for s in range(1, max_steps+1):
        w = step(w, rules)
        if w is None: return None
        if w and set(w) == {"B"}: return len(w), s
    raise RuntimeError("no return")

def F(n, q, r):
    steps = (r+1)*((n+1)//2)
    if n % 2 == 0: return r*n//2, steps
    return (q*r*n + q*r - 2)//2, steps
