"""Resubstitution check for the count-bound test: does plain fitness on the full log already match R1?

If the bounded shadow log only moved ShadowGen toward the fitness of the log it was trained on, the gain against R1 would
say nothing about generalization. This script replays one representative trace per variant of the full log on the
benchmark net (cached PNML; L2 Alpha+ by in-memory discovery, since its cache does not reproduce the stored cell) and
reports four resubstitution readings: case-weighted mean trace fitness, variant mean, singleton-variant mean, and
token-aggregated log fitness (the aggregation R1 uses on held-out cases). They are set against R1 and against the
fresh and bounded ShadowGen scores from results/count_bound/r1_<key>.json (read only).

With --split, the same readings are taken on the training split (nets rediscovered on it) and set against the unseen-only
reference of results/count_bound/<key>_<split>.json (read only), for the temporal and the random split.

Output: results/count_bound/resub_<key>.json, summary_resub.md; with --split resub_<key>_<split>.json, summary_resub_split.md.
Run from the repo root:  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/resub_check.py D1 D2 D3 D5
                         PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/resub_check.py --split D1 D2 D3 D5
"""
import os
import sys
import json
import time

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
from temporal_holdout import variants  # noqa: E402
from singleton_weighting import criteria  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "count_bound")
SIX = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
READINGS = ("resub_case", "resub_variant", "resub_singleton", "resub_token")


def act(t):
    return tuple(e["concept:name"] for e in t)


def process(dkey):
    t0 = time.time()
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    vc = variants(log)
    reps = {}
    for t in log:
        reps.setdefault(act(t), t)
    keys = list(vc)
    cnt = np.array([vc[k] for k in keys], float)
    single = cnt == 1
    vlog = EventLog([reps[k] for k in keys])
    cb = json.load(open(os.path.join(OUT_DIR, f"r1_{dkey}.json"), encoding="utf-8"))
    rec = {"log": cb["log"], "dataset": DATASETS[dkey]["name"], "n_variants": len(keys), "miners": {}}
    print(f"\n=== {rec['log']}: {len(keys)} variants, {int(single.sum())} singletons [{time.time() - t0:.0f}s]", flush=True)
    for mn in SIX:
        tm = time.time()
        if dkey == "D2" and mn == "Alpha+":
            net, im, fm = MINERS[mn](log)
            source = "in-memory discovery"
        else:
            net, im, fm = pm4py.read_pnml(os.path.join(_HERE, "models", dkey, f"{mn}.pnml"))
            source = "cached PNML"
        rs = token_replay.apply(vlog, net, im, fm)
        f = np.array([r["trace_fitness"] for r in rs])
        m = np.array([r["missing_tokens"] for r in rs], float)
        c = np.array([r["consumed_tokens"] for r in rs], float)
        r_ = np.array([r["remaining_tokens"] for r in rs], float)
        p = np.array([r["produced_tokens"] for r in rs], float)
        row = {"resub_case": float(np.dot(cnt, f) / cnt.sum()), "resub_variant": float(f.mean()),
               "resub_singleton": float(f[single].mean()),
               "resub_token": float(0.5 * (1 - np.dot(cnt, m) / np.dot(cnt, c)) + 0.5 * (1 - np.dot(cnt, r_) / np.dot(cnt, p))),
               "r1": cb["miners"][mn]["r1"], "score": cb["miners"][mn]["score"], "score_bounded": cb["miners"][mn]["score_bounded"],
               "net_source": source}
        rec["miners"][mn] = row
        print(f"  {mn:21s} R1 {row['r1']:.3f} | resub case {row['resub_case']:.3f} variant {row['resub_variant']:.3f} "
              f"singleton {row['resub_singleton']:.3f} token {row['resub_token']:.3f} | ShadowGen {row['score']:.3f} bounded "
              f"{row['score_bounded']:.3f} [{time.time() - tm:.0f}s]", flush=True)
    r1v = [rec["miners"][m]["r1"] for m in SIX]
    rec["criteria"] = {k: criteria([rec["miners"][m][k] for m in SIX], r1v) for k in READINGS + ("score", "score_bounded")}
    rec["seconds"] = time.time() - t0
    rec["protocol"] = f"one representative per variant, cached nets benchmark/models/{dkey}; pm4py {pm4py.__version__}"
    with open(os.path.join(OUT_DIR, f"resub_{dkey}.json"), "w", encoding="utf-8") as fp:
        json.dump(rec, fp, indent=1)


def resub_readings(log_part, net, im, fm):
    """Replay one representative per variant of log_part; return the four graded readings and two strict ones."""
    vc = variants(log_part)
    reps = {}
    for t in log_part:
        reps.setdefault(act(t), t)
    keys = list(vc)
    cnt = np.array([vc[k] for k in keys], float)
    single = cnt == 1
    rs = token_replay.apply(EventLog([reps[k] for k in keys]), net, im, fm)
    f = np.array([r["trace_fitness"] for r in rs])
    ok = np.array([1.0 if r["trace_is_fit"] else 0.0 for r in rs])
    m = np.array([r["missing_tokens"] for r in rs], float)
    c = np.array([r["consumed_tokens"] for r in rs], float)
    r_ = np.array([r["remaining_tokens"] for r in rs], float)
    p = np.array([r["produced_tokens"] for r in rs], float)
    return {"resub_case": float(np.dot(cnt, f) / cnt.sum()), "resub_variant": float(f.mean()),
            "resub_singleton": float(f[single].mean()) if single.any() else None,
            "resub_token": float(0.5 * (1 - np.dot(cnt, m) / np.dot(cnt, c)) + 0.5 * (1 - np.dot(cnt, r_) / np.dot(cnt, p))),
            "resub_case_strict": float(np.dot(cnt, ok) / cnt.sum()),
            "resub_singleton_strict": float(ok[single].mean()) if single.any() else None}


def process_split(dkey, split):
    """Training-split fitness against the unseen-only reference of results/count_bound/<key>_<split>.json (read only)."""
    from temporal_holdout import temporal_split
    from temporal_drift_screen import random_split
    t0 = time.time()
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    train = temporal_split(log)[0] if split == "temporal" else random_split(log, seed=0)[0]
    cb = json.load(open(os.path.join(OUT_DIR, f"{dkey}_{split}.json"), encoding="utf-8"))
    rec = {"log": cb["log"], "split": split, "miners": {}}
    print(f"\n=== {rec['log']} {split}: {len(train)} training cases [{time.time() - t0:.0f}s]", flush=True)
    for mn in SIX:
        tm = time.time()
        net, im, fm = MINERS[mn](train)
        row = resub_readings(train, net, im, fm)
        x = cb["miners"][mn]
        row.update({"ref": x["ref"], "ref_strict": x["ref_strict"], "score": x["score"], "score_bounded": x["score_bounded"],
                    "accept": x["accept"], "accept_bounded": x["accept_bounded"]})
        rec["miners"][mn] = row
        print(f"  {mn:21s} ref {row['ref']:.3f} | resub case {row['resub_case']:.3f} singleton {row['resub_singleton']:.3f} token "
              f"{row['resub_token']:.3f} | ShadowGen {row['score']:.3f} bounded {row['score_bounded']:.3f} | strict ref {row['ref_strict']:.3f} "
              f"resub {row['resub_case_strict']:.3f} singleton {row['resub_singleton_strict']:.3f} accept {row['accept']:.3f} "
              f"bounded {row['accept_bounded']:.3f} [{time.time() - tm:.0f}s]", flush=True)
    refs = [rec["miners"][m]["ref"] for m in SIX]
    rec["criteria"] = {k: criteria([rec["miners"][m][k] for m in SIX], refs) for k in READINGS + ("score", "score_bounded")}
    refs_s = [rec["miners"][m]["ref_strict"] for m in SIX]
    if np.std(refs_s) > 1e-9:
        rec["criteria_strict"] = {k: criteria([rec["miners"][m][k] for m in SIX], refs_s)
                                  for k in ("resub_case_strict", "resub_singleton_strict", "accept", "accept_bounded")}
    rec["seconds"] = time.time() - t0
    with open(os.path.join(OUT_DIR, f"resub_{dkey}_{split}.json"), "w", encoding="utf-8") as fp:
        json.dump(rec, fp, indent=1)


def summarize_split():
    L = ["# Training-split fitness against the unseen-only reference (count-bound test, control)", "",
         "| log | split | score | Pearson | Spearman | MAE | spread (ref) | max dev |", "|---|---|---|---|---|---|---|---|"]
    labels = {"resub_case": "resub, case-weighted", "resub_variant": "resub, variant mean", "resub_singleton": "resub, singleton mean",
              "resub_token": "resub, token-aggregated", "score": "ShadowGen", "score_bounded": "ShadowGen bounded"}
    slabels = {"resub_case_strict": "strict resub, case-weighted", "resub_singleton_strict": "strict resub, singleton mean",
               "accept": "strict ShadowGen", "accept_bounded": "strict ShadowGen bounded"}
    for k in ("D1", "D2", "D3", "D4", "D5"):
        for s in ("temporal", "random"):
            p = os.path.join(OUT_DIR, f"resub_{k}_{s}.json")
            if not os.path.exists(p):
                continue
            r = json.load(open(p, encoding="utf-8"))
            rows = [(r["criteria"][q], lab) for q, lab in labels.items()]
            rows += [(r["criteria_strict"][q], lab) for q, lab in slabels.items()] if "criteria_strict" in r else []
            for i, (c, lab) in enumerate(rows):
                L.append(f"| {r['log'] if i == 0 else ''} | {s if i == 0 else ''} | {lab} | {c['pearson']:.3f} | {c['spearman']:.2f} | "
                         f"{c['mae']:.3f} | {c['spread']:.2f} ({c['spread_ref']:.2f}) | {c['max_abs_dev']:.3f} |")
    open(os.path.join(OUT_DIR, "summary_resub_split.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def summarize():
    L = ["# Resubstitution fitness against R1 (count-bound test, control)", "",
         "| log | score | Pearson | Spearman | MAE | spread (R1) | max dev |", "|---|---|---|---|---|---|---|"]
    labels = {"resub_case": "resub, case-weighted", "resub_variant": "resub, variant mean", "resub_singleton": "resub, singleton mean",
              "resub_token": "resub, token-aggregated", "score": "ShadowGen", "score_bounded": "ShadowGen bounded"}
    per = ["", "## Per miner (minus R1)", "", "| log | miner | R1 | resub case | resub variant | resub singleton | resub token | ShadowGen | bounded |",
           "|---|---|---|---|---|---|---|---|---|"]
    for k in ("D1", "D2", "D3", "D4", "D5"):
        p = os.path.join(OUT_DIR, f"resub_{k}.json")
        if not os.path.exists(p):
            continue
        r = json.load(open(p, encoding="utf-8"))
        for i, (key, lab) in enumerate(labels.items()):
            c = r["criteria"][key]
            L.append(f"| {r['log'] if i == 0 else ''} | {lab} | {c['pearson']:.3f} | {c['spearman']:.2f} | {c['mae']:.3f} | "
                     f"{c['spread']:.2f} ({c['spread_ref']:.2f}) | {c['max_abs_dev']:.3f} |")
        for m in SIX:
            x = r["miners"][m]
            per.append(f"| {r['log']} | {m} | {x['r1']:.3f} | " + " | ".join(f"{x[q] - x['r1']:+.3f}" for q in READINGS + ("score", "score_bounded")) + " |")
    open(os.path.join(OUT_DIR, "summary_resub.md"), "w", encoding="utf-8").write("\n".join(L + per) + "\n")
    print("\n".join(L + per))


def main():
    keys = [a for a in sys.argv[1:] if a.startswith("D")] or ["D1", "D2", "D3", "D5"]
    split_mode = "--split" in sys.argv
    if "--summary" not in sys.argv:
        for k in keys:
            try:
                if split_mode:
                    for s in ("temporal", "random"):
                        process_split(k, s)
                else:
                    process(k)
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                print(f"[{k}] FAIL {type(e).__name__}: {e}", flush=True)
    summarize_split() if split_mode else summarize()


if __name__ == "__main__":
    main()
