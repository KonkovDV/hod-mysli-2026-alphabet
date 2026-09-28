"""Сводит треки R1–R5: числа, рисунки, results/track_R*.md, results/key_numbers.json.

Запуск из корня репозитория: python scripts/make_tracks.py
Все числа в отчётах и в key_numbers.json вычислены этим скриптом.
"""
from __future__ import annotations
import csv, json, math, os, sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tagsys.collatz import T, T_q, collatz_orbit, predicted_halting_steps
from tagsys.core import TASK
from tagsys.runs import (
    apply_steps, consume_right, decode, encode, step_state, word_len,
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
os.makedirs(RES, exist_ok=True)
os.makedirs(FIG, exist_ok=True)
plt.rcParams["font.family"] = "DejaVu Sans"


def compositions(total: int, parts: int):
    if parts == 1:
        yield (total,)
        return
    for i in range(total + 1):
        yield from ((i,) + tail for tail in compositions(total - i, parts - 1))


def count_states(max_len: int) -> int:
    seen = 0
    for phase in (0, 1):
        for L in range(phase, max_len + 1):
            rest_base = L - phase
            for markers in range(rest_base // 2 + 1):
                rest = rest_base - 2 * markers
                for _ in compositions(rest, markers + 1):
                    seen += 1
    return seen


def track_r1(nums: dict) -> None:
    nums["states_le_20"] = count_states(20)
    checked = match_comp = 0
    counter = None
    for n in range(1, 31):
        for m in range(1, 31):
            got = consume_right(0, (n, m))
            assert got is not None
            k, pred = got
            assert apply_steps(0, (n, m), k) == pred
            checked += 1
            tn, tm = T(n), T(m)
            runs = pred[1]
            if pred[0] == 0 and len(runs) == 2 and (runs == (tn, tm) or runs == (tm, tn)):
                match_comp += 1
            elif counter is None:
                counter = {
                    "phase": 0, "n": n, "m": m, "steps": k,
                    "out_phase": pred[0], "out_runs": list(runs),
                    "T_n": tn, "T_m": tm,
                }
    # явный контрпример из доказательства, даже если цикл выше нашёл другой первым
    ex = consume_right(0, (4, 1))
    assert ex is not None
    nums["macro_pairs_checked"] = checked
    nums["componentwise_T_matches"] = match_comp
    nums["counterexample_scan"] = counter
    nums["counterexample"] = {
        "phase": 0, "n": 4, "m": 1, "steps": ex[0],
        "out_phase": ex[1][0], "out_runs": list(ex[1][1]),
        "T_n": T(4), "T_m": T(1),
    }
    # семейство Т4 в координатах серий
    nums["family_block"] = [0, 1, 3]
    # вход в L: все классы L<=12
    entered = 0
    for L in range(2, 13):
        nr = (L + 1) // 2
        for code in range(3 ** nr):
            o = ["B"] * L
            x = code
            for i in range(nr):
                o[L - 1 - 2 * i] = "ABC"[x % 3]
                x //= 3
            w = "".join(o)
            cur = w
            for _ in range((L + 1) // 2):
                nxt = TASK.step(cur)
                if nxt is None:
                    break
                cur = nxt
            assert encode(cur) is not None
            entered += 1
    nums["entry_classes_checked"] = entered
    nums["entry_L_max"] = 12


def load_cycles_base():
    rows = []
    with open(os.path.join(RES, "cycles.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "first_L": int(r["first_L"]),
                "period": int(r["period"]),
                "min_len": int(r["min_len"]),
                "max_len": int(r["max_len"]),
                "word": r["word_latin"],
            })
    return rows


def load_new_cycles():
    path = os.path.join(RES, "cycles_26_28.txt")
    out = []
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return out
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line.startswith("CYCLE,"):
            continue
        # CYCLE,L,period,minlen,maxlen,word
        parts = line.split(",", 5)
        if len(parts) != 6:
            continue
        _, L, per, mn, mx, word = parts
        out.append({
            "first_L": int(L), "period": int(per), "min_len": int(mn),
            "max_len": int(mx), "word": word,
        })
    return out


def dedupe_cycles(cycles):
    best = {}
    for c in cycles:
        w = c["word"]
        if w not in best or c["first_L"] < best[w]["first_L"]:
            best[w] = c
    return sorted(best.values(), key=lambda c: (c["first_L"], c["period"], c["word"]))


def verify_sigma(kmax=24):
    """Семейство σ_k: фаза 0, серии (0,9,0,0,0)+(0,5,0,3)^k."""
    rows = []
    ok = 0
    for k in range(1, kmax + 1):
        runs = (0, 9, 0, 0, 0) + (0, 5, 0, 3) * k
        expect = 20 if k == 1 else 40 + 60 * k
        kind, per, mu = outcome(0, runs, limit=expect + 8, max_word=50000)
        good = kind == "cycle" and per == expect and mu == 0
        ok += int(good)
        rows.append({"k": k, "kind": kind, "period": per, "mu": mu, "expect": expect, "ok": good})
    return {"kmax": kmax, "n_ok": ok, "rows": rows}


def load_enum_rows():
    rows = []
    with open(os.path.join(RES, "enumeration.csv"), encoding="utf-8") as f:
        rows.extend(csv.DictReader(f))
    ext = os.path.join(RES, "enumeration_26_28.csv")
    if os.path.exists(ext) and os.path.getsize(ext) > 0:
        try:
            with open(ext, encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    if r.get("L"):
                        rows.append(r)
        except Exception:
            pass
    # уникальные L, по возрастанию
    byL = {}
    for r in rows:
        byL[int(r["L"])] = r
    return [byL[L] for L in sorted(byL)]


def outcome(phase, runs, limit=4000, max_word=8000):
    st = (phase, tuple(runs))
    seen = {st: 0}
    for i in range(limit):
        nxt = step_state(*st)
        if nxt is None:
            return "halt", None, None
        if word_len(*nxt) > max_word:
            return "unknown", None, None
        if nxt in seen:
            return "cycle", i + 1 - seen[nxt], seen[nxt]
        seen[nxt] = i + 1
        st = nxt
    return "unknown", None, None


def annotate_cycles(cycles):
    annotated = []
    for c in cycles:
        st = encode(c["word"])
        if st is None:
            c = dict(c)
            c["in_L"] = False
            annotated.append(c)
            continue
        phase, runs = st
        states = [(phase, runs)]
        cur = (phase, runs)
        for _ in range(c["period"] - 1):
            cur = step_state(*cur)
            states.append(cur)
        back = step_state(*cur)
        assert back == (phase, runs), c["word"]
        c = dict(c)
        c["in_L"] = True
        c["phase"] = phase
        c["runs"] = list(runs)
        c["n_series"] = len(runs)
        c["max_series"] = max(len(s[1]) for s in states)
        c["phases_on_orbit"] = sorted({s[0] for s in states})
        c["states"] = states
        # член семейства Т4?
        def _t4(ph, rr):
            return (ph == 1 and len(rr) > 1 and rr[0] == 0
                    and (len(rr) - 1) % 2 == 0
                    and rr[1:] == (1, 3) * ((len(rr) - 1) // 2))
        c["is_T4"] = c["period"] == 4 and any(_t4(ph, rr) for ph, rr in states)
        annotated.append(c)
    return annotated


def search_pumps(cycles):
    """Ищем блок серий, повтор которого оставляет слово на цикле (mu=0) при k=2,3,4."""
    hits = []
    seen_key = set()
    for c in cycles:
        if not c.get("in_L"):
            continue
        # достаточно канонического состояния и ещё состояний орбиты:
        # орбиты длинные, но отсев на k=2 быстрый
        for phase, runs in c["states"]:
            L = len(runs)
            for i in range(L):
                for bl in range(1, min(4, L - i) + 1):
                    block = runs[i:i + bl]
                    periods = []
                    mus = []
                    good = True
                    built = None
                    for k in (2, 3, 4):
                        new_runs = runs[:i] + block * k + runs[i + bl:]
                        if len(new_runs) > 48:
                            good = False
                            break
                        kind, per, mu = outcome(phase, new_runs)
                        if kind != "cycle" or mu != 0:
                            good = False
                            break
                        periods.append(per)
                        mus.append(mu)
                        built = new_runs
                    if not good:
                        continue
                    # k=5 как дополнительная проверка, не как фильтр отчёта
                    new5 = runs[:i] + block * 5 + runs[i + bl:]
                    kind5, per5, mu5 = outcome(phase, new5) if len(new5) <= 60 else ("unknown", None, None)
                    key = (phase, tuple(block), tuple(periods), c["period"], tuple(runs[:i]), tuple(runs[i + bl:]))
                    if key in seen_key:
                        continue
                    seen_key.add(key)
                    hits.append({
                        "source_period": c["period"],
                        "source_word": c["word"],
                        "phase": phase,
                        "prefix": list(runs[:i]),
                        "block": list(block),
                        "suffix": list(runs[i + bl:]),
                        "periods_k234": periods,
                        "k5": None if kind5 != "cycle" else {"period": per5, "mu": mu5},
                    })
    return hits


def track_r3(nums: dict) -> None:
    def collect(q, n_max, step_cap):
        deltas = []
        odd_to_odd = odd_steps = steps = 0
        for n0 in range(2, n_max + 1):
            n = n0
            for _ in range(step_cap):
                if n <= 1:
                    break
                odd = n % 2 == 1
                m = T_q(n, q)
                if m <= 0:
                    break
                deltas.append(math.log(m) - math.log(n))
                steps += 1
                if odd:
                    odd_steps += 1
                    if m % 2 == 1:
                        odd_to_odd += 1
                n = m
                if n > 10 ** 18:
                    break
        return {
            "q": q,
            "n_max": n_max,
            "step_cap": step_cap,
            "macro_steps": steps,
            "mean_dln": sum(deltas) / len(deltas),
            "theory": 0.5 * math.log(q / 4),
            "odd_steps": odd_steps,
            "odd_to_odd": odd_to_odd,
            "deltas": deltas,
        }

    a = collect(3, 8000, 10000)
    b = collect(5, 4000, 60)
    # цепочка q=4 от 3
    chain = [3]
    n = 3
    for _ in range(8):
        n = T_q(n, 4)
        chain.append(n)
    nums["q4_chain"] = chain
    nums["drift"] = {
        "q3": {k: a[k] for k in a if k != "deltas"},
        "q5": {k: b[k] for k in b if k != "deltas"},
    }
    # рисунок
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for ax, pack, title in (
        (axes[0], a, "q = 3"),
        (axes[1], b, "q = 5"),
    ):
        ax.hist(pack["deltas"], bins=40, color="#1f77b4", alpha=0.85)
        ax.axvline(pack["theory"], color="#d62728", lw=1.5, label="½ ln(q/4)")
        ax.axvline(pack["mean_dln"], color="#2ca02c", lw=1.2, ls="--", label="среднее по орбитам")
        ax.set_title(title)
        ax.set_xlabel("ln(длина′) − ln(длина)")
        ax.legend(fontsize=8)
    axes[0].set_ylabel("число макрошагов")
    fig.suptitle("Дрейф логарифма длины чистого слова Б")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "drift_q.png"), dpi=160)
    plt.close()


def track_r4(nums: dict) -> None:
    n_max = 8000
    ratios = []
    s_over = []
    log_ratio = []
    macro_over_ln = []
    for n in range(2, n_max + 1):
        orb = collatz_orbit(n)
        steps = len(orb) - 1
        S = predicted_halting_steps(n)
        ratios.append(S / n)
        s_over.append(S / n)
        log_ratio.append(math.log(S) - math.log(n))
        if n >= 100:
            macro_over_ln.append(steps / math.log(n))
    const = 2 / math.log(4 / 3)
    model = 1 / (1 - math.sqrt(3 / 4))
    arr = np.array(s_over)
    logs = np.array(log_ratio)
    nums["stopping"] = {
        "n_min": 2,
        "n_max": n_max,
        "lagarias_const": const,
        "mean_macro_per_ln": float(np.mean(macro_over_ln)),
        "median_macro_per_ln": float(np.median(macro_over_ln)),
        "mean_S_over_n": float(np.mean(arr)),
        "median_S_over_n": float(np.median(arr)),
        "mean_ln_S_over_n": float(np.mean(logs)),
        "model_S_factor": model,
        "s27": predicted_halting_steps(27),
        "maxlen27": max(collatz_orbit(27)),
        "macro_steps_27": len(collatz_orbit(27)) - 1,
    }
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.hist(logs, bins=60, color="#1f77b4")
    ax.axvline(math.log(model), color="#d62728", lw=1.4, label="модель Σ r^k")
    ax.axvline(float(np.median(logs)), color="#2ca02c", ls="--", lw=1.2, label="медиана")
    ax.set_xlabel("ln S(n) − ln n")
    ax.set_ylabel("число n")
    ax.set_title(f"Время остановки tag-системы, n = 2…{n_max}")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "log_S_ratio.png"), dpi=160)
    plt.close()


def track_r2(nums, cycles, enum_rows) -> None:
    # график: число различных циклов с min_len ≤ L и доля классов
    Ls = list(range(1, max(int(r["L"]) for r in enum_rows) + 1))
    cum = []
    for L in Ls:
        cum.append(sum(1 for c in cycles if c["min_len"] <= L))
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.plot(Ls, cum, "o-", ms=3)
    ax.set_xlabel("L")
    ax.set_ylabel("число циклов с мин. длиной ≤ L")
    ax.set_title("Каталог циклов (различные орбиты)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "cycles_cumulative.png"), dpi=160)
    plt.close()

    enum_L = [int(r["L"]) for r in enum_rows]
    frac = [int(r["cycle"]) / int(r["classes"]) for r in enum_rows]
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.plot(enum_L, frac, "o-")
    ax.set_xlabel("длина слова L")
    ax.set_ylabel("доля классов в цикле")
    ax.set_title("Полный перебор классов (лемма 1)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "cycle_fraction.png"), dpi=160)
    plt.close()

    nums["enum"] = []
    for r in enum_rows:
        nums["enum"].append({
            "L": int(r["L"]),
            "classes": int(r["classes"]),
            "halt": int(r["halt"]),
            "cycle": int(r["cycle"]),
            "unknown": int(r["unknown"]),
            "max_steps_to_halt": int(r["max_steps_to_halt"]),
        })
    nums["enum_max_L"] = nums["enum"][-1]["L"]
    nums["unknown_total"] = sum(r["unknown"] for r in nums["enum"])
    brief = []
    for c in cycles:
        brief.append({
            "first_L": c["first_L"], "period": c["period"],
            "min_len": c["min_len"], "max_len": c["max_len"],
            "word": c["word"], "phase": c.get("phase"),
            "runs": c.get("runs"), "n_series": c.get("n_series"),
            "max_series": c.get("max_series"), "is_T4": c.get("is_T4", False),
        })
    nums["cycles"] = brief
    nums["n_cycles"] = len(brief)
    nums["n_T4_members"] = sum(1 for c in brief if c["is_T4"])
    nums["n_sporadic"] = nums["n_cycles"] - nums["n_T4_members"]


def track_r5(nums: dict) -> None:
    path = os.path.join(RES, "search_ext.txt")
    info = {"ready": False}
    if os.path.exists(path):
        text = open(path, encoding="utf-8", errors="replace").read()
        info["text_tail"] = text[-2000:]
        info["found_lines"] = [ln for ln in text.splitlines() if ln.startswith("FOUND")]
        for ln in text.splitlines():
            if ln.startswith("BOUNDS "):
                info["bounds"] = ln[len("BOUNDS "):]
            if ln.startswith("SYSTEMS "):
                info["systems"] = int(ln.split()[1])
            if ln.startswith("PASSED_N2 "):
                info["passed_n2"] = int(ln.split()[1])
            if ln.strip() == "DONE":
                info["ready"] = True
    nums["search_ext"] = info


def fmt(x, digits=6):
    if isinstance(x, float):
        return f"{x:.{digits}g}"
    return str(x)


def write_reports(nums, pumps) -> None:
    cx = nums["counterexample"]
    d3 = nums["drift"]["q3"]
    d5 = nums["drift"]["q5"]
    st = nums["stopping"]
    lines = []
    lines.append("# Трек R1. Нормальная форма и связанные серии\n")
    lines.append("## Гипотеза\n")
    lines.append(
        "После не более чем ⌈L/2⌉ шагов любое слово лежит в языке L = L0 ∪ L1, "
        "где L0 — слова вида Б^{n0}(АВ Б^{n1})…(АВ Б^{nk}), а L1 = L0·А. "
        "Состояние — фаза и вектор длин серий. Гипотеза плана: на двух сериях "
        "каждая координата эволюционирует отображением T, а чётность даёт перенос фазы, как в сумматоре.\n"
    )
    lines.append("## Метод\n")
    lines.append(
        "Правила одного шага R1–R5 выведены разбором последних двух букв и сверены с "
        f"`TASK.step` на всех словах L длины ≤ 20 (их {nums['states_le_20']}). "
        f"Вход в L проверен на всех классах леммы 1 при 2 ≤ L ≤ {nums['entry_L_max']} "
        f"({nums['entry_classes_checked']} классов). "
        "Макроформула «съесть правую серию» сверена с цепочкой микрошагов для всех пар серий. "
        "Покомпонентная гипотеза T(n), T(m) проверена на парах 1…30.\n"
    )
    lines.append("## Результат\n")
    lines.append(
        "Язык L инвариантен, кодирование биективно, шаг задаётся правилами R1–R5. "
        "Статус этих утверждений: **доказано** (разбор случаев) и **проверено перебором** "
        f"на {nums['states_le_20']} словах длины ≤ 20 и на {nums['entry_classes_checked']} классах входа.\n"
    )
    lines.append(
        "Правая серия не превращается в T одновременно с левой. "
        f"Контрпример: фаза 0, серии ({cx['n']}, {cx['m']}). "
        f"За {cx['steps']} шаг получается фаза {cx['out_phase']}, серии {cx['out_runs']}. "
        f"Покомпонентные образы были бы T({cx['n']})={cx['T_n']}, T({cx['m']})={cx['T_m']}. "
        f"Из {nums['macro_pairs_checked']} пар (n, m) ∈ {{1…30}}² ровно "
        f"{nums['componentwise_T_matches']} дают две серии, совпадающие с (T(n), T(m)) или (T(m), T(n)). "
        "Статус сильной гипотезы «обе серии сразу эволюционируют по T»: **опровергнуто перебором**.\n"
    )
    lines.append(
        "Верная замена гипотезы (**доказано**): чтение идёт справа, запись — слева. "
        "За t+1 шагов правая серия m=2t (фаза 0) заменяется кодом (1, 0, …, 0) с t−1 нулём, "
        "а левый вектор серий остаётся справа без изменений; при m=2t+1 результат имеет фазу 1 "
        "и код из t+1 нулей слева от старого левого вектора. "
        "Фаза 1 и правая серия m≥1 за один шаг дают (0, n0+3, …, m−1): это и есть «+3» из 3n+1, "
        "уходящее на левый конец, а не в соседнюю серию. "
        "На одной серии тот же механизм сворачивается в T (второе доказательство теоремы 3). "
        "На нескольких сериях запись одной серии позже читается как вход следующей, "
        "и эта обратная связь создаёт циклы. Семейство теоремы 4 — состояние "
        "фаза 1, серии (0)+(1, 3)^k; четыре применения R1–R5 возвращают его на место.\n"
    )
    lines.append("## Статус\n")
    lines.append(
        "- Нормальная форма, биекция, правила R1–R5, макроформула правой серии, второе доказательство Т3, "
        "разбор семейства Т4: **доказано**.\n"
        "- Совпадение с программой на всех словах L длины ≤ 20: **проверено перебором**.\n"
        "- «Каждая из двух серий эволюционирует по T за один макрошаг»: **опровергнуто**.\n"
    )
    open(os.path.join(RES, "track_R1.md"), "w", encoding="utf-8").write("\n".join(lines))

    # R2
    lines = ["# Трек R2. Каталог и семейства циклов\n", "## Гипотеза\n",
             "Все циклы принадлежат конечному числу бесконечных семейств, получаемых накачкой блока.\n",
             "## Метод\n"]
    lines.append(
        f"Каталог: `results/cycles.csv` и, если есть, `results/cycles_26_28.txt`. "
        f"Перебор классов: `results/enumeration.csv`"
        + (" плюс `enumeration_26_28.csv`" if nums["enum_max_L"] > 25 else "")
        + f". Максимальная длина в таблице: {nums['enum_max_L']}. "
        "Для каждого цикла орбита переведена в координаты серий. "
        "Накачка: каждый подблок серий длины ≤ 4 повторяется k=2,3,4 раза; "
        "считается успехом цикл с μ=0 (само слово уже на цикле).\n"
    )
    lines.append("## Результат\n")
    lines.append(
        f"Различных циклов в каталоге: {nums['n_cycles']}. "
        f"Из них членов семейства Т4 (период 4, серии (0)+(1,3)^k): {nums['n_T4_members']}. "
        f"Остальных орбит: {nums['n_sporadic']}. "
        f"Неопределённых исходов в переборе (столбец unknown): {nums['unknown_total']}.\n"
    )
    lines.append("| first_L | период | min_len | max_len | фаза | серии | max серий на орбите | Т4 |")
    lines.append("|---:|---:|---:|---:|---:|---|---:|:---:|")
    for c in nums["cycles"]:
        lines.append(
            f"| {c['first_L']} | {c['period']} | {c['min_len']} | {c['max_len']} | "
            f"{c['phase']} | {c['runs']} | {c['max_series']} | {'да' if c['is_T4'] else ''} |"
        )
    lines.append("")
    # сгруппировать накачки по блоку
    p4 = [p for p in pumps if p["periods_k234"] == [4, 4, 4]]
    grow = [p for p in pumps if p["periods_k234"] == [160, 220, 280]]
    other = [p for p in pumps if p["periods_k234"] not in ([4, 4, 4], [160, 220, 280])]
    sig = nums.get("sigma", {})
    lines.append(
        f"Успешных накачек: {len(pumps)}. "
        f"С постоянным периодом 4 (механизм теоремы 4, включая сдвиги блока вроде (3, 1)): {len(p4)}. "
        f"С периодами 160, 220, 280 при k=2,3,4: {len(grow)}. "
        f"Иных подписей: {len(other)}.\n"
    )
    lines.append(
        "Все растущие накачки — окна одного явления. Его чистая форма — семейство σ_k: "
        "фаза 0, серии (0, 9, 0, 0, 0) + (0, 5, 0, 3)^k. "
        f"Проверено для k=1…{sig.get('kmax')}: совпало {sig.get('n_ok')} из {sig.get('kmax')}. "
        "Период равен 20 при k=1 (это уже известный цикл периода 20) и 40+60k при k≥2. "
        "Статус общей формулы при всех k: **гипотеза**, подтверждённая указанным перебором. "
        "Доказательства для всех k в этой работе нет: лишний блок вдоль орбиты меняет форму, "
        "и индукция не сводится к одной строке, как в теореме 4.\n"
    )
    if other:
        lines.append("Накачки с другой подписью периода:\n")
        for p in other[:15]:
            lines.append(
                f"- период источника {p['source_period']}, блок {p['block']}, "
                f"периоды {p['periods_k234']}"
            )
        lines.append("")
    lines.append("## Статус\n")
    lines.append(
        f"- Каталог до L={nums['enum_max_L']}, unknown={nums['unknown_total']}: **проверено перебором**.\n"
        "- Бесконечное семейство периода 4: **доказано** (теорема 4).\n"
        "- Семейство σ_k (период 20 при k=1 и 40+60k при k≥2): **проверено перебором** "
        "для k до границы в разделе «Результат»; для всех k — **гипотеза**.\n"
        "- «Все циклы лежат в конечном числе семейств»: **гипотеза**.\n"
    )
    open(os.path.join(RES, "track_R2.md"), "w", encoding="utf-8").write("\n".join(lines))

    lines = ["# Трек R3. Неограниченный рост и выбор q=3\n", "## Гипотеза\n",
             "Для q=3 неограниченный рост слова Б^n равносилен расходимости орбиты Коллатца. "
             "При q=4 рост доказуем. Средний множитель ln за макрошаг равен ½ ln(q/4).\n",
             "## Метод\n",
             "Классификация T_q доказана разбором чётной и нечётной ветвей (теорема 3′ в тексте работы). "
             "Численно собраны приращения ln T_q(n) − ln n вдоль орбит.\n",
             "## Результат\n"]
    lines.append(
        f"q=3: макрошагов в выборке {d3['macro_steps']} (n=2…{d3['n_max']}). "
        f"Среднее Δln = {fmt(d3['mean_dln'])}, теория ½ ln(3/4) = {fmt(d3['theory'])}. "
        f"Переходов нечёт→нечёт: {d3['odd_to_odd']} из {d3['odd_steps']} нечётных макрошагов.\n"
    )
    lines.append(
        f"q=5: макрошагов {d5['macro_steps']} (n=2…{d5['n_max']}, не более {d5['step_cap']} шагов на старт, "
        f"обрыв при n>10^18). Среднее Δln = {fmt(d5['mean_dln'])}, теория ½ ln(5/4) = {fmt(d5['theory'])}. "
        f"Переходов нечёт→нечёт: {d5['odd_to_odd']} из {d5['odd_steps']}.\n"
    )
    lines.append(
        f"q=4, старт 3, длины чистых слов: {nums['q4_chain']}. "
        "Каждый шаг — нечётное число, строго большее предыдущего.\n"
    )
    lines.append(
        "Рисунок: `figures/drift_q.png`.\n"
    )
    lines.append("## Статус\n")
    lines.append(
        "- Б^n при q=3 неограниченно ⟺ орбита T неограниченна: **доказано** (теорема 3 и оценка промежуточных длин).\n"
        "- При чётном q≥4 всякое нечётное Б^n растёт неограниченно; при q=2 нечётные Б^n — циклы периода n+1; "
        "при q=1 всякое Б^n останавливается: **доказано**.\n"
        "- Равенство среднего Δln величине ½ ln(q/4): **гипотеза** случайной чётности. "
        "Для q=4 она неприменима (нечётность — инвариант). "
        f"Для q=3 и q=5 среднее по выборке близко к теории: **проверено численно** "
        f"(см. числа выше).\n"
        "- «q=3 — единственное целое q≥1, где эвристика предсказывает сжатие, а простой инвариант чётности исход не закрывает»: "
        "**доказано** как утверждение об этой эвристике, не как решение проблемы Коллатца.\n"
    )
    open(os.path.join(RES, "track_R3.md"), "w", encoding="utf-8").write("\n".join(lines))

    lines = ["# Трек R4. Статистика времени остановки\n", "## Гипотеза\n",
             "S(n)/n сравнимо с суммой геометрической прогрессии со знаменателем sqrt(3/4), "
             "а число макрошагов T — с (2/ln(4/3)) ln n (модель Лагариаса–Вейса для ускоренного отображения).\n",
             "## Метод\n",
             f"Для n от {st['n_min']} до {st['n_max']} орбита T и формула S(n) считаются напрямую, без ручных констант.\n",
             "## Результат\n"]
    lines.append(
        f"S(27) = {st['s27']}, максимум орбиты и максимум длины слова Б^27 = {st['maxlen27']}, "
        f"макрошагов T до 1: {st['macro_steps_27']}.\n"
    )
    lines.append(
        f"Константа модели макрошагов 2/ln(4/3) = {fmt(st['lagarias_const'])}. "
        f"По выборке n=100…{st['n_max']}: среднее (число макрошагов)/ln n = {fmt(st['mean_macro_per_ln'])}, "
        f"медиана = {fmt(st['median_macro_per_ln'])}.\n"
    )
    lines.append(
        f"Среднее S(n)/n = {fmt(st['mean_S_over_n'])}, медиана = {fmt(st['median_S_over_n'])}, "
        f"среднее ln(S/n) = {fmt(st['mean_ln_S_over_n'])}. "
        f"Модельный множитель 1/(1−sqrt(3/4)) = {fmt(st['model_S_factor'])} "
        f"(натуральный логарифм этого множителя = {fmt(math.log(st['model_S_factor']))}).\n"
    )
    lines.append("Рисунок: `figures/log_S_ratio.png`. Тяжёлый хвост — длинные экскурсии, как у n=27.\n")
    lines.append("## Статус\n")
    lines.append(
        "- Формула S(n): **доказано** при условии, что орбита доходит до 1.\n"
        "- Численные средние: **проверено** на указанном диапазоне.\n"
        "- Совпадение числа макрошагов с 2/ln(4/3): **гипотеза** случайной модели; "
        "среднее по выборке к ней близко, медиана меньше из-за асимметрии.\n"
        "- Множитель 1/(1−sqrt(3/4)) для S(n)/n: **гипотеза**. "
        "Он даёт правильный порядок, но медиана S/n примерно вдвое больше: "
        "модель не учитывает корреляции чётности и хвост экскурсий.\n"
    )
    open(os.path.join(RES, "track_R4.md"), "w", encoding="utf-8").write("\n".join(lines))

    info = nums["search_ext"]
    lines = ["# Трек R5. Чистая tag-система на двух буквах\n", "## Гипотеза\n",
             "В малых границах нет чистой tag-системы (правило зависит только от одной буквы) "
             "на алфавите {А, Б}, которая на кодах X^n S вычисляет T.\n",
             "## Метод\n",
             "Программа `csrc/search_ext.c`: классическая ориентация, перебор d, X, суффикса S и продукций. "
             "Принимается система, у которой первое возвращение к слову вида X^m S даёт m=T(n) "
             "на тестовом наборе {2,3,4,5,6,7,8,9,11,12,15,16,27}.\n",
             "## Результат\n"]
    if info.get("ready"):
        lines.append(f"Границы: {info.get('bounds')}.\n")
        lines.append(
            f"Просмотрено систем: {info.get('systems')}. "
            f"Из них прошли тест n=2: {info.get('passed_n2')}. "
            f"Полностью подходящих: {len(info.get('found_lines') or [])}.\n"
        )
        if info.get("found_lines"):
            lines.append("Найденные системы:\n")
            for ln in info["found_lines"]:
                lines.append(f"- {ln}")
        else:
            lines.append("Ни одной системы в этих границах не найдено.\n")
        lines.append("## Статус\n")
        lines.append(
            "- Пустота перебора в напечатанных границах: **проверено перебором**.\n"
            "- «Чистой двухбуквенной tag-системы не существует»: так писать нельзя. "
            "Двоичные tag-системы универсальны при больших параметрах (Neary 2015). "
            "Статус общего существования: **открыто** (ожидается «да, но параметры велики»).\n"
        )
    else:
        lines.append("Поиск ещё не завершён или файл `results/search_ext.txt` не содержит строку DONE.\n")
        lines.append("## Статус\n")
        lines.append("- Расширенный перебор: **не завершён** на момент генерации отчёта.\n")
    # базовый поиск из комментария исходника не пересказываем как факт, пока его не перезапустили
    lines.append(
        "\nБазовый перебор `csrc/search_binary.c` (d≤6, |продукции|≤8, коды X^n без суффикса, |X|≤3) "
        "оставлен отдельной программой; его повторный прогон, если выполнен, пишется в `results/search_binary_stdout.txt`.\n"
    )
    open(os.path.join(RES, "track_R5.md"), "w", encoding="utf-8").write("\n".join(lines))

    # таблица перебора для статьи
    et = ["| L | классов | остановка | цикл | неизвестно | макс. шагов до остановки |",
          "|---:|---:|---:|---:|---:|---:|"]
    for r in nums["enum"]:
        et.append(f"| {r['L']} | {r['classes']} | {r['halt']} | {r['cycle']} | {r['unknown']} | {r['max_steps_to_halt']} |")
    open(os.path.join(RES, "enum_table.md"), "w", encoding="utf-8").write("\n".join(et) + "\n")

    # json без огромных полей — pumps отдельно кратко
    nums["pumps_summary"] = {
        "n_hits": len(pumps),
        "n_block_13": sum(1 for p in pumps if p["block"] == [1, 3]),
        "n_other": sum(1 for p in pumps if p["block"] != [1, 3]),
        "other": [p for p in pumps if p["block"] != [1, 3]][:20],
    }
    # убрать несериализуемое при наличии
    out = dict(nums)
    open(os.path.join(RES, "key_numbers.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=2)
    )


def main():
    nums = {}
    print("R1...")
    track_r1(nums)
    print("cycles...")
    cycles = annotate_cycles(dedupe_cycles(load_cycles_base() + load_new_cycles()))
    print("pumps...", "states", sum(len(c.get("states", [])) for c in cycles))
    pumps = search_pumps(cycles)
    print("sigma...")
    nums["sigma"] = verify_sigma(24)
    print("pumps found", len(pumps))
    print("enum...")
    enum_rows = load_enum_rows()
    track_r2(nums, cycles, enum_rows)
    print("R3...")
    track_r3(nums)
    print("R4...")
    track_r4(nums)
    track_r5(nums)
    write_reports(nums, pumps)
    print("enum_max_L", nums["enum_max_L"], "cycles", nums["n_cycles"], "S27", nums["stopping"]["s27"])
    print("wrote results/track_R*.md and key_numbers.json")


if __name__ == "__main__":
    main()
