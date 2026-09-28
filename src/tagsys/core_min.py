"""Минимальное ядро (копия семантики core.TASK) для автономных скриптов red-team пакета."""
def make_rules(q=3, r=1):
    return {"A": "B"*q, "B": "AC"*r, "C": "B"}
def step(w, rules, delete=2):
    if len(w) < delete: return None
    return rules[w[-1]] + w[:-delete]
