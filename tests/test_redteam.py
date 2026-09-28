"""Тесты red-team пакета. Запуск: pytest -q tests/test_redteam.py"""
import sys, os, subprocess
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from tagsys.family_qr import first_return, F
from tagsys.core_min import make_rules, step
from tagsys.runs_min import step_state, decode

def test_qr_macro_law():
    for q in range(1, 7):
        for r in range(1, 4):
            for n in range(2, 60):
                assert first_return(n, q, r) == F(n, q, r), (q, r, n)

def test_qr_reduces_to_theorem3_at_r1_q3():
    for n in range(2, 200):
        m, s = F(n, 3, 1)
        assert m == (n//2 if n % 2 == 0 else (3*n+1)//2)
        assert s == (n if n % 2 == 0 else n+1)

def test_sigma_law_k_le_40():
    def per(s):
        seen = {}; t = 0
        while s not in seen:
            seen[s] = t; s = step_state(*s); t += 1
        return t - seen[s], seen[s]
    for k in range(1, 41):
        p, mu = per((0, (0,9,0,0,0) + (0,5,0,3)*k))
        assert mu == 0 and p == (20 if k == 1 else 40 + 60*k), k

def _encode(w):
    ph = 1 if w.endswith("A") else 0
    body = w[:-1] if ph else w
    runs=[]; b=0; i=0
    while i < len(body):
        if body[i]=="B": b+=1; i+=1
        elif body[i:i+2]=="AC": runs.append(b); b=0; i+=2
        else: return None
    runs.append(b); return ph, tuple(runs)

def test_runs_rules_match_words():
    import itertools
    R = make_rules()
    for L in range(2, 13):
        for code in itertools.product("ABC", repeat=(L+1)//2):
            w = ["B"]*L
            for k, c in enumerate(code): w[L-1-2*k] = c
            w = "".join(w)
            for _ in range((L+1)//2):
                w = step(w, R)
                if w is None: break
            if w is None: continue
            s = _encode(w); assert s is not None, w       # вход в язык L за ceil(L/2) шагов
            for _ in range(40):
                w2 = step(w, R); s2 = step_state(*s)
                if w2 is None: assert s2 is None; break
                assert decode(*s2) == w2
                w, s = w2, s2

def test_basins_match_enumeration():
    """Третья, независимая реализация (мемоизация на run-состояниях) против results/enumeration.csv."""
    import csv
    path = os.path.join(ROOT, "results", "enumeration.csv")
    if not os.path.exists(path): return
    out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "basins.py"), "16"],
                         capture_output=True, text=True, cwd=ROOT, check=True).stdout.split("\n")
    mine = {int(l.split()[0]): l.split() for l in out if l.strip()}
    for row in csv.DictReader(open(path, encoding="utf-8")):
        L = int(row["L"])
        if L in mine:
            f = mine[L]
            assert int(f[3]) == int(row["halt"]) and int(f[5]) == int(row["cycle"]), L
