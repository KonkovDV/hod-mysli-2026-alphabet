"""σ_k = (фаза 0; (0,9,0,0,0) + (0,5,0,3)^k). Гипотеза: период 20 при k=1, 40+60k при k>=2.
Проверка на run-состояниях (быстро) + сверка со строковой симуляцией для малых k."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tagsys.runs_min import step_state, decode
from tagsys.core_min import make_rules, step
def sigma(k): return (0, (0,9,0,0,0) + (0,5,0,3)*k)
def orbit_period(s, limit=10**7):
    seen = {}; t = 0
    while s is not None and t < limit:
        if s in seen: return t - seen[s], seen[s]
        seen[s] = t; s = step_state(*s); t += 1
    return None, None
def word_period(w, limit=10**6):
    R = make_rules(); seen = {}; t = 0
    while w is not None and t < limit:
        if w in seen: return t - seen[w]
        seen[w] = t; w = step(w, R); t += 1
KMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 150
bad = []
for k in range(1, KMAX+1):
    per, mu = orbit_period(sigma(k))
    exp = 20 if k == 1 else 40 + 60*k
    if per != exp or mu != 0: bad.append((k, per, mu, exp))
    if k <= 12:
        assert word_period(decode(*sigma(k))) == per, k
print(f"k=1..{KMAX}: mismatches={bad}")
# структура для доказательства: длины и число серий вдоль орбиты
for k in (2,3,4):
    s = sigma(k); lens=[]; nr=[]
    per,_ = orbit_period(s)
    for _ in range(per):
        lens.append(sum(s[1])+2*(len(s[1])-1)+s[0]); nr.append(len(s[1])); s = step_state(*s)
    print(k, "period", per, "len range", min(lens), max(lens), "runs range", min(nr), max(nr))
