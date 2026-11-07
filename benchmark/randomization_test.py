"""Randomization test for a generalization metric (after Zhang et al., ICLR 2017).

Zhang et al. train the same network on the true data and on a copy with random labels: the
training error stays at 0, the test error falls to chance, and an explanation of generalization
has to tell the two cases apart. The transfer to process models: destroy the control-flow
structure of the log step by step, rediscover the models, and check that the metric follows the
true acceptance of future behavior at every step.

Randomization at level p: a share p of the cases (chosen at random) gets the order of its
activities permuted uniformly at random. Trace length and the activities of a trace are kept,
the ordering information is destroyed. p = 0 is the natural log, p = 1 the fully randomized log.
The system at level p is the natural system followed by this permutation, so a fresh sample of
its future behavior is available: held-out cases randomized by the same mechanism.

Per level and repetition (fixed-model protocol, no rediscovery on the test side):
  1. randomize the log at level p, split the cases 70/30 at random (train / future)
  2. discover the eight models on the training split
  3. metric:    ShadowGen (graded and strict) and PM4Py generalization (M2) from the training
                split and the model only
  4. truth:     token-replay fitness and perfect-replay share of the future cases whose variant
                is absent from the training split (Eq. (1) of the paper, unseen-only reference)
  5. training:  the same replay on the training split (the "training error" side of the gap)

Output: results/randomization/randomization_<key>.json, one file per log; a .partial.json is
written after every (level, repetition) and resumed from. Nothing else is written.
Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/randomization_test.py D1 D2
  optional: --levels 0,0.25,0.5,0.75,1 --reps 3 --tag smoke
"""
import os
import sys
import json
import time
import random
import argparse

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["TQDM_DISABLE"] = "1"
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
sys.path.insert(0, _REPO)
sys.path.insert(0, _HERE)

import numpy as np  # noqa: E402
import pm4py  # noqa: E402
from pm4py.objects.log.obj import EventLog, Trace, Event  # noqa: E402
from pm4py.algo.evaluation.generalization import algorithm as gen_eval  # noqa: E402

from miners import MINERS  # noqa: E402
from datasets import DATASETS, get_log_path  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

try:
    import pm4py.util.constants as _pmc
    _pmc.SHOW_PROGRESS_BAR = False
except Exception:  # noqa: BLE001
    pass

SEED = 42                      # ShadowGen seed, as in temporal_unseen.py
GEN_KW = dict(num_traces=1000, iterations=1, safe_threshold=5, max_n=6, successor_weighting="mle")
TRAIN_FRAC = 0.70
OUT_DIR = os.path.join(_HERE, "results", "randomization")
ACT = "concept:name"


def acts(trace):
    return tuple(e[ACT] for e in trace)


def rebuild(trace, sequence):
    """Copy of the trace with the given activity sequence; timestamps stay in position."""
    t = Trace(attributes=dict(trace.attributes))
    for e, a in zip(trace, sequence):
        ev = Event({ACT: a})
        if "time:timestamp" in e:
            ev["time:timestamp"] = e["time:timestamp"]
        t.append(ev)
    return t


def randomize(log, p, rng):
    """Permute the activity order of round(p * |log|) randomly chosen cases."""
    n = len(log)
    chosen = set(rng.sample(range(n), int(round(p * n))))
    out = []
    for i, tr in enumerate(log):
        seq = list(acts(tr))
        if i in chosen:
            rng.shuffle(seq)
        out.append(rebuild(tr, seq))
    return out, len(chosen)


def split(traces, rng):
    idx = list(range(len(traces)))
    rng.shuffle(idx)
    cut = int(len(idx) * TRAIN_FRAC)
    return EventLog([traces[i] for i in idx[:cut]]), EventLog([traces[i] for i in idx[cut:]])


def avg_fit(log, net, im, fm):
    r = pm4py.fitness_token_based_replay(log, net, im, fm)
    return float(r["average_trace_fitness"]), float(r["perc_fit_traces"]) / 100.0


def score_both(log, net, im, fm):
    random.seed(SEED)
    np.random.seed(SEED)
    r = load_algorithm("v2.6").calculate_gen_shadow_stable(log, net, im, fm, **GEN_KW)
    return (float(r["mean"]), float(r["accept_mean"]),
            sum(r["mutation_counts"]) / float(GEN_KW["num_traces"]), int(r["duplicates_kept"]))


def run_cell(log, p, rep):
    rng = random.Random(1000 * rep + int(round(p * 100)))
    traces, n_perm = randomize(log, p, rng)
    train, test = split(traces, rng)
    vtr = set(acts(t) for t in train)
    unseen = EventLog([t for t in test if acts(t) not in vtr])
    cell = {"p": p, "rep": rep, "n_train": len(train), "n_test": len(test),
            "n_permuted": n_perm, "n_test_unseen": len(unseen),
            "unseen_share": len(unseen) / len(test), "var_train": len(vtr),
            "var_test_unseen": len(set(acts(t) for t in unseen)), "models": {}}
    for mn, fn in MINERS.items():
        m = {"error": None}
        tm = time.time()
        try:
            net, im, fm = fn(train)
            m["n_transitions"] = len(net.transitions)
            (m["shadowgen"], m["shadowgen_strict"], m["mutated_share"],
             m["duplicates_kept"]) = score_both(train, net, im, fm)
            m["train_fit"], m["train_fit_strict"] = avg_fit(train, net, im, fm)
            if len(unseen):
                m["unseen_fit"], m["unseen_fit_strict"] = avg_fit(unseen, net, im, fm)
            else:
                m["unseen_fit"], m["unseen_fit_strict"] = None, None
            try:
                m["m2"] = float(gen_eval.apply(train, net, im, fm))
            except Exception:  # noqa: BLE001
                m["m2"] = None
        except Exception as e:  # noqa: BLE001
            m["error"] = f"{type(e).__name__}: {e}"
        m["seconds"] = time.time() - tm
        cell["models"][mn] = m
        if m["error"]:
            print(f"      {mn:22s} FAIL {m['error']}", flush=True)
        else:
            uf = "  -   " if m["unseen_fit"] is None else f"{m['unseen_fit']:.4f}"
            print(f"      {mn:22s} sg={m['shadowgen']:.4f} truth={uf} train={m['train_fit']:.4f} "
                  f"m2={m['m2'] if m['m2'] is None else round(m['m2'], 4)} [{m['seconds']:.0f}s]",
                  flush=True)
    return cell


def process(dkey, levels, reps, tag):
    t0 = time.time()
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    os.makedirs(OUT_DIR, exist_ok=True)
    stem = f"randomization_{dkey}" + (f"_{tag}" if tag else "")
    partial = os.path.join(OUT_DIR, stem + ".partial.json")
    cells = {}
    if os.path.exists(partial):
        cells = json.load(open(partial, encoding="utf-8")).get("cells", {})
        print(f"  resuming: {len(cells)} cells from {partial}", flush=True)
    rec = {"dataset": DATASETS[dkey]["name"], "n_cases": len(log), "levels": levels, "reps": reps,
           "cells": cells}
    print(f"\n=== {dkey} {DATASETS[dkey]['name']}: {len(log)} cases, levels {levels}, {reps} reps",
          flush=True)
    # repetitions outside, levels inside: a full curve exists after the first repetition
    for rep in range(reps):
        for p in levels:
            key = f"{p:.2f}|{rep}"
            if key in cells:
                print(f"  p={p:.2f} rep={rep} resumed", flush=True)
                continue
            tc = time.time()
            print(f"  p={p:.2f} rep={rep}", flush=True)
            cell = run_cell(log, p, rep)
            cell["seconds"] = time.time() - tc
            print(f"    |train|={cell['n_train']} variants={cell['var_train']} "
                  f"unseen share={cell['unseen_share']:.3f} [{cell['seconds']:.0f}s]", flush=True)
            cells[key] = cell
            with open(partial, "w", encoding="utf-8") as fp:
                json.dump(rec, fp, indent=1)
    rec["seconds"] = time.time() - t0
    rec["protocol"] = ("within-trace permutation of a share p of the cases; random 70/30 case split; "
                       "models discovered on the training split; ShadowGen seed 42, one 1,000-trace "
                       "draw, N=6, tau=5, mle, v2.6 core; truth = token replay of future cases with a "
                       "variant absent from training; pm4py " + pm4py.__version__)
    path = os.path.join(OUT_DIR, stem + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    os.remove(partial)
    print(f"  [{dkey} done in {rec['seconds']:.0f}s -> {path}]", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*", default=["D1", "D2"])
    ap.add_argument("--levels", default="0,0.25,0.5,0.75,1")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    levels = [float(x) for x in a.levels.split(",")]
    for k in a.keys:
        try:
            process(k, levels, a.reps, a.tag)
        except Exception as e:  # noqa: BLE001
            print(f"[{k}] DATASET FAIL: {type(e).__name__}: {e}", flush=True)


if __name__ == "__main__":
    main()
