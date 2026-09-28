"""Строгая сверка свежего прогона перебора с сохранённым каталогом.
usage: python scripts/check_enum.py GOT.csv EXPECTED.csv LMAX
Проверяет: ровно строки L=2..LMAX без дублей; поля classes/halt/cycle/unknown/max_steps_to_halt;
halt+cycle+unknown == classes == 3^ceil(L/2); unknown == 0; каталог циклов без дублей."""
import csv, os, sys
got_p, exp_p, lmax = sys.argv[1], sys.argv[2], int(sys.argv[3])
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rows(p): return list(csv.DictReader(open(p, encoding="utf-8")))
got, exp = rows(got_p), rows(exp_p)
Ls = [int(r["L"]) for r in got]
if Ls != list(range(2, lmax+1)): sys.exit(f"FAIL: строки L {Ls[:3]}..{Ls[-3:]} != 2..{lmax}")
expd = {int(r["L"]): r for r in exp}
fields = ["classes", "halt", "cycle", "unknown", "max_steps_to_halt"]
for r in got:
    L = int(r["L"]); e = expd.get(L)
    if e is None: sys.exit(f"FAIL: в эталоне нет L={L}")
    for f in fields:
        if f in r and f in e and r[f] != e[f]: sys.exit(f"FAIL L={L} {f}: {r[f]} != {e[f]}")
    c = int(r["classes"])
    if c != 3 ** ((L+1)//2): sys.exit(f"FAIL L={L}: classes != 3^ceil(L/2)")
    if int(r["halt"]) + int(r["cycle"]) + int(r["unknown"]) != c: sys.exit(f"FAIL L={L}: сумма исходов")
    if int(r["unknown"]) != 0: sys.exit(f"FAIL L={L}: unknown>0")
cyc = rows(os.path.join(root, "results", "cycles.csv"))
keys = [r.get("word_latin") or list(r.values())[0] for r in cyc]
if len(set(keys)) != len(keys): sys.exit("FAIL: дубли в cycles.csv")
print(f"OK: L=2..{lmax}, {len(cyc)} циклов в каталоге")
