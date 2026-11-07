"""Summarize results/synth_strict/synth_premise_check.json: how much of the shadow log is valid system behavior,
and whether the strict undershoot of ShadowGen on the inductive nets (synth_unseen_check.json) is that invalid share.

Run from the repo root:  python benchmark/synth_premise_analyze.py
Writes results/synth_strict/summary_premise.md.
"""
import os
import json
import math
import statistics as st

_HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(_HERE, "results", "synth_strict")


def pearson(x, y):
    n = len(x)
    if n < 3:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sxy / (sx * sy) if sx > 1e-12 and sy > 1e-12 else float("nan")


def q(v, name):
    v = sorted(x for x in v if x is not None)
    if not v:
        return f"| {name} | 0 | | | | | |"
    qs = st.quantiles(v, n=4) if len(v) >= 4 else [v[0], st.median(v), v[-1]]
    return f"| {name} | {len(v)} | {st.mean(v):.3f} | {min(v):.3f} | {qs[0]:.3f} | {st.median(v):.3f} | {qs[2]:.3f} | {max(v):.3f} |"


def main():
    d = json.load(open(os.path.join(DIR, "synth_premise_check.json"), encoding="utf-8"))
    S = d["systems"]
    lines = [f"# Generator premise on the synthetic known systems ({d['n_systems']} systems, {d['protocol']})", "",
             f"Trees match the stored study on {sum(s['tree_matches_stored'] for s in S)} of {len(S)}; logs resampled. "
             "Shadow log generated once per system from the 300-trace training log and replayed on the system itself.", "",
             "| quantity | n | mean | min | Q1 | median | Q3 | max |", "|---|---|---|---|---|---|---|---|"]
    for key, name in [("valid_strict", "shadow traces in the system's language (strict)"),
                      ("valid_graded", "shadow log replay fitness on the system (graded)"),
                      ("valid_strict_regular", "strict, regular traces"), ("valid_strict_mutated", "strict, mutated traces"),
                      ("valid_graded_regular", "graded, regular traces"), ("valid_graded_mutated", "graded, mutated traces"),
                      ("hit_unseen", "shadow traces that are an unseen future variant (hit rate)"),
                      ("hit_unseen_regular", "hit rate, regular"), ("hit_unseen_mutated", "hit rate, mutated"),
                      ("unseen_variants_covered", "share of unseen future variants covered by the shadow log"),
                      ("random_valid_strict", "random traces in the system's language (strict)"),
                      ("random_valid_graded", "random traces replay fitness (graded)"),
                      ("random_hit_unseen", "random traces that are an unseen future variant"),
                      ("shadow_in_L", "shadow traces whose variant is in the training log (duplicates kept)")]:
        lines.append(q([s.get(key) for s in S], name))
    mut = [s["n_mutated"] / s["n_shadow"] for s in S]
    lines.append(q(mut, "mutated share of the shadow log"))

    # pooled over all shadow traces (weights systems equally only via equal shadow size)
    n = sum(s["n_shadow"] for s in S)
    lines.append(f"\nPooled over all {n} shadow traces: valid strict {sum(s['valid_strict'] * s['n_shadow'] for s in S) / n:.3f}, "
                 f"valid graded {sum(s['valid_graded'] * s['n_shadow'] for s in S) / n:.3f}, hit rate {sum(s['hit_unseen'] * s['n_shadow'] for s in S) / n:.3f}; "
                 f"random: valid strict {sum(s['random_valid_strict'] * s['n_shadow'] for s in S) / n:.4f}, hit rate {sum(s['random_hit_unseen'] * s['n_shadow'] for s in S) / n:.4f}.")

    # relation to log size
    vl = [s["var_L"] for s in S]
    vs = [s["valid_strict"] for s in S]
    lines.append(f"\nValid share against the number of training variants: Pearson {pearson([math.log(x) for x in vl], vs):.3f} (log variants); "
                 f"systems with valid share < 0.5: {sum(x < 0.5 for x in vs)}; < 0.9: {sum(x < 0.9 for x in vs)}.")

    # join with the unseen run: strict undershoot on Inductive strict vs invalid share
    path = os.path.join(DIR, "synth_unseen_check.json")
    if os.path.exists(path):
        u = {(s["mode"], s["seed"]): s for s in json.load(open(path, encoding="utf-8"))["systems"]}
        rows = []
        for s in S:
            us = u.get((s["mode"], s["seed"]))
            if not us:
                continue
            m = us["models"].get("Inductive_Strict")
            if m and m.get("error") is None and m.get("true_recall_strict_unseen") is not None:
                rows.append((s["valid_strict"], m["strict"], m["true_recall_strict_unseen"], s["valid_graded"], m["graded"], m["true_recall_unseen"]))
        if rows:
            v, sc, ref, vg, g, refg = zip(*rows)
            under = [r - x for x, r in zip(sc, ref)]
            lines.append(f"\nInductive strict net (n={len(rows)}): strict score mean {st.mean(sc):.3f}, strict reference mean {st.mean(ref):.3f}, "
                         f"valid share mean {st.mean(v):.3f}; Pearson(strict score, valid share) {pearson(sc, v):.3f}; "
                         f"mean |strict score - valid share| {st.mean(abs(a - b) for a, b in zip(sc, v)):.3f}; "
                         f"undershoot mean {st.mean(under):.3f} against invalid share mean {1 - st.mean(v):.3f}. "
                         f"Graded: score mean {st.mean(g):.3f}, valid graded mean {st.mean(vg):.3f}, reference mean {st.mean(refg):.3f}, "
                         f"mean |graded score - valid graded| {st.mean(abs(a - b) for a, b in zip(g, vg)):.3f}.")

    out = os.path.join(DIR, "summary_premise.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
