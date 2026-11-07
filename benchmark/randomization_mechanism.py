"""Why ShadowGen misses the truth on a randomized log (follow-up to randomization_test.py).

Hypothesis: after the within-trace permutation the remaining structure of the system is which
activities a trace contains (its activity multiset). The N-gram generator models order, so its
shadow traces can carry multisets the system never produces, and nets that encode the multiset
structure reject them although they accept the true future.

For one cell (log, level p, repetition 0, same seeds as randomization_test.py) the script
regenerates the randomized log, the split and the shadow log (seed 42), and reports
  - reproduction: ShadowGen recomputed here vs the value stored by randomization_test.py
  - multiset-valid share: traces whose activity multiset occurs in the full randomized log
    (training plus future), for the shadow log and for the unseen future traces (1 by construction)
  - multiset novelty: share whose multiset is absent from the training split
  - acceptance (graded / strict) of the shadow traces, split by multiset-valid or not, per net,
    next to the acceptance of the unseen future traces

Output: results/randomization/mechanism_<key>.json (new file) and a printed table.
Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/randomization_mechanism.py D1 D2
"""
import os
import sys
import json
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
from HybridGen.algorithm import load_algorithm  # noqa: E402
from randomization_test import randomize, split, acts, SEED, GEN_KW, OUT_DIR  # noqa: E402

NETS = ["Alpha+", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
LEVELS = [0.0, 1.0]
REP = 0


def mset(seq):
    return tuple(sorted(Counter(seq).items()))


def replay(log, net, im, fm):
    res = token_replay.apply(log, net, im, fm)
    fit = np.array([r["trace_fitness"] for r in res], float)
    acc = np.array([1.0 if r.get("trace_is_fit", r["trace_fitness"] >= 1.0) else 0.0 for r in res])
    return fit, acc


def mean(x):
    return float(np.mean(x)) if len(x) else None


def process(dkey):
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    stored = json.load(open(os.path.join(OUT_DIR, f"randomization_{dkey}.json"), encoding="utf-8"))
    out = {"dataset": DATASETS[dkey]["name"], "levels": {}}
    for p in LEVELS:
        rng = random.Random(1000 * REP + int(round(p * 100)))
        traces, _ = randomize(log, p, rng)
        train, test = split(traces, rng)
        vtr = set(acts(t) for t in train)
        unseen = EventLog([t for t in test if acts(t) not in vtr])
        ms_train = set(mset(acts(t)) for t in train)
        ms_all = ms_train | set(mset(acts(t)) for t in test)

        random.seed(SEED)
        np.random.seed(SEED)
        shadow = load_algorithm("v2.6").generate_shadow_log(
            train, num_traces=GEN_KW["num_traces"], safe_threshold=GEN_KW["safe_threshold"],
            max_n=GEN_KW["max_n"], successor_weighting=GEN_KW["successor_weighting"])[0]
        sh_valid = np.array([mset(acts(t)) in ms_all for t in shadow])
        sh_new = np.array([mset(acts(t)) not in ms_train for t in shadow])
        un_new = np.array([mset(acts(t)) not in ms_train for t in unseen])
        lev = {"n_shadow": len(shadow), "n_unseen": len(unseen),
               "shadow_multiset_valid": float(sh_valid.mean()),
               "shadow_multiset_absent_from_training": float(sh_new.mean()),
               "unseen_multiset_absent_from_training": float(un_new.mean()),
               "shadow_mean_len": float(np.mean([len(t) for t in shadow])),
               "unseen_mean_len": float(np.mean([len(t) for t in unseen])), "nets": {}}
        print(f"\n{dkey} p={p:.0f}: shadow multiset-valid {sh_valid.mean():.3f}, "
              f"multiset absent from training: shadow {sh_new.mean():.3f}, unseen future {un_new.mean():.3f}; "
              f"mean length shadow {lev['shadow_mean_len']:.1f}, unseen {lev['unseen_mean_len']:.1f}")
        print("  net".ljust(24) + "ShadowGen (stored)   shadow valid g/s   shadow invalid g/s   unseen future g/s")
        cell = stored["cells"][f"{p:.2f}|{REP}"]["models"]
        for mn in NETS:
            net, im, fm = MINERS[mn](train)
            fs, as_ = replay(shadow, net, im, fm)
            fu, au = replay(unseen, net, im, fm)
            rec = {"shadowgen": mean(fs), "shadowgen_strict": mean(as_),
                   "shadowgen_stored": cell[mn]["shadowgen"],
                   "shadowgen_strict_stored": cell[mn]["shadowgen_strict"],
                   "valid_graded": mean(fs[sh_valid]), "valid_strict": mean(as_[sh_valid]),
                   "invalid_graded": mean(fs[~sh_valid]), "invalid_strict": mean(as_[~sh_valid]),
                   "unseen_graded": mean(fu), "unseen_strict": mean(au),
                   "unseen_graded_stored": cell[mn]["unseen_fit"]}
            lev["nets"][mn] = rec
            f = lambda x: "  -  " if x is None else f"{x:.3f}"  # noqa: E731
            print(f"  {mn:22s}{f(rec['shadowgen'])} ({f(rec['shadowgen_stored'])})"
                  f"        {f(rec['valid_graded'])}/{f(rec['valid_strict'])}"
                  f"        {f(rec['invalid_graded'])}/{f(rec['invalid_strict'])}"
                  f"          {f(rec['unseen_graded'])}/{f(rec['unseen_strict'])}")
        out["levels"][f"{p:.2f}"] = lev
    path = os.path.join(OUT_DIR, f"mechanism_{dkey}.json")
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(out, fp, indent=1)
    print(f"[written {path}]")


if __name__ == "__main__":
    for k in sys.argv[1:] or ["D1", "D2"]:
        process(k)
