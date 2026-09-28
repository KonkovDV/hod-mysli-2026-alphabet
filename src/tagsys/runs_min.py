"""Правила R1–R5 (копия семантики runs.step_state из репозитория) для автономных скриптов."""
def word_len(phase, r): return sum(r) + 2*(len(r)-1) + phase
def step_state(phase, runs):
    r = list(runs)
    if word_len(phase, r) < 2: return None
    k = len(r)-1; nk = r[-1]
    if phase == 0:
        if nk >= 2: return 0, tuple([0]+r[:-1]+[nk-2])
        if nk == 1:
            if k == 0: return None
            return 1, tuple([0]+r[:-1])
        return 0, tuple([r[0]+1]+r[1:-1])
    if nk >= 1:
        if k == 0: return 0, (r[0]+2,)
        return 0, tuple([r[0]+3]+r[1:-1]+[nk-1])
    return 1, tuple([r[0]+3]+r[1:-1])
def decode(phase, runs):
    w = "B"*runs[0] + "".join("AC"+"B"*n for n in runs[1:])
    return w + ("A" if phase else "")
