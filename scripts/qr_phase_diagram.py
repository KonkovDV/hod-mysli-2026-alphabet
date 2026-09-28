import sys, os, csv; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tagsys.family_qr import first_return, F
QMAX, RMAX, NMAX = 8, 4, 120
bad = []; rows = []
for q in range(1, QMAX+1):
    for r in range(1, RMAX+1):
        ok = 0
        for n in range(2, NMAX+1):
            got = first_return(n, q, r); exp = F(n, q, r)
            if got != exp: bad.append((q, r, n, got, exp))
            else: ok += 1
        # классификация чистого слоя
        ev = "сжатие" if r == 1 else ("сохранение" if r == 2 else "рост")
        od_num = q*r  # нечётная ветвь ~ (qr/2) n
        od = "сжатие" if od_num < 2 else ("сохранение" if od_num == 2 else "рост")
        rows.append((q, r, ok, ev, od))
os.makedirs("results", exist_ok=True)
with open("results/qr_phase.csv", "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["q","r","n_checked_ok","even_branch","odd_branch"]); wr.writerows(rows)
print("mismatches:", len(bad)); print(bad[:10])
