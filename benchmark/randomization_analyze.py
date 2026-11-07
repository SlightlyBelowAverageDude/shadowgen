"""Summary of the randomization test (benchmark/randomization_test.py).

Reads results/randomization/randomization_<key>.json and prints / writes, per log:
  A  per level: agreement of each metric with the truth over the six real miners
     (Pearson, Spearman, MAE, spread of metric vs spread of truth), median over repetitions
  B  per model: truth, training fitness, gap, ShadowGen and M2 per level (mean over repetitions)
  C  per model: does the metric move with the truth from p = 0 to p = 1 (change of each)
Output: results/randomization/summary_<key>.md (overwrites only its own summary).
Run from the repo root:  env/Scripts/python.exe benchmark/randomization_analyze.py D1 D2
"""
import os
import sys
import json
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(_HERE, "results", "randomization")
REAL = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
ALL = ["Trace_Filtered"] + REAL + ["Flower"]
PAIRS = [("ShadowGen graded", "shadowgen", "unseen_fit"),
         ("ShadowGen strict", "shadowgen_strict", "unseen_fit_strict"),
         ("M2", "m2", "unseen_fit")]


def ranks(x):
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x), float)
    r[order] = np.arange(1, len(x) + 1)
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return r


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else float("nan")


def vec(cell, key, models):
    out = []
    for m in models:
        v = cell["models"][m].get(key)
        out.append(np.nan if v is None else float(v))
    return np.array(out)


def fmt(x, w=7, d=3):
    return ("-".rjust(w) if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:{w}.{d}f}")


def analyze(key, tag=""):
    stem = f"randomization_{key}" + (f"_{tag}" if tag else "")
    final = os.path.join(OUT_DIR, stem + ".json")
    running = not os.path.exists(final)          # a run in progress has only the partial file
    rec = json.load(open(final if not running else os.path.join(OUT_DIR, stem + ".partial.json"),
                         encoding="utf-8"))
    levels = rec["levels"]
    # complete repetitions only (all levels present)
    reps = 0
    while all(f"{p:.2f}|{reps}" in rec["cells"] for p in levels):
        reps += 1
    if reps == 0:
        print(f"[{key}] no complete repetition yet ({len(rec['cells'])} cells)")
        return
    L = []
    L.append(f"# Randomization test, {key} ({rec['dataset']}), {rec['n_cases']} cases, {reps} repetitions"
             + (f" of {rec['reps']} (run in progress)" if running else ""))
    L.append("")
    L.append(rec.get("protocol", "protocol: see benchmark/randomization_test.py"))
    L.append("")
    L.append("## Log statistics per level (mean over repetitions)")
    L.append("")
    L.append("| p | training variants | unseen share of the future | errors |")
    L.append("|---|---|---|---|")
    for p in levels:
        cs = [rec["cells"][f"{p:.2f}|{r}"] for r in range(reps)]
        errs = sum(1 for c in cs for m in c["models"].values() if m.get("error"))
        L.append(f"| {p:.2f} | {np.mean([c['var_train'] for c in cs]):.0f} | "
                 f"{np.mean([c['unseen_share'] for c in cs]):.3f} | {errs} |")
    L.append("")
    L.append("## A. Agreement with the truth over the six real miners (median over repetitions)")
    L.append("")
    L.append("| metric | p | Pearson | Spearman | MAE | spread metric | spread truth |")
    L.append("|---|---|---|---|---|---|---|")
    for name, mk, tk in PAIRS:
        for p in levels:
            rows = []
            for r in range(reps):
                c = rec["cells"][f"{p:.2f}|{r}"]
                a, b = vec(c, mk, REAL), vec(c, tk, REAL)
                ok = ~(np.isnan(a) | np.isnan(b))
                if ok.sum() < 4:
                    continue
                a, b = a[ok], b[ok]
                rows.append((corr(a, b), corr(ranks(a), ranks(b)), float(np.mean(np.abs(a - b))),
                             float(a.max() - a.min()), float(b.max() - b.min())))
            if rows:
                med = np.nanmedian(np.array(rows), axis=0)
                L.append(f"| {name} | {p:.2f} | {med[0]:.3f} | {med[1]:.3f} | {med[2]:.3f} | "
                         f"{med[3]:.3f} | {med[4]:.3f} |")
    L.append("")
    L.append("## B. Per model and level (mean over repetitions)")
    for title, keys in [("graded reading", ("unseen_fit", "train_fit", "shadowgen", "m2")),
                        ("strict reading", ("unseen_fit_strict", "train_fit_strict", "shadowgen_strict", None))]:
        L.append("")
        L.append(f"### {title}: truth / training / gap (training minus truth) / ShadowGen"
                 + (" / M2" if keys[3] else ""))
        L.append("")
        L.append("| model | " + " | ".join(f"p={p:.2f}" for p in levels) + " |")
        L.append("|---|" + "---|" * len(levels))
        for m in ALL:
            cellsout = []
            for p in levels:
                cs = [rec["cells"][f"{p:.2f}|{r}"]["models"][m] for r in range(reps)]
                def mean(k):
                    v = [c.get(k) for c in cs if c.get(k) is not None]
                    return float(np.mean(v)) if v else float("nan")
                t, tr, sg = mean(keys[0]), mean(keys[1]), mean(keys[2])
                s = f"{t:.3f} / {tr:.3f} / {tr - t:+.3f} / {sg:.3f}"
                if keys[3]:
                    s += f" / {mean(keys[3]):.3f}"
                cellsout.append(s)
            L.append(f"| {m} | " + " | ".join(cellsout) + " |")
    L.append("")
    L.append("## C. Change from p = 0 to p = 1 (mean over repetitions)")
    L.append("")
    L.append("| model | truth | ShadowGen | M2 | truth strict | ShadowGen strict |")
    L.append("|---|---|---|---|---|---|")
    p0, p1 = levels[0], levels[-1]
    dt, ds, dm = [], [], []
    for m in ALL:
        def delta(k):
            a = [rec["cells"][f"{p0:.2f}|{r}"]["models"][m].get(k) for r in range(reps)]
            b = [rec["cells"][f"{p1:.2f}|{r}"]["models"][m].get(k) for r in range(reps)]
            a = [x for x in a if x is not None]; b = [x for x in b if x is not None]
            return float(np.mean(b) - np.mean(a)) if a and b else float("nan")
        row = [delta("unseen_fit"), delta("shadowgen"), delta("m2"),
               delta("unseen_fit_strict"), delta("shadowgen_strict")]
        if m in REAL:
            dt.append(row[0]); ds.append(row[1]); dm.append(row[2])
        L.append(f"| {m} | " + " | ".join(f"{x:+.3f}" for x in row) + " |")
    L.append("")
    L.append(f"Correlation of the change over the six real miners: ShadowGen vs truth "
             f"{corr(np.array(ds), np.array(dt)):.3f}, M2 vs truth {corr(np.array(dm), np.array(dt)):.3f}.")
    text = "\n".join(L) + "\n"
    path = os.path.join(OUT_DIR, f"summary_{key}" + (f"_{tag}" if tag else "")
                        + ("_partial" if running else "") + ".md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"[written {path}]")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--tag=")]
    tag = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--tag=")), "")
    for k in args or ["D1", "D2"]:
        analyze(k, tag)
