"""Sensitivity analysis: reject shadow traces that break a count bound of the training log.

Bound of activity a: min and max of count(a) over the training traces. A shadow trace keeps the bounds if every
activity count lies within them (absent activities count 0). The v2.6 generator already rejects walks that repeat a
seen variant; this adds the bound as a second rejection rule without touching the generator: draws continue from the
same seeded stream (batches of 1,000, seed 42 once) and the first 1,000 bound-keeping traces form the shadow log,
which is the generator's distribution conditioned on the bounds.

Mode "split" (default): temporal 70/30 by case start and random 70/30 (seed 0); six miners on the training split;
reference = replay fitness of the test cases whose variant is absent from training; one shadow log (K=1) as the score.
Also reported: the share of real unseen test cases that break the training bounds (the risk of the rule).
Mode "r1": full log, cached benchmark nets (in-memory discovery where the cache does not reproduce the stored cell),
5 draws, against the stored R1 and R1-accept (read only).

Output: results/count_bound/<key>_<split>.json, r1_<key>.json, summary_split.md, summary_r1.md (new folder).
Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/count_bound_check.py D1 D2 D3 D5
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/count_bound_check.py --r1 D1 D2 D3 D5 D4
"""
import os
import sys
import json
import time
import random
from collections import Counter

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
from datasets import DATASETS, get_log_path  # noqa: E402
from temporal_holdout import temporal_split, variants  # noqa: E402
from temporal_drift_screen import random_split  # noqa: E402
from singleton_weighting import criteria  # noqa: E402
from singleton_weighting_r1 import stored  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "count_bound")
CFG = os.path.join(_HERE, "results", "configs")
LKEY = {"D1": "L1", "D2": "L2", "D3": "L3", "D4": "L4", "D5": "L5"}
SIX = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
GEN_KW = dict(num_traces=1000, safe_threshold=5, max_n=6, successor_weighting="mle")
MAX_BATCHES = 50


def act(t):
    return tuple(e["concept:name"] for e in t)


def bounds(vc):
    alpha = sorted({a for v in vc for a in v})
    cnts = [Counter(v) for v in vc]
    return {a: (min(c.get(a, 0) for c in cnts), max(c.get(a, 0) for c in cnts)) for a in alpha}


def keeps(seq, bd):
    c = Counter(seq)
    if any(a not in bd for a in c):
        return False
    return all(lo <= c.get(a, 0) <= hi for a, (lo, hi) in bd.items())


def violation_kind(seq, bd):
    c = Counter(seq)
    over = any(c[a] > bd.get(a, (0, 0))[1] for a in c)
    under = any(c.get(a, 0) < lo for a, (lo, _) in bd.items())
    return over, under


def draw_logs(log, bd, n_logs, gen):
    """Seed once; original logs = consecutive batches; bounded logs = first 1,000 bound-keeping traces per log."""
    random.seed(42)
    np.random.seed(42)
    orig, bounded, info = [], [], []
    pending, drawn, consumed = [], 0, 0
    for k in range(n_logs):
        sh, *_ = gen(log, **GEN_KW)
        orig.append(sh)
    # bounded stream restarts from the same seed, so its first batch equals the first original log
    random.seed(42)
    np.random.seed(42)
    for k in range(n_logs):
        keep = []
        while len(keep) < GEN_KW["num_traces"]:
            if not pending:
                if drawn >= MAX_BATCHES * GEN_KW["num_traces"] * n_logs:
                    break
                sh, *_ = gen(log, **GEN_KW)
                pending = list(sh)
                drawn += len(sh)
            t = pending.pop(0)
            consumed += 1
            if keeps(act(t), bd):
                keep.append(t)
        bounded.append(EventLog(keep))
        info.append(len(keep))
    return orig, bounded, {"drawn": drawn, "kept_per_log": info, "consumed": consumed,
                                   "acceptance": sum(info) / consumed if consumed else None}


def replay_stats(sh, net, im, fm):
    rs = token_replay.apply(sh, net, im, fm)
    return float(np.mean([r["trace_fitness"] for r in rs])), float(np.mean([1.0 if r["trace_is_fit"] else 0.0 for r in rs]))


def process_split(dkey, split):
    t0 = time.time()
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    train, test = temporal_split(log)[:2] if split == "temporal" else random_split(log, seed=0)
    vtr, vte = variants(train), variants(test)
    reps = {}
    for t in log:
        reps.setdefault(act(t), t)
    un = [v for v in vte if v not in vtr]
    uw = np.array([vte[v] for v in un], float)
    bd = bounds(vtr)
    kinds = [violation_kind(v, bd) for v in un]
    gen = load_algorithm("v2.6").generate_shadow_log
    orig, bnd, info = draw_logs(train, bd, 1, gen)
    o, b = orig[0], bnd[0]
    ok = np.array([keeps(act(t), bd) for t in o])
    rec = {"log": LKEY[dkey], "split": split, "n_unseen_cases": int(uw.sum()),
           "binding_bounds": {a: v for a, v in bd.items() if v[0] > 0 or v[1] < 50},
           "unseen_breaking": {"any": float(np.dot([x[0] or x[1] for x in kinds], uw) / uw.sum()),
                               "over_max": float(np.dot([x[0] for x in kinds], uw) / uw.sum()),
                               "under_min": float(np.dot([x[1] for x in kinds], uw) / uw.sum())},
           "shadow_breaking": float(1 - ok.mean()), "generation": info,
           "len_mean": {"shadow": float(np.mean([len(t) for t in o])), "bounded": float(np.mean([len(t) for t in b])),
                        "unseen": float(np.dot([len(v) for v in un], uw) / uw.sum())}, "miners": {}}
    print(f"\n=== {rec['log']} {split}: shadow breaking {rec['shadow_breaking']:.3f}; unseen cases breaking {rec['unseen_breaking']['any']:.3f} "
          f"(over max {rec['unseen_breaking']['over_max']:.3f}, under min {rec['unseen_breaking']['under_min']:.3f}); acceptance {info['acceptance']:.3f}; "
          f"length shadow {rec['len_mean']['shadow']:.1f} bounded {rec['len_mean']['bounded']:.1f} unseen {rec['len_mean']['unseen']:.1f} [{time.time() - t0:.0f}s]", flush=True)
    for mn in SIX:
        tm = time.time()
        net, im, fm = MINERS[mn](train)
        ru = token_replay.apply(EventLog([reps[k] for k in un]), net, im, fm)
        ref = float(np.dot([r["trace_fitness"] for r in ru], uw) / uw.sum())
        ref_s = float(np.dot([1.0 if r["trace_is_fit"] else 0.0 for r in ru], uw) / uw.sum())
        s, a = replay_stats(o, net, im, fm)
        sb, ab = replay_stats(b, net, im, fm)
        rec["miners"][mn] = {"ref": ref, "ref_strict": ref_s, "score": s, "score_bounded": sb, "accept": a, "accept_bounded": ab}
        print(f"  {mn:21s} ref {ref:.3f} score {s:.3f} ({s - ref:+.3f}) bounded {sb:.3f} ({sb - ref:+.3f}) | strict ref {ref_s:.3f} "
              f"score {a:.3f} bounded {ab:.3f} [{time.time() - tm:.0f}s]", flush=True)
    refs = [rec["miners"][m]["ref"] for m in SIX]
    refs_s = [rec["miners"][m]["ref_strict"] for m in SIX]
    rec["criteria"] = {k: criteria([rec["miners"][m][k] for m in SIX], refs) for k in ("score", "score_bounded")}
    if np.std(refs_s) > 1e-9:
        rec["criteria_strict"] = {k: criteria([rec["miners"][m][k] for m in SIX], refs_s) for k in ("accept", "accept_bounded")}
    for k in ("score", "score_bounded"):
        c = rec["criteria"][k]
        print(f"  {k:14s} Pearson {c['pearson']:.3f} Spearman {c['spearman']:.2f} MAE {c['mae']:.3f} spread {c['spread']:.2f}/{c['spread_ref']:.2f} max dev {c['max_abs_dev']:.3f}", flush=True)
    rec["seconds"] = time.time() - t0
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"{dkey}_{split}.json"), "w", encoding="utf-8") as fp:
        json.dump(rec, fp, indent=1)


def process_r1(dkey):
    t0 = time.time()
    ds = DATASETS[dkey]["name"]
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    bd = bounds(variants(log))
    gen = load_algorithm("v2.6").generate_shadow_log
    orig, bnd, info = draw_logs(log, bd, 5, gen)
    rec = {"log": LKEY[dkey], "dataset": ds, "generation": info,
           "shadow_breaking": float(np.mean([1 - np.mean([keeps(act(t), bd) for t in o]) for o in orig])),
           "len_mean": {"shadow": float(np.mean([len(t) for o in orig for t in o])), "bounded": float(np.mean([len(t) for b in bnd for t in b]))},
           "miners": {}}
    print(f"\n=== {rec['log']} R1: shadow breaking {rec['shadow_breaking']:.3f}; acceptance {info['acceptance']:.3f}; length shadow "
          f"{rec['len_mean']['shadow']:.1f} bounded {rec['len_mean']['bounded']:.1f} [{time.time() - t0:.0f}s]", flush=True)
    for mn in SIX:
        tm = time.time()
        m1g, r1 = stored(ds, mn, "M1g"), stored(ds, mn, "R1")
        p = os.path.join(CFG, f"{ds}__{mn}__R1accept.json")
        r1a = stored(ds, mn, "R1accept") if os.path.exists(p) else None
        net, im, fm = pm4py.read_pnml(os.path.join(_HERE, "models", dkey, f"{mn}.pnml"))
        so = [replay_stats(o, net, im, fm) for o in orig]
        source = "cached PNML"
        if abs(np.mean([x[0] for x in so]) - m1g["mean"]) > 0.001:
            net2, im2, fm2 = MINERS[mn](log)
            so2 = [replay_stats(o, net2, im2, fm2) for o in orig]
            if abs(np.mean([x[0] for x in so2]) - m1g["mean"]) < abs(np.mean([x[0] for x in so]) - m1g["mean"]):
                net, im, fm, so, source = net2, im2, fm2, so2, "in-memory discovery"
        sb = [replay_stats(b, net, im, fm) for b in bnd]
        row = {"r1": r1["mean"], "r1_accept": r1a.get("accept_mean", r1a.get("mean")) if r1a else None, "m1g_stored": m1g["mean"],
               "score": float(np.mean([x[0] for x in so])), "score_bounded": float(np.mean([x[0] for x in sb])),
               "accept": float(np.mean([x[1] for x in so])), "accept_bounded": float(np.mean([x[1] for x in sb])), "net_source": source}
        rec["miners"][mn] = row
        print(f"  {mn:21s} R1 {row['r1']:.3f} | stored {row['m1g_stored']:.3f} fresh {row['score']:.3f} bounded {row['score_bounded']:.3f} | gap "
              f"{row['score'] - row['r1']:+.3f} -> {row['score_bounded'] - row['r1']:+.3f} | accept {row['accept']:.3f} bounded {row['accept_bounded']:.3f} "
              f"R1-accept {row['r1_accept']} ({source}) [{time.time() - tm:.0f}s]", flush=True)
    r1v = [rec["miners"][m]["r1"] for m in SIX]
    rec["criteria"] = {k: criteria([rec["miners"][m][k] for m in SIX], r1v) for k in ("m1g_stored", "score", "score_bounded")}
    r1a = [rec["miners"][m]["r1_accept"] for m in SIX]
    if all(x is not None for x in r1a) and np.std(r1a) > 1e-9:
        rec["criteria_accept"] = {k: criteria([rec["miners"][m][k] for m in SIX], r1a) for k in ("accept", "accept_bounded")}
    for k in ("m1g_stored", "score", "score_bounded"):
        c = rec["criteria"][k]
        print(f"  {k:14s} Pearson {c['pearson']:.3f} Spearman {c['spearman']:.2f} MAE {c['mae']:.3f} spread {c['spread']:.2f}/{c['spread_ref']:.2f} max dev {c['max_abs_dev']:.3f}", flush=True)
    rec["seconds"] = time.time() - t0
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"r1_{dkey}.json"), "w", encoding="utf-8") as fp:
        json.dump(rec, fp, indent=1)


def summarize():
    L = ["# Count-bound rejection of shadow traces (sensitivity analysis)", "",
         "| log | split | shadow breaking | unseen cases breaking (over max / under min) | length shadow / bounded / unseen | score | Pearson | Spearman | MAE | spread (ref) | max dev |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in ("D1", "D2", "D3", "D4", "D5"):
        for s in ("temporal", "random"):
            p = os.path.join(OUT_DIR, f"{k}_{s}.json")
            if not os.path.exists(p):
                continue
            r = json.load(open(p, encoding="utf-8"))
            u, lm = r["unseen_breaking"], r["len_mean"]
            for key, lab in (("score", "original"), ("score_bounded", "bounded")):
                c = r["criteria"][key]
                head = (f"| {r['log']} | {s} | {r['shadow_breaking']:.3f} | {u['any']:.3f} ({u['over_max']:.3f} / {u['under_min']:.3f}) | "
                        f"{lm['shadow']:.1f} / {lm['bounded']:.1f} / {lm['unseen']:.1f} |") if key == "score" else "| | | | | |"
                L.append(f"{head} {lab} | {c['pearson']:.3f} | {c['spearman']:.2f} | {c['mae']:.3f} | {c['spread']:.2f} ({c['spread_ref']:.2f}) | {c['max_abs_dev']:.3f} |")
            for key, lab in (("accept", "strict original"), ("accept_bounded", "strict bounded")):
                if "criteria_strict" in r:
                    c = r["criteria_strict"][key]
                    L.append(f"| | | | | | {lab} | {c['pearson']:.3f} | {c['spearman']:.2f} | {c['mae']:.3f} | {c['spread']:.2f} ({c['spread_ref']:.2f}) | {c['max_abs_dev']:.3f} |")
    L += ["", "## Per miner, graded (score minus reference)", "", "| log | split | miner | reference | original | bounded |", "|---|---|---|---|---|---|"]
    for k in ("D1", "D2", "D3", "D4", "D5"):
        for s in ("temporal", "random"):
            p = os.path.join(OUT_DIR, f"{k}_{s}.json")
            if os.path.exists(p):
                r = json.load(open(p, encoding="utf-8"))
                for m in SIX:
                    x = r["miners"][m]
                    L.append(f"| {r['log']} | {s} | {m} | {x['ref']:.3f} | {x['score'] - x['ref']:+.3f} | {x['score_bounded'] - x['ref']:+.3f} |")
    open(os.path.join(OUT_DIR, "summary_split.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    L = ["# Count-bound rejection against R1", "", "| log | shadow breaking | acceptance | length shadow / bounded | score | Pearson | Spearman | MAE | spread (R1) | max dev |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for k in ("D1", "D2", "D3", "D4", "D5"):
        p = os.path.join(OUT_DIR, f"r1_{k}.json")
        if not os.path.exists(p):
            continue
        r = json.load(open(p, encoding="utf-8"))
        for key, lab in (("m1g_stored", "stored"), ("score", "fresh"), ("score_bounded", "bounded")):
            c = r["criteria"][key]
            head = (f"| {r['log']} | {r['shadow_breaking']:.3f} | {r['generation']['acceptance']:.3f} | {r['len_mean']['shadow']:.1f} / {r['len_mean']['bounded']:.1f} |"
                    if key == "m1g_stored" else "| | | | |")
            L.append(f"{head} {lab} | {c['pearson']:.3f} | {c['spearman']:.2f} | {c['mae']:.3f} | {c['spread']:.2f} ({c['spread_ref']:.2f}) | {c['max_abs_dev']:.3f} |")
        for key, lab in (("accept", "strict fresh"), ("accept_bounded", "strict bounded")):
            if "criteria_accept" in r:
                c = r["criteria_accept"][key]
                L.append(f"| | | | | {lab} | {c['pearson']:.3f} | {c['spearman']:.2f} | {c['mae']:.3f} | {c['spread']:.2f} ({c['spread_ref']:.2f}) | {c['max_abs_dev']:.3f} |")
    L += ["", "## Per miner (score minus R1)", "", "| log | miner | R1 | fresh | bounded | net |", "|---|---|---|---|---|---|"]
    for k in ("D1", "D2", "D3", "D4", "D5"):
        p = os.path.join(OUT_DIR, f"r1_{k}.json")
        if os.path.exists(p):
            r = json.load(open(p, encoding="utf-8"))
            for m in SIX:
                x = r["miners"][m]
                L.append(f"| {r['log']} | {m} | {x['r1']:.3f} | {x['score'] - x['r1']:+.3f} | {x['score_bounded'] - x['r1']:+.3f} | {x['net_source']} |")
    open(os.path.join(OUT_DIR, "summary_r1.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


def main():
    keys = [a for a in sys.argv[1:] if a.startswith("D")] or ["D1", "D2", "D3", "D5"]
    if "--summary" not in sys.argv:
        for k in keys:
            try:
                if "--r1" in sys.argv:
                    process_r1(k)
                else:
                    for s in ("temporal", "random"):
                        process_split(k, s)
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                print(f"[{k}] FAIL {type(e).__name__}: {e}", flush=True)
    summarize()


if __name__ == "__main__":
    main()
