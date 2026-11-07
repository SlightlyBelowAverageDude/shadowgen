"""Four criteria for the temporal hold-out against both references (all test cases, unseen test cases only),
for both ShadowGen readings and M2, from results/temporal_unseen/temporal_unseen_<key>.json.

Criteria as in four_criteria_new_refs.py (Pearson, Spearman with argsort ranks as in the submitted table,
Kendall tau_b, MAE, spread of metric and reference over the six non-degenerate miners). A tie-aware
Spearman is added because the strict values contain ties (many exact zeros).
Run from the repo root:  python benchmark/temporal_unseen_analyze.py
Writes results/temporal_unseen/summary.md and summary.json.
"""
import os
import json
import math

import numpy as np

# criterion functions copied verbatim from four_criteria_new_refs.py (importing it would run that script
# and rewrite results/four_criteria_new_refs.json)
def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x, y):
    rank = lambda v: np.argsort(np.argsort(np.asarray(v, float))).astype(float)
    return pearson(rank(x), rank(y))


def kendall_tau_b(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    C = D = tx = ty = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx, dy = x[i] - x[j], y[i] - y[j]
            if dx == 0 and dy == 0:
                continue
            if dx == 0:
                tx += 1
            elif dy == 0:
                ty += 1
            elif dx * dy > 0:
                C += 1
            else:
                D += 1
    den = np.sqrt((C + D + tx) * (C + D + ty))
    return None if den == 0 else float((C - D) / den)


def mae(x, y):
    return float(np.mean(np.abs(np.asarray(x, float) - np.asarray(y, float))))


def spread(v):
    return float(max(v) - min(v))



_HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(_HERE, "results", "temporal_unseen")
REAL = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
POLES = ["Trace_Filtered", "Flower"]
LOGS = ["D1", "D2", "D3", "D4", "D5"]
LAB = {"D1": "L1", "D2": "L2", "D3": "L3", "D4": "L4", "D5": "L5"}
PAIRS = [("ShadowGen graded", "shadowgen", "holdout_fit"), ("ShadowGen graded", "shadowgen", "unseen_fit"),
         ("ShadowGen strict", "shadowgen_strict", "holdout_fit_strict"), ("ShadowGen strict", "shadowgen_strict", "unseen_fit_strict"),
         ("M2", "m2", "holdout_fit"), ("M2", "m2", "unseen_fit")]


def tie_ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def f(x, d=3):
    return "--" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}"


def main():
    recs = {}
    for k in LOGS:
        p = os.path.join(DIR, f"temporal_unseen_{k}.json")
        if os.path.exists(p):
            recs[k] = json.load(open(p, encoding="utf-8"))
    lines = ["# Temporal hold-out: all test cases against unseen test cases only", ""]
    lines.append("| log | test cases | unseen cases | unseen share | unseen variants |")
    lines.append("|---|---|---|---|---|")
    for k, r in recs.items():
        lines.append(f"| {LAB[k]} | {r['n_test']} | {r['n_test_unseen']} | {r['unseen_share']:.3f} | {r['var_test_unseen']} |")

    lines.append("\n## Reproduction of the stored run (|fresh - stored| per model, six miners and poles)\n")
    lines.append("| log | shadowgen max | holdout_fit max | holdout_fit_strict max | m2 max | models above 0.001 |")
    lines.append("|---|---|---|---|---|---|")
    for k, r in recs.items():
        mx, above = {}, []
        for key in ("shadowgen", "holdout_fit", "holdout_fit_strict", "m2"):
            ds = []
            for mn, m in r["models"].items():
                if m.get("error") is None and m.get(key) is not None and m.get(key + "_stored") is not None:
                    d = abs(m[key] - m[key + "_stored"])
                    ds.append(d)
                    if d > 0.001:
                        above.append(f"{mn}.{key} {d:.4f}")
            mx[key] = max(ds) if ds else None
        lines.append(f"| {LAB[k]} | {f(mx['shadowgen'], 4)} | {f(mx['holdout_fit'], 4)} | {f(mx['holdout_fit_strict'], 4)} | {f(mx['m2'], 4)} | {'; '.join(above) or 'none'} |")

    out = {}
    lines.append("\n## Four criteria over the six miners\n")
    lines.append("| log | metric | reference | Pearson | Spearman | Spearman (ties) | tau_b | MAE | spread metric | spread reference |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for k, r in recs.items():
        m = r["models"]
        out[k] = {}
        for name, key, ref in PAIRS:
            xs, ys = [], []
            for n in REAL:
                if m[n].get("error") is None and m[n].get(key) is not None and m[n].get(ref) is not None:
                    xs.append(m[n][key]); ys.append(m[n][ref])
            if len(xs) < 3:
                continue
            c = {"pearson": pearson(xs, ys), "spearman": spearman(xs, ys),
                 "spearman_ties": pearson(tie_ranks(xs), tie_ranks(ys)), "kendall_tau_b": kendall_tau_b(xs, ys),
                 "mae": mae(xs, ys), "spread_metric": spread(xs), "spread_gt": spread(ys), "n": len(xs)}
            out[k][f"{key}~{ref}"] = c
            lines.append(f"| {LAB[k]} | {name} | {ref} | {f(c['pearson'])} | {f(c['spearman'], 2)} | {f(c['spearman_ties'], 2)} | {f(c['kendall_tau_b'], 2)} | {f(c['mae'])} | {f(c['spread_metric'], 2)} | {f(c['spread_gt'], 2)} |")

    lines.append("\n## Per model: score against both references (graded and strict)\n")
    lines.append("| log | model | graded | all | unseen | graded - unseen | strict | all strict | unseen strict | strict - unseen strict |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for k, r in recs.items():
        for n in REAL + POLES:
            v = r["models"][n]
            if v.get("error"):
                lines.append(f"| {LAB[k]} | {n} | error: {v['error']} | | | | | | | |")
                continue
            dg = None if v.get("unseen_fit") is None else v["shadowgen"] - v["unseen_fit"]
            ds = None if v.get("unseen_fit_strict") is None else v["shadowgen_strict"] - v["unseen_fit_strict"]
            lines.append(f"| {LAB[k]} | {n} | {f(v['shadowgen'])} | {f(v['holdout_fit'])} | {f(v.get('unseen_fit'))} | {f(dg)} | "
                         f"{f(v['shadowgen_strict'])} | {f(v['holdout_fit_strict'])} | {f(v.get('unseen_fit_strict'))} | {f(ds)} |")

    # summary ranges over logs
    lines.append("\n## Ranges over the logs\n")
    for key in out[next(iter(out))]:
        vals = {c: [out[k][key][c] for k in out if key in out[k] and out[k][key][c] is not None] for c in ("pearson", "spearman", "spearman_ties", "mae")}
        rng = {c: (f"{min(v):.3f} to {max(v):.3f}" if v else "--") for c, v in vals.items()}
        lines.append(f"- {key}: Pearson {rng['pearson']}; Spearman {rng['spearman']} (ties {rng['spearman_ties']}); MAE {rng['mae']}")

    open(os.path.join(DIR, "summary.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    json.dump(out, open(os.path.join(DIR, "summary.json"), "w", encoding="utf-8"), indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
