"""Analyze a results/synth_strict/*.json run: both ShadowGen readings against true recall and true
precision on the synthetic systems, with the replication check against the stored study.

Usage (from the repo root):
  python benchmark/synth_strict_analyze.py [--file synth_strict_check.json] [--ref full|unseen]

--ref full    reference = replay fitness of the whole fresh sample F (as in the original study)
--ref unseen  reference = replay fitness of the traces of F whose variant is absent from the
              training log (the reference Eq. (1) of the paper asks for); needs a run that
              recorded true_recall_unseen / true_recall_strict_unseen.
Writes results/synth_strict/summary_<file stem>_<ref>.md.
"""
import os
import json
import math
import argparse
import statistics as st

_HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(_HERE, "results", "synth_strict")
MINERS = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
POLES = ["Trace_Filtered", "Flower"]
SPREAD_MIN = 0.05
REF_FIELDS = {
    "full": {"graded": "true_recall", "strict": "true_recall_strict"},
    "unseen": {"graded": "true_recall_unseen", "strict": "true_recall_strict_unseen"},
}


def pearson(x, y):
    n = len(x)
    if n < 3:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sxy / (sx * sy) if sx > 1e-12 and sy > 1e-12 else float("nan")


def ranks(v):
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


def spearman(x, y):
    return pearson(ranks(x), ranks(y))


def partial(x, y, z):
    """corr(x, y | z)"""
    rxy, rxz, ryz = pearson(x, y), pearson(x, z), pearson(y, z)
    if any(math.isnan(v) for v in (rxy, rxz, ryz)) or abs(rxz) >= 1 or abs(ryz) >= 1:
        return float("nan")
    return (rxy - rxz * ryz) / math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))


def clean(v):
    return [x for x in v if not (isinstance(x, float) and math.isnan(x))]


def med(v):
    v = clean(v)
    return st.median(v) if v else float("nan")


def pos(v):
    v = clean(v)
    return sum(x > 0 for x in v) / len(v) if v else float("nan")


def rows_of(s, miners, fields):
    out = []
    for m in miners:
        v = s["models"].get(m)
        if not v or v.get("error") is not None:
            continue
        if any(v.get(f) is None for f in fields):
            continue
        out.append([v[f] for f in fields])
    return out


def block(systems, miners, label, lines, rf, discriminating):
    """Pooled, centred, per-system statistics for both readings against the reference and precision."""
    pairs = [("graded", rf["graded"]), ("strict", rf["strict"]), ("strict", rf["graded"])]
    lines.append(f"\n### {label}\n")
    lines.append("| reading | reference | n pairs | pooled r | centred r | per-system median r | positive | per-system median rho | median MAE | partial r with precision given reference | per-system median r with precision |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for reading, ref in pairs:
        X, Y, P, cX, cY, cP = [], [], [], [], [], []
        per_r, per_rho, per_mae, per_rp = [], [], [], []
        for s in systems:
            rows = rows_of(s, miners, [reading, ref, "true_precision"])
            if len(rows) < 3:
                continue
            a, b, c = zip(*rows)
            if discriminating and st.pstdev(b) < SPREAD_MIN:
                continue
            X += a; Y += b; P += c
            ma, mb, mc = sum(a) / len(a), sum(b) / len(b), sum(c) / len(c)
            cX += [x - ma for x in a]; cY += [x - mb for x in b]; cP += [x - mc for x in c]
            per_r.append(pearson(a, b)); per_rho.append(spearman(a, b))
            per_mae.append(sum(abs(x - y) for x, y in zip(a, b)) / len(a))
            per_rp.append(pearson(a, c))
        lines.append(f"| {reading} | {ref} | {len(X)} | {pearson(X, Y):.3f} | {pearson(cX, cY):.3f} | {med(per_r):.3f} | {pos(per_r):.2f} | {med(per_rho):.3f} | {med(per_mae):.3f} | {partial(X, P, Y):.3f} (centred {partial(cX, cP, cY):.3f}) | {med(per_rp):.3f} (positive {pos(per_rp):.2f}) |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="synth_strict_check.json")
    ap.add_argument("--ref", choices=list(REF_FIELDS), default="full")
    args = ap.parse_args()
    path = os.path.join(DIR, args.file)
    rf = REF_FIELDS[args.ref]
    out = os.path.join(DIR, f"summary_{os.path.splitext(args.file)[0]}_{args.ref}.md")

    d = json.load(open(path, encoding="utf-8"))
    systems = d["systems"]
    lines = [f"# ShadowGen readings on the synthetic known-system study ({args.file}, reference: {args.ref})", "",
             f"Protocol: {d['protocol']}. {d['n_systems']} systems regenerated from the stored seeds "
             f"(trees match the stored study on {sum(s['tree_matches_stored'] for s in systems)} of {len(systems)}); "
             "training log and fresh sample resampled, so this is a replication under resampling, not a reproduction.", ""]
    if args.ref == "unseen":
        shares = [s["n_F_unseen"] / s["n_F"] for s in systems if s.get("n_F_unseen") is not None]
        lines.append(f"Unseen share of the fresh sample: median {med(shares):.2f}, min {min(shares):.2f}, max {max(shares):.2f}; "
                     f"systems with an empty unseen part: {sum(x == 0 for x in shares)}.")
        lines.append("")

    # replication against stored values (full reference only exists in the stored study)
    diffs = {k: [] for k in ("graded", "true_recall", "true_precision", "m2")}
    for s in systems:
        for m, v in s["models"].items():
            if v.get("error") is not None:
                continue
            for k, ks in (("graded", "graded_stored"), ("true_recall", "true_recall_stored"),
                          ("true_precision", "true_precision_stored"), ("m2", "m2_stored")):
                if v.get(k) is not None and v.get(ks) is not None:
                    diffs[k].append(abs(v[k] - v[ks]))
    lines.append("## Replication against the stored study (per log-model pair, |fresh - stored|, full reference)\n")
    lines.append("| quantity | n | median | p90 | max |")
    lines.append("|---|---|---|---|---|")
    for k, v in diffs.items():
        if v:
            v2 = sorted(v)
            lines.append(f"| {k} | {len(v)} | {st.median(v2):.4f} | {v2[int(0.9 * (len(v2) - 1))]:.4f} | {max(v2):.4f} |")

    fresh_r, stored_r = [], []
    for s in systems:
        rows = rows_of(s, MINERS, ["graded", "true_recall", "graded_stored", "true_recall_stored"])
        if len(rows) < 3:
            continue
        a, b, c, e = zip(*rows)
        if st.pstdev(b) >= SPREAD_MIN:
            fresh_r.append(pearson(a, b))
        if st.pstdev(e) >= SPREAD_MIN:
            stored_r.append(pearson(c, e))
    lines.append(f"\nGraded reading, per-system Pearson with full true recall over the six miners, discriminating systems (sd >= {SPREAD_MIN}): "
                 f"fresh median {med(fresh_r):.3f} (n={len(clean(fresh_r))}, positive {pos(fresh_r):.2f}); "
                 f"stored median {med(stored_r):.3f} (n={len(clean(stored_r))}, positive {pos(stored_r):.2f}).")

    lines.append(f"\n## Both readings against the {args.ref} reference and true precision\n")
    lines.append("Pooled r over all pairs; centred r after subtracting each system's mean; per-system medians over systems with at least 3 models. "
                 "The partial correlation asks whether the score still tracks true precision once the reference recall is held fixed.")
    block(systems, MINERS, "discriminating systems, six discovered nets", lines, rf, True)
    block(systems, MINERS, "all systems, six discovered nets", lines, rf, False)
    block(systems, MINERS + POLES, "all systems, eight models including the poles", lines, rf, False)

    lines.append("\n## Per miner across systems\n")
    lines.append("| miner | n | graded~ref | graded~precision | partial(graded, precision given ref) | strict~ref_strict | strict~precision | partial(strict, precision given ref_strict) | mean ref | mean ref strict | mean precision | mean graded | mean strict |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for m in MINERS + POLES:
        rows = []
        for s in systems:
            v = s["models"].get(m)
            if v and v.get("error") is None and all(v.get(f) is not None for f in ("graded", "strict", rf["graded"], rf["strict"], "true_precision")):
                rows.append((v["graded"], v["strict"], v[rf["graded"]], v[rf["strict"]], v["true_precision"]))
        if len(rows) < 3:
            continue
        g, sc, r, rs, p = zip(*rows)
        lines.append(f"| {m} | {len(rows)} | {pearson(g, r):.3f} | {pearson(g, p):.3f} | {partial(g, p, r):.3f} | {pearson(sc, rs):.3f} | {pearson(sc, p):.3f} | {partial(sc, p, rs):.3f} | {sum(r)/len(r):.3f} | {sum(rs)/len(rs):.3f} | {sum(p)/len(p):.3f} | {sum(g)/len(g):.3f} | {sum(sc)/len(sc):.3f} |")

    fl = [s["models"]["Flower"] for s in systems if s["models"].get("Flower") and s["models"]["Flower"].get("error") is None and s["models"]["Flower"].get(rf["graded"]) is not None]
    tr = [s["models"]["Trace_Filtered"] for s in systems if s["models"].get("Trace_Filtered") and s["models"]["Trace_Filtered"].get("error") is None and s["models"]["Trace_Filtered"].get(rf["graded"]) is not None]
    lines.append("\n## Poles\n")
    lines.append(f"Flower (n={len(fl)}): graded mean {st.mean(v['graded'] for v in fl):.4f} (min {min(v['graded'] for v in fl):.4f}), strict mean {st.mean(v['strict'] for v in fl):.4f} (min {min(v['strict'] for v in fl):.4f}), "
                 f"reference {st.mean(v[rf['graded']] for v in fl):.3f}, reference strict {st.mean(v[rf['strict']] for v in fl):.3f}, true precision {st.mean(v['true_precision'] for v in fl if v.get('true_precision') is not None):.3f}.")
    lines.append(f"Trace model (n={len(tr)}): graded mean {st.mean(v['graded'] for v in tr):.3f}, strict mean {st.mean(v['strict'] for v in tr):.3f}, "
                 f"reference {st.mean(v[rf['graded']] for v in tr):.3f}, reference strict {st.mean(v[rf['strict']] for v in tr):.3f}, "
                 f"true precision {st.mean(v['true_precision'] for v in tr if v.get('true_precision') is not None):.3f}.")

    strict_vals = [v["strict"] for s in systems for m, v in s["models"].items() if m in MINERS and v.get("error") is None and v.get("strict") is not None]
    lines.append(f"\nStrict reading over the six miners: share of pairs at exactly 0: {sum(x == 0 for x in strict_vals)/len(strict_vals):.2f}, at exactly 1: {sum(x == 1 for x in strict_vals)/len(strict_vals):.2f}, n={len(strict_vals)}.")

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
