"""Сверяет свежий прогон enum с сохранённым каталогом и считает циклы."""
import csv
import sys


def main() -> None:
    got_path, ref_path, lmax = sys.argv[1], sys.argv[2], int(sys.argv[3])
    got = {int(r["L"]): r for r in csv.DictReader(open(got_path, encoding="utf-8"))}
    ref = {int(r["L"]): r for r in csv.DictReader(open(ref_path, encoding="utf-8"))}
    keys = ["classes", "halt", "cycle", "unknown", "max_steps_to_halt", "argmax_word"]
    for length in range(2, lmax + 1):
        for key in keys:
            if got[length][key] != ref[length][key]:
                raise SystemExit(f"{length} {key}: {got[length][key]} != {ref[length][key]}")
    cycles = list(csv.DictReader(open("results/cycles.csv", encoding="utf-8")))
    if len(cycles) != 11:
        raise SystemExit(f"cycles.csv: {len(cycles)} rows, expected 11")
    print(f"enum 2..{lmax} matches, cycles={len(cycles)}")


if __name__ == "__main__":
    main()
