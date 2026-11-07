"""Why does ShadowGen undershoot Alpha+ on L1 and L2?

Score and reference on the same net: discover on the training split (temporal 70/30 by case start, or random 70/30
with seed 0), regenerate the shadow log exactly as the v2.6 core does (seed 42, N=6, tau=5, mle, 1,000 traces),
replay it, and replay the test cases whose variant is absent from training. Per trace: length, fitness, the missing
and remaining token terms of the fitness, mutated flag, and the transitions with missing tokens.

Reported per (log, split, miner): score, reference, gap; length distributions; fitness by length bin; the shadow score
reweighted to the reference's length distribution; the gap split into the missing and remaining token terms; for
Alpha+ the activities whose replay problems differ most between shadow and unseen traces.

Output: results/alphaplus_check/<key>_<split>.json and summary_<keys>.md (new folder).
Run from the repo root:  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/alphaplus_check.py D1 D2 D3
"""
import os
import sys
import json
import time
import random
from collections import Counter, defaultdict

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["TQDM_DISABLE"] = "1"
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, _HERE)

import numpy as np  # noqa: E402
import pm4py  # noqa: E402
from pm4py.objects.log.obj import EventLog  # noqa: E402
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay  # noqa: E402

from miners import MINERS  # noqa: E402
from datasets import get_log_path  # noqa: E402
from temporal_holdout import temporal_split, variants  # noqa: E402
from temporal_drift_screen import random_split  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "alphaplus_check")
LKEY = {"D1": "L1", "D2": "L2", "D3": "L3", "D4": "L4", "D5": "L5"}
SIX = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
GEN_KW = dict(num_traces=1000, safe_threshold=5, max_n=6, successor_weighting="mle")


def act(t):
    return tuple(e["concept:name"] for e in t)


def per_trace(res, seqs):
    out = []
    for r, s in zip(res, seqs):
        c, p = max(r["consumed_tokens"], 1), max(r["produced_tokens"], 1)
        out.append({"len": len(s), "fit": float(r["trace_fitness"]), "ok": bool(r["trace_is_fit"]),
                    "miss": 0.5 * r["missing_tokens"] / c, "rem": 0.5 * r["remaining_tokens"] / p,
                    "prob": sorted({t.label for t in r["transitions_with_problems"] if t.label is not None}),
                    "acts": sorted(set(s))})
    return out


def wavg(rows, w, key):
    tw = sum(w)
    return sum(r[key] * x for r, x in zip(rows, w)) / tw if tw else None


def qs(vals, w):
    order = np.argsort(vals)
    v, ww = np.asarray(vals, float)[order], np.asarray(w, float)[order]
    cw = np.cumsum(ww) / ww.sum()
    return {q: float(v[np.searchsorted(cw, q)]) for q in (0.1, 0.25, 0.5, 0.75, 0.9)}


def analyse(sh, un, un_w):
    """sh: shadow rows (weight 1 each); un: unseen variant rows, un_w: case counts."""
    sh_w = [1.0] * len(sh)
    rec = {"score": wavg(sh, sh_w, "fit"), "reference": wavg(un, un_w, "fit")}
    rec["gap"] = rec["score"] - rec["reference"]
    rec["len_shadow"] = {"mean": wavg(sh, sh_w, "len"), **qs([r["len"] for r in sh], sh_w)}
    rec["len_unseen"] = {"mean": wavg(un, un_w, "len"), **qs([r["len"] for r in un], un_w)}
    rec["miss_term"] = {"shadow": wavg(sh, sh_w, "miss"), "unseen": wavg(un, un_w, "miss")}
    rec["rem_term"] = {"shadow": wavg(sh, sh_w, "rem"), "unseen": wavg(un, un_w, "rem")}
    # length bins: deciles of the reference's case-weighted length distribution
    lens_u = np.repeat([r["len"] for r in un], un_w)
    edges = np.unique(np.quantile(lens_u, np.linspace(0, 1, 11)))
    edges[-1] = max(edges[-1], max(r["len"] for r in sh)) + 1
    edges[0] = min(edges[0], min(r["len"] for r in sh))

    def b(x):
        return int(min(np.searchsorted(edges, x, side="right") - 1, len(edges) - 2))
    bins = []
    for k in range(len(edges) - 1):
        s_ = [r for r in sh if b(r["len"]) == k]
        u_ = [(r, w) for r, w in zip(un, un_w) if b(r["len"]) == k]
        uw = sum(w for _, w in u_)
        bins.append({"lo": float(edges[k]), "hi": float(edges[k + 1]), "n_shadow": len(s_), "w_unseen": uw,
                     "fit_shadow": float(np.mean([r["fit"] for r in s_])) if s_ else None,
                     "fit_unseen": sum(r["fit"] * w for r, w in u_) / uw if uw else None})
    tot_u = sum(x["w_unseen"] for x in bins)
    cov = [x for x in bins if x["n_shadow"] and x["w_unseen"]]
    cm = sum(x["w_unseen"] for x in cov)
    rec["len_bins"] = bins
    rec["reweighted_score"] = sum(x["fit_shadow"] * x["w_unseen"] for x in cov) / cm if cm else None
    rec["reference_on_covered"] = sum(x["fit_unseen"] * x["w_unseen"] for x in cov) / cm if cm else None
    rec["covered_unseen_mass"] = cm / tot_u if tot_u else None
    rec["within_bin_gap"] = (rec["reweighted_score"] - rec["reference_on_covered"]) if cm else None
    return rec


def problems(sh, un, un_w, top=10):
    """Per activity: share of traces containing it that have a missing-token problem at it, shadow vs unseen."""
    def rate(rows, w):
        has, bad = Counter(), Counter()
        for r, x in zip(rows, w):
            for a in r["acts"]:
                has[a] += x
            for a in r["prob"]:
                bad[a] += x
        tot = sum(w)
        return {a: {"contain": has[a] / tot, "problem": bad[a] / has[a]} for a in has}
    rs, ru = rate(sh, [1.0] * len(sh)), rate(un, un_w)
    acts = sorted(set(rs) | set(ru), key=lambda a: -abs(rs.get(a, {}).get("contain", 0) * rs.get(a, {}).get("problem", 0)
                                                       - ru.get(a, {}).get("contain", 0) * ru.get(a, {}).get("problem", 0)))
    return [{"activity": a, "shadow": rs.get(a), "unseen": ru.get(a)} for a in acts[:top]]


def process(dkey, split, miners):
    t0 = time.time()
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    if split == "temporal":
        train, test, *_ = temporal_split(log)
    else:
        train, test = random_split(log, seed=0)
    vtr, vte = variants(train), variants(test)
    reps = {}
    for t in log:
        reps.setdefault(act(t), t)
    un_keys = [v for v in vte if v not in vtr]
    un_w = [vte[v] for v in un_keys]
    random.seed(42)
    np.random.seed(42)
    shadow, flags, dup, trunc, cap = load_algorithm("v2.6").generate_shadow_log(train, **GEN_KW)
    sh_seqs = [act(t) for t in shadow]
    rec = {"log": LKEY[dkey], "split": split, "n_train": len(train), "n_unseen_cases": sum(un_w),
           "n_unseen_variants": len(un_keys), "shadow": {"n": len(shadow), "mutated": int(sum(flags)), "duplicates_kept": dup,
                                                       "truncated": trunc, "cap": cap,
                                                       "seen_in_train": sum(1 for s in sh_seqs if s in vtr)},
           "len_train": {"mean": sum(len(v) * c for v, c in vtr.items()) / len(train)}, "miners": {}}
    print(f"\n=== {rec['log']} {split}: train {len(train)}, unseen cases {sum(un_w)} ({len(un_keys)} variants), "
          f"shadow {len(shadow)} (mutated {sum(flags)}, seen in train {rec['shadow']['seen_in_train']}) [{time.time() - t0:.0f}s]", flush=True)
    for mn in miners:
        tm = time.time()
        net, im, fm = MINERS[mn](train)
        sh = per_trace(token_replay.apply(shadow, net, im, fm), sh_seqs)
        un = per_trace(token_replay.apply(EventLog([reps[k] for k in un_keys]), net, im, fm), un_keys)
        r = analyse(sh, un, un_w)
        r["score_regular"] = float(np.mean([x["fit"] for x, f in zip(sh, flags) if not f]))
        r["score_mutated"] = float(np.mean([x["fit"] for x, f in zip(sh, flags) if f])) if any(flags) else None
        r["n_transitions"] = len(net.transitions)
        r["n_silent"] = sum(1 for t in net.transitions if t.label is None)
        r["n_places"] = len(net.places)
        lab = Counter(t.label for t in net.transitions if t.label is not None)
        alpha = {e["concept:name"] for tr in train for e in tr}
        r["labels_missing_from_net"] = sorted(alpha - set(lab))
        r["isolated_transitions"] = sorted(t.label or "tau" for t in net.transitions if not t.in_arcs or not t.out_arcs)
        if mn in ("Alpha", "Alpha+"):
            r["problem_activities"] = problems(sh, un, un_w)
        rec["miners"][mn] = r
        print(f"  {mn:21s} score {r['score']:.3f} ref {r['reference']:.3f} gap {r['gap']:+.3f} | len shadow {r['len_shadow']['mean']:.1f} "
              f"unseen {r['len_unseen']['mean']:.1f} | reweighted {r['reweighted_score']:.3f} vs {r['reference_on_covered']:.3f} "
              f"(within-bin gap {r['within_bin_gap']:+.3f}, covered {r['covered_unseen_mass']:.2f}) | miss {r['miss_term']['shadow']:.3f}/"
              f"{r['miss_term']['unseen']:.3f} rem {r['rem_term']['shadow']:.3f}/{r['rem_term']['unseen']:.3f} | reg {r['score_regular']:.3f} "
              f"mut {r['score_mutated']} | missing labels {len(r['labels_missing_from_net'])} isolated {len(r['isolated_transitions'])} "
              f"[{time.time() - tm:.0f}s]", flush=True)
    rec["seconds"] = time.time() - t0
    rec["protocol"] = "v2.6 generate_shadow_log, seed 42, " + str(GEN_KW) + "; pm4py " + pm4py.__version__
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"{dkey}_{split}.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    return rec


def main():
    keys = [a for a in sys.argv[1:] if a.startswith("D")] or ["D1", "D2", "D3"]
    splits = ["temporal", "random"]
    miners = SIX if "--alpha-only" not in sys.argv else ["Alpha", "Alpha+"]
    recs = []
    for k in keys:
        for s in splits:
            try:
                recs.append(process(k, s, miners))
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                print(f"[{k} {s}] FAIL {type(e).__name__}: {e}", flush=True)
    f3 = lambda x: "--" if x is None else f"{x:.3f}"  # noqa: E731
    L = ["# Alpha+ undershoot: score and unseen reference on the same net", "",
         "| log | split | miner | score | reference | gap | len shadow | len unseen | reweighted score | reference on covered bins | within-bin gap | covered | miss term shadow / unseen | rem term shadow / unseen | regular / mutated |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in recs:
        for mn, m in r["miners"].items():
            L.append(f"| {r['log']} | {r['split']} | {mn} | {m['score']:.3f} | {m['reference']:.3f} | {m['gap']:+.3f} | {m['len_shadow']['mean']:.1f} | "
                     f"{m['len_unseen']['mean']:.1f} | {f3(m['reweighted_score'])} | {f3(m['reference_on_covered'])} | {f3(m['within_bin_gap'])} | "
                     f"{f3(m['covered_unseen_mass'])} | {m['miss_term']['shadow']:.3f} / {m['miss_term']['unseen']:.3f} | "
                     f"{m['rem_term']['shadow']:.3f} / {m['rem_term']['unseen']:.3f} | {m['score_regular']:.3f} / {f3(m['score_mutated'])} |")
    for r in recs:
        m = r["miners"].get("Alpha+")
        if not m:
            continue
        L += ["", f"## {r['log']} {r['split']}, Alpha+ by length bin (deciles of the unseen cases)", "",
              "| length | shadow n | unseen cases | fit shadow | fit unseen |", "|---|---|---|---|---|"]
        for x in m["len_bins"]:
            L.append(f"| {x['lo']:.0f} to {x['hi']:.0f} | {x['n_shadow']} | {x['w_unseen']} | {f3(x['fit_shadow'])} | {f3(x['fit_unseen'])} |")
        L += ["", f"Net: {m['n_transitions']} transitions ({m['n_silent']} silent), {m['n_places']} places; labels missing from net "
              f"{m['labels_missing_from_net']}; transitions without input or output arcs {m['isolated_transitions']}", "",
              "| activity | shadow: contain | shadow: problem rate | unseen: contain | unseen: problem rate |", "|---|---|---|---|---|"]
        for x in m["problem_activities"]:
            s, u = x["shadow"] or {}, x["unseen"] or {}
            L.append(f"| {x['activity']} | {f3(s.get('contain'))} | {f3(s.get('problem'))} | {f3(u.get('contain'))} | {f3(u.get('problem'))} |")
    name = "summary_" + "_".join(keys) + ".md"
    open(os.path.join(OUT_DIR, name), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
