"""Overfitting ladder: do fitness and generalization diverge, and does ShadowGen follow?

The six benchmark miners barely overfit: on a random split their acceptance of unseen-variant
future cases stays close to their training fitness (fitness_baseline_check.py). A generalization
measure can only show a direction of its own on models whose fitness and generalization differ.
This script builds two families of such models on the training split, with a ladder over k:

  Trie-k    trace model over the k most frequent training variants, built as a prefix tree
            (axiom_check.build_trie_net). k = all is the full memorizer. Its language is exactly
            the k variants, so the exact strict training fitness is the coverage of those
            variants and the exact strict acceptance of unseen variants is 0. In a prefix tree
            every choice is between different labels, so token replay follows the right branch.
  Trace-k   the benchmark's flat trace model (miners.filtered_trace_miner), same language as
            Trie-k but one separate path per variant. Every path starts in the same place, so
            token replay has to choose among equally labeled transitions and picks a wrong path
            for most traces. Run at k = 50 (the benchmark's Trace_Filtered) and k = all only, to
            document that engine effect.
  IM-k      Inductive Miner (noise 0) discovered from the training cases of the k most frequent
            variants only. The model generalizes from frequent behavior; k = all is the
            benchmark's Inductive_Strict.

Protocol (identical to randomization_test.py at level p = 0, same seeds, so the splits are the
same and Trace-50 / IM-all reproduce the stored Trace_Filtered / Inductive_Strict cells):
  random 70/30 case split; models built on the training split; ShadowGen (graded and strict)
  from the training split and the model; truth = token replay of the future cases whose variant
  is absent from the training split; training fitness = the same replay on the training split.

Output: results/topk_overfit/topk_<key>.json (a .partial.json is written after every model and
resumed from). Nothing else is written.
Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/topk_overfit_test.py D1 D2
  optional: --ks 10,50,100,200,400,all --reps 3 --tag smoke
"""
import os
import sys
import json
import time
import random
import argparse
from collections import defaultdict

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["TQDM_DISABLE"] = "1"
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, _HERE)

import pm4py  # noqa: E402
from pm4py.objects.log.obj import EventLog  # noqa: E402

from miners import filtered_trace_miner  # noqa: E402
from axiom_check import build_trie_net  # noqa: E402
from datasets import DATASETS, get_log_path  # noqa: E402
from randomization_test import randomize, split, acts, avg_fit, score_both  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "topk_overfit")


def variants_by_frequency(log):
    """Variants ordered as in miners.filtered_trace_miner (count descending, stable)."""
    counts = defaultdict(int)
    for t in log:
        counts[acts(t)] += 1
    return [v for v, _ in sorted(counts.items(), key=lambda i: i[1], reverse=True)], counts


def build(family, train, order, k):
    if family == "Trace":
        return filtered_trace_miner(train, top_k=k)
    if family == "Trie":
        net, im, fm, _ = build_trie_net(order[:k])
        return net, im, fm
    keep = set(order[:k])
    sub = EventLog([t for t in train if acts(t) in keep])
    return pm4py.discover_petri_net_inductive(sub, noise_threshold=0.0)


def run_rep(log, rep, ks, done, save):
    rng = random.Random(1000 * rep + 0)              # the p = 0 seed of randomization_test.py
    traces, _ = randomize(log, 0.0, rng)
    train, test = split(traces, rng)
    order, counts = variants_by_frequency(train)
    vtr = set(order)
    unseen = EventLog([t for t in test if acts(t) not in vtr])
    info = {"n_train": len(train), "n_test": len(test), "var_train": len(order),
            "n_test_unseen": len(unseen), "unseen_share": len(unseen) / len(test)}
    print(f"  rep={rep} |train|={len(train)} variants={len(order)} unseen share="
          f"{info['unseen_share']:.3f}", flush=True)
    ladder = sorted({min(k, len(order)) for k in ks if k is not None}) + ([len(order)] if None in ks else [])
    ladder = sorted(set(ladder))
    for family in ("Trie", "IM", "Trace"):
        # flat trace model: k = 50 in every repetition, k = all in repetition 0 only (slow replay)
        for k in (ladder if family != "Trace" else
                  [k for k in ladder if k == 50 or (k == len(order) and rep == 0)]):
            key = f"{rep}|{family}|{k}"
            if key in done:
                continue
            m = {"rep": rep, "family": family, "k": k, "all": k == len(order), "error": None,
                 "coverage": sum(counts[v] for v in order[:k]) / len(train)}
            t0 = time.time()
            try:
                net, im, fm = build(family, train, order, k)
                m["n_transitions"] = len(net.transitions)
                (m["shadowgen"], m["shadowgen_strict"], m["mutated_share"],
                 m["duplicates_kept"]) = score_both(train, net, im, fm)
                m["train_fit"], m["train_fit_strict"] = avg_fit(train, net, im, fm)
                m["unseen_fit"], m["unseen_fit_strict"] = avg_fit(unseen, net, im, fm)
            except Exception as e:  # noqa: BLE001
                m["error"] = f"{type(e).__name__}: {e}"
            m["seconds"] = time.time() - t0
            done[key] = m
            save(info, rep)
            if m["error"]:
                print(f"    {family}-{k:<5d} FAIL {m['error']}", flush=True)
            else:
                print(f"    {family}-{k:<5d} cov={m['coverage']:.3f}  graded fit/truth/sg="
                      f"{m['train_fit']:.3f}/{m['unseen_fit']:.3f}/{m['shadowgen']:.3f}  strict="
                      f"{m['train_fit_strict']:.3f}/{m['unseen_fit_strict']:.3f}/"
                      f"{m['shadowgen_strict']:.3f} [{m['seconds']:.0f}s]", flush=True)


def process(dkey, ks, reps, tag):
    t0 = time.time()
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    os.makedirs(OUT_DIR, exist_ok=True)
    stem = f"topk_{dkey}" + (f"_{tag}" if tag else "")
    partial = os.path.join(OUT_DIR, stem + ".partial.json")
    rec = {"dataset": DATASETS[dkey]["name"], "n_cases": len(log), "reps": reps, "splits": {},
           "models": {}}
    if os.path.exists(partial):
        old = json.load(open(partial, encoding="utf-8"))
        rec["models"], rec["splits"] = old.get("models", {}), old.get("splits", {})
        print(f"  resuming: {len(rec['models'])} models from {partial}", flush=True)
    print(f"\n=== {dkey} {DATASETS[dkey]['name']}: {len(log)} cases, {reps} reps", flush=True)

    def save(info, rep):
        rec["splits"][str(rep)] = info
        with open(partial, "w", encoding="utf-8") as fp:
            json.dump(rec, fp, indent=1)

    for rep in range(reps):
        run_rep(log, rep, ks, rec["models"], save)
    rec["seconds"] = time.time() - t0
    rec["protocol"] = ("random 70/30 case split with the p = 0 seeds of randomization_test.py; IM-k = Inductive Miner "
                       "(noise 0) on the training cases of those variants; ShadowGen seed 42, one "
                       "1,000-trace draw, N=6, tau=5, mle, v2.6 core, scored with the full training "
                       "split; Trie-k = prefix-tree trace model over the k most frequent variants, "
                       "Trace-k = flat trace model (k = 50 and all only); truth = token replay of future cases with a variant absent from "
                       "training; pm4py " + pm4py.__version__)
    path = os.path.join(OUT_DIR, stem + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    os.remove(partial)
    print(f"  [{dkey} done in {rec['seconds']:.0f}s -> {path}]", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*", default=["D1", "D2"])
    ap.add_argument("--ks", default="10,50,100,200,400,all")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    ks = [None if x == "all" else int(x) for x in a.ks.split(",")]
    for k in a.keys:
        try:
            process(k, ks, a.reps, a.tag)
        except Exception as e:  # noqa: BLE001
            print(f"[{k}] DATASET FAIL: {type(e).__name__}: {e}", flush=True)


if __name__ == "__main__":
    main()
