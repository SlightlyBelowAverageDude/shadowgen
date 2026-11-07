"""Fitness baseline for the randomization runs (read-only, prints only).

Does plain training fitness predict the unseen-future reference as well
as ShadowGen? Uses the randomization result files (final or partial). Prints only."""
import json, os, sys
import numpy as np

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "randomization")
REAL = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
FILES = {"L1": "randomization_D1.json", "L2": "randomization_D2.json",
         "L3": "randomization_D3.partial.json", "L5": "randomization_D5.partial.json"}


def ranks(x):
    o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); r[o] = np.arange(1, len(x) + 1)
    for v in np.unique(x):
        m = x == v; r[m] = r[m].mean()
    return r


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else float("nan")


def stats(pred, truth):
    return corr(pred, truth), corr(ranks(pred), ranks(truth)), float(np.mean(np.abs(pred - truth)))


for lid, fn in FILES.items():
    rec = json.load(open(os.path.join(D, fn), encoding="utf-8"))
    print(f"\n=== {lid} ({fn}) ===")
    print("p     reps | graded: ShadowGen P/S/MAE      | fitness P/S/MAE        | mean|truth-fit| || "
          "strict: ShadowGen P/S/MAE     | strict fitness P/S/MAE")
    for p in rec["levels"]:
        rows = {"sg": [], "fit": [], "sgs": [], "fits": [], "gap": []}
        for key, c in rec["cells"].items():
            if abs(float(key.split("|")[0]) - p) > 1e-9:
                continue
            g = lambda k: np.array([float(c["models"][m][k]) for m in REAL])
            try:
                t, ts = g("unseen_fit"), g("unseen_fit_strict")
                rows["sg"].append(stats(g("shadowgen"), t)); rows["fit"].append(stats(g("train_fit"), t))
                rows["sgs"].append(stats(g("shadowgen_strict"), ts))
                rows["fits"].append(stats(g("train_fit_strict"), ts))
                rows["gap"].append(float(np.mean(np.abs(t - g("train_fit")))))
            except (KeyError, TypeError):
                continue
        if not rows["sg"]:
            continue
        med = lambda k: np.nanmedian(np.array(rows[k]), axis=0)
        f = lambda v: f"{v[0]:6.3f} {v[1]:6.3f} {v[2]:5.3f}"
        print(f"{p:4.2f}  {len(rows['sg'])}    | {f(med('sg'))}        | {f(med('fit'))}    | "
              f"{np.median(rows['gap']):.3f}          || {f(med('sgs'))}       | {f(med('fits'))}")

# per-model view at p = 0, first repetition
print("\n=== per model at p = 0, repetition 0: truth / training fitness / ShadowGen (graded | strict) ===")
for lid, fn in FILES.items():
    rec = json.load(open(os.path.join(D, fn), encoding="utf-8"))
    c = rec["cells"]["0.00|0"]
    print(lid)
    for m in ["Trace_Filtered"] + REAL + ["Flower"]:
        x = c["models"][m]
        print(f"  {m:22s} {x['unseen_fit']:.3f} / {x['train_fit']:.3f} / {x['shadowgen']:.3f}   |   "
              f"{x['unseen_fit_strict']:.3f} / {x['train_fit_strict']:.3f} / {x['shadowgen_strict']:.3f}")
