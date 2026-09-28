"""Бассейны: доля классов длины L, уходящих в остановку и в каждый цикл.
Функциональный граф с мемоизацией на run-состояниях (после входа в язык L).
Цикл канонизируется минимальным словом орбиты (латиница) — как в enum.c / main.rs."""
import sys, os, csv, itertools, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tagsys.runs_min import step_state, decode
from tagsys.core_min import make_rules, step
R = make_rules()
memo = {}  # state -> ("H", steps_to_halt) | ("C", key, steps_to_cycle)
def encode(w):
    ph = 1 if w.endswith("A") else 0
    body = w[:-1] if ph else w
    runs=[]; b=0; i=0
    while i < len(body):
        if body[i]=="B": b+=1; i+=1
        elif body[i:i+2]=="AC": runs.append(b); b=0; i+=2
        else: return None
    runs.append(b); return ph, tuple(runs)
def resolve(s):
    path=[]; idx={}
    while True:
        if s is None: base=("H",-1); break  # состояние без преемника = 0 шагов
        if s in memo: base=memo[s]; break
        if s in idx:  # новый цикл
            cyc = path[idx[s]:]
            key = min(decode(*x) for x in cyc)
            for x in cyc: memo[x]=("C",key,0)
            path = path[:idx[s]]; base=memo[s]; break
        idx[s]=len(path); path.append(s); s=step_state(*s)
    for x in reversed(path):
        if base[0]=="H": base=("H",base[1]+1)
        else: base=("C",base[1],base[2]+1)
        memo[x]=base
    return base
def classify(w):
    t=0
    for _ in range((len(w)+1)//2):
        n=step(w,R)
        if n is None: return ("H",t)
        w=n; t+=1
    s=encode(w); assert s is not None, w
    r=resolve(s)
    return ("H",r[1]+t) if r[0]=="H" else ("C",r[1],r[2]+t)
def write_highlight():
    """Таблица долей бассейна из results/basins.csv: числа не переписываются руками."""
    import csv as _csv
    rows=list(_csv.DictReader(open("results/basins.csv",encoding="utf-8")))
    cyc={r["word_latin"]: r["period"] for r in _csv.DictReader(open("results/cycles.csv",encoding="utf-8"))}
    lines=["| L | цикл, период | классы | доля среди зациклившихся |",
           "|---:|---:|---:|---:|"]
    notes=[]
    for L in (20,22,24):
        items=[]
        for r in rows:
            if int(r["L"])!=L or not r["cycle_key"]:
                continue
            items.append((int(r["cycle_classes"]), r["cycle_key"]))
        items.sort(reverse=True)
        if not items:
            continue
        total=sum(v for v,_ in items)
        for v,k in items[:4]:
            per=cyc.get(k,"?")
            lines.append(f"| {L} | {per} | {v} | {100*v/total:.1f}% |")
        top=items[0]
        t4=sum(v for v,k in items if cyc.get(k)=="4")
        notes.append(
            f"При L={L} зациклившихся классов {total}; "
            f"период {cyc.get(top[1],'?')} собирает {top[0]} ({100*top[0]/total:.1f}%), "
            f"члены периода 4 вместе — {t4}."
        )
    text="\n".join(lines)+"\n\n"+" ".join(notes)+"\n"
    open("results/basins_highlight.md","w",encoding="utf-8").write(text)

LMAX=int(sys.argv[1]) if len(sys.argv)>1 else 20
os.makedirs("results",exist_ok=True)
out=open("results/basins.csv","w",newline=""); wr=csv.writer(out)
en=open(os.environ.get("BASINS_ENUM_OUT","results/enumeration_basins.csv"),"w",newline=""); ew=csv.writer(en); ew.writerow(["L","classes","halt","cycle","unknown","max_steps_to_halt"])
wr.writerow(["L","classes","halt","halt_frac","cycle_key","cycle_classes"])
for L in range(2,LMAX+1):
    nr=(L+1)//2; cnt=collections.Counter(); halt=0; maxh=0
    for code in itertools.product("ABC",repeat=nr):
        w=["B"]*L
        for k,c in enumerate(code): w[L-1-2*k]=c
        r=classify("".join(w))
        if r[0]=="H": halt+=1; maxh=max(maxh,r[1])
        else: cnt[r[1]]+=1
    tot=3**nr
    wr.writerow([L,tot,halt,f"{halt/tot:.4f}","",""])
    for k,v in sorted(cnt.items(), key=lambda x:-x[1]): wr.writerow([L,tot,"","",k,v])
    ew.writerow([L,tot,halt,tot-halt,0,maxh]); en.flush()
    print(L,tot,"halt",halt,"cycle",tot-halt,"maxhalt",maxh,"cycles",len(cnt))
out.close(); en.close()
write_highlight()
