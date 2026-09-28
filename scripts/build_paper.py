"""Собирает paper/solution_ru.md из шаблона и results/key_numbers.json.

Числа в текст подставляются только отсюда. После правки шаблона:
    python scripts/build_paper.py
"""
from __future__ import annotations
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tagsys.collatz import predicted_halting_steps, collatz_orbit
from tagsys.core import TASK, to_cyr

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def commit_id() -> str:
    try:
        h = subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, text=True
        ).strip()
        dirty = subprocess.call(["git", "diff", "--quiet", "HEAD"], cwd=ROOT) != 0
        return h + ("-dirty" if dirty else "")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def isp(n) -> str:
    return f"{int(n):,}".replace(",", " ")


def fnum(x, nd=5) -> str:
    return f"{float(x):.{nd}f}"


def mile_lengths(n: int) -> str:
    w = "B" * n
    out = [str(len(w))]
    guard = 0
    while guard < 100000:
        guard += 1
        nxt = TASK.step(w)
        if nxt is None:
            break
        w = nxt
        if set(w) == {"B"}:
            out.append(str(len(w)))
            if w == "B":
                break
    return ", ".join(out)


def milestones(n: int) -> str:
    w = "B" * n
    out = [to_cyr(w)]
    guard = 0
    while guard < 100000:
        guard += 1
        nxt = TASK.step(w)
        if nxt is None:
            break
        w = nxt
        if set(w) == {"B"}:
            out.append(to_cyr(w))
            if w == "B":
                break
    return " → ".join(out)


def first_macro(n: int) -> str:
    w = "B" * n
    out = [to_cyr(w)]
    guard = 0
    while guard < 10000:
        guard += 1
        w = TASK.step(w)
        out.append("стоп" if w is None else to_cyr(w))
        if w is None or set(w) == {"B"}:
            break
    return " → ".join(out)


def cycle_table(cycles) -> str:
    lines = [
        "| первое L | период | min | max | серии канонического слова | пометка |",
        "|---:|---:|---:|---:|---|---|",
    ]
    for c in cycles:
        if c.get("is_T4"):
            note = "семейство Т4"
        elif c["period"] == 20:
            note = "σ_1"
        elif c["period"] == 148:
            note = "новый цикл, L=26"
        else:
            note = "отдельная орбита"
        lines.append(
            f"| {c['first_L']} | {c['period']} | {c['min_len']} | {c['max_len']} | `{c['runs']}` | {note} |"
        )
    return "\n".join(lines)


def main():
    nums = json.load(open(os.path.join(ROOT, "results", "key_numbers.json"), encoding="utf-8"))
    tpl = open(os.path.join(ROOT, "paper", "solution_ru.tpl.md"), encoding="utf-8").read()
    st = nums["stopping"]
    d3 = nums["drift"]["q3"]
    d5 = nums["drift"]["q5"]
    cx = nums["counterexample"]
    sig = nums["sigma"]
    se = nums["search_ext"]
    assert se.get("ready") and sig["n_ok"] == sig["kmax"]
    # контроль: знаменитое S(27) совпадает с формулой, а не с чужой записью
    assert predicted_halting_steps(27) == st["s27"]
    assert max(collatz_orbit(27)) == st["maxlen27"]
    enum_md = open(os.path.join(ROOT, "results", "enum_table.md"), encoding="utf-8").read().strip()
    repl = {
        "S27": isp(st["s27"]),
        "MAXLEN27": isp(st["maxlen27"]),
        "MACRO27": str(st["macro_steps_27"]),
        "STATES20": isp(nums["states_le_20"]),
        "ENTRY_N": isp(nums["entry_classes_checked"]),
        "ENTRY_L": str(nums["entry_L_max"]),
        "PAIRS": isp(nums["macro_pairs_checked"]),
        "COMP_MATCH": str(nums["componentwise_T_matches"]),
        "CX_N": str(cx["n"]),
        "CX_M": str(cx["m"]),
        "CX_RUNS": str(cx["out_runs"]).replace(" ", ""),
        "CX_TN": str(cx["T_n"]),
        "CX_TM": str(cx["T_m"]),
        "N_CYCLES": str(nums["n_cycles"]),
        "N_T4": str(nums["n_T4_members"]),
        "ENUM_L": str(nums["enum_max_L"]),
        "UNKNOWN": str(nums["unknown_total"]),
        "SIGMA_KMAX": str(sig["kmax"]),
        "BASINS_NOTE": open(os.path.join(ROOT, "results", "basins_highlight.md"), encoding="utf-8").read().strip(),
        "Q3_MEAN": fnum(d3["mean_dln"], 3),
        "Q3_TH": fnum(d3["theory"], 3),
        "Q3_STEPS": isp(d3["macro_steps"]),
        "Q3_N": isp(d3["n_max"]),
        "Q3_ODD": isp(d3["odd_steps"]),
        "Q3_OO": isp(d3["odd_to_odd"]),
        "Q5_MEAN": fnum(d5["mean_dln"], 3),
        "Q5_TH": fnum(d5["theory"], 3),
        "Q5_STEPS": isp(d5["macro_steps"]),
        "Q5_N": isp(d5["n_max"]),
        "LAG": fnum(st["lagarias_const"], 4),
        "MEAN_MAC": fnum(st["mean_macro_per_ln"], 3),
        "MED_MAC": fnum(st["median_macro_per_ln"], 3),
        "MEAN_S": fnum(st["mean_S_over_n"], 2),
        "MED_S": fnum(st["median_S_over_n"], 2),
        "MODEL_S": fnum(st["model_S_factor"], 3),
        "MEAN_LN_S": fnum(st["mean_ln_S_over_n"], 3),
        "NMAX_S": isp(st["n_max"]),
        "SEARCH_SYS": isp(se["systems"]),
        "SEARCH_N2": isp(se["passed_n2"]),
        "SEARCH_FOUND": str(len(se.get("found_lines") or [])),
        "SEARCH_BOUNDS": se["bounds"],
        "BIN2_S27": isp(nums["bin2"]["s27"]),
        "UNIQ_SYSTEMS": isp(nums["unique3"]["plus_systems"]),
        "UNIQ_FOUND": str(nums["unique3"]["plus_found"]),
        "UNIQ_MINUS_SYSTEMS": isp(nums["unique3"]["minus_systems"]),
        "UNIQ_MINUS_FOUND": str(nums["unique3"]["minus_found"]),
        "VAR_SYSTEMS": isp(nums["vardelete"]["systems"]),
        "VAR_TESTED": isp(nums["vardelete"]["tested"]),
        "VAR_FOUND": str(nums["vardelete"]["found"]),
        "CTX_TESTED": isp(nums["context2"]["tested"]),
        "CTX_FOUND": str(nums["context2"]["found"]),
        "L9_P4": str(nums["length9"]["period4_classes"]),
        "L9_P40": str(nums["length9"]["period40_classes"]),
        "L9_W4": str(nums["length9"]["period4_words"]),
        "L9_W40": str(nums["length9"]["period40_words"]),
        "Q4_CHAIN": ", ".join(str(x) for x in nums["q4_chain"]),
        "TRACE3": first_macro(3),
        "TRACE6": first_macro(6),
        "MILE3": milestones(3),
        "MILE7": mile_lengths(7),
        "ENUM_TABLE": enum_md,
        "CYCLE_TABLE": cycle_table(nums["cycles"]),
        "GITHUB": "https://github.com/KonkovDV/hod-mysli-2026-alphabet",
        "COMMIT": commit_id(),
    }
    out = tpl
    for k, v in repl.items():
        token = "{{" + k + "}}"
        if token not in out:
            raise SystemExit(f"шаблон не содержит {token}")
        out = out.replace(token, v)
    if "{{" in out:
        raise SystemExit("в тексте остались незаполненные скобки")
    dest = os.path.join(ROOT, "paper", "solution_ru.md")
    open(dest, "w", encoding="utf-8").write(out)
    print("wrote", dest, "chars", len(out))


if __name__ == "__main__":
    main()
