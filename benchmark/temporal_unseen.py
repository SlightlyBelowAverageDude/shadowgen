"""Temporal hold-out with an unseen-only reference.

temporal_holdout.py scores the token-replay fitness of all test (latest 30 percent) cases, including
cases whose variant already occurs in the training split. Eq. (1) of the paper conditions on behavior
absent from the log, and ShadowGen probes unseen variants only. This script repeats the temporal
protocol (same split, same eight miners, same ShadowGen protocol) and records, per model:

  shadowgen / shadowgen_strict        graded and strict reading (v2.6 core, seed 42, K=1, N=6, tau=5, mle)
  holdout_fit / holdout_fit_strict    replay fitness / perfect-replay share of ALL test cases (as stored)
  unseen_fit / unseen_fit_strict      the same on the test cases whose variant is absent from training
  m2                                  PM4Py structural generalization on the training split
  *_stored                            values from results/temporal_holdout.json (read only) for comparison

Output: results/temporal_unseen/temporal_unseen_<key>.json, one file per log (nothing overwritten);
a .partial.json is written after every model and resumed from if the run is stopped.
Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/temporal_unseen.py D1 D2 D5 D3 D4
"""
import os
import sys
import json
import time
import random

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["TQDM_DISABLE"] = "1"
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
sys.path.insert(0, _REPO)
sys.path.insert(0, _HERE)

import numpy as np  # noqa: E402
import pm4py  # noqa: E402
from pm4py.objects.log.obj import EventLog  # noqa: E402
from pm4py.algo.evaluation.generalization import algorithm as gen_eval  # noqa: E402

from miners import MINERS  # noqa: E402
from datasets import DATASETS, get_log_path  # noqa: E402
from temporal_holdout import temporal_split, variants, avg_fit  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

try:
    import pm4py.util.constants as _pmc
    _pmc.SHOW_PROGRESS_BAR = False
except Exception:  # noqa: BLE001
    pass

SEED = 42
GEN_KW = dict(num_traces=1000, iterations=1, safe_threshold=5, max_n=6, successor_weighting="mle")
STORED = os.path.join(_HERE, "results", "temporal_holdout.json")
OUT_DIR = os.path.join(_HERE, "results", "temporal_unseen")


def score_both(log, net, im, fm):
    """Same seeding as shadowgen.gen_shadow, then the v2.6 core, which reports both readings."""
    random.seed(SEED)
    np.random.seed(SEED)
    r = load_algorithm("v2.6").calculate_gen_shadow_stable(log, net, im, fm, **GEN_KW)
    return float(r["mean"]), float(r["accept_mean"]), sum(r["mutation_counts"]) / float(GEN_KW["num_traces"]), int(r["duplicates_kept"])


def process(dkey, stored):
    t0 = time.time()
    st_rec = stored.get(dkey, {})
    st_models = st_rec.get("models", {})
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    train, test, tr0, tr1, te0, te1 = temporal_split(log)
    vtr = variants(train)
    unseen = EventLog([t for t in test if tuple(e["concept:name"] for e in t) not in vtr])
    vte_unseen = variants(unseen)
    print(f"\n=== {dkey} {DATASETS[dkey]['name']}: |train|={len(train)} |test|={len(test)} "
          f"|test unseen|={len(unseen)} ({len(unseen) / len(test):.3f}; stored {st_rec.get('novel_in_test')}) "
          f"unseen variants={len(vte_unseen)}", flush=True)
    rec = {"dataset": DATASETS[dkey]["name"], "n_train": len(train), "n_test": len(test),
           "n_test_unseen": len(unseen), "unseen_share": len(unseen) / len(test),
           "unseen_share_stored": st_rec.get("novel_in_test"), "var_train": len(vtr),
           "var_test_unseen": len(vte_unseen),
           "train_range": [str(tr0), str(tr1)], "test_range": [str(te0), str(te1)], "models": {}}
    os.makedirs(OUT_DIR, exist_ok=True)
    partial = os.path.join(OUT_DIR, f"temporal_unseen_{dkey}.partial.json")
    done = {}
    if os.path.exists(partial):
        done = json.load(open(partial, encoding="utf-8")).get("models", {})
        print(f"  resuming: {len(done)} models from {partial}", flush=True)
    for mn, fn in MINERS.items():
        if mn in done and done[mn].get("error") is None:
            rec["models"][mn] = done[mn]
            print(f"    {mn:22s} resumed", flush=True)
            continue
        s = st_models.get(mn) or {}
        m = {"error": None}
        tm = time.time()
        try:
            net, im, fm = fn(train)
            m["n_transitions"] = len(net.transitions)
            m["shadowgen"], m["shadowgen_strict"], m["mutated_share"], m["duplicates_kept"] = score_both(train, net, im, fm)
            m["holdout_fit"], m["holdout_fit_strict"] = avg_fit(test, net, im, fm)
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
        for k in ("shadowgen", "holdout_fit", "holdout_fit_strict", "m2"):
            m[k + "_stored"] = s.get(k)
        m["seconds"] = time.time() - tm
        rec["models"][mn] = m
        with open(partial, "w", encoding="utf-8") as fp:
            json.dump(rec, fp, indent=1)
        if m["error"]:
            print(f"    {mn:22s} FAIL {m['error']}", flush=True)
        else:
            print(f"    {mn:22s} sg={m['shadowgen']:.4f} (stored {s.get('shadowgen')}) strict={m['shadowgen_strict']:.4f} "
                  f"all={m['holdout_fit']:.4f} (stored {s.get('holdout_fit')}) unseen={m['unseen_fit'] if m['unseen_fit'] is None else round(m['unseen_fit'], 4)} "
                  f"unseen_strict={m['unseen_fit_strict'] if m['unseen_fit_strict'] is None else round(m['unseen_fit_strict'], 4)} [{m['seconds']:.0f}s]", flush=True)
    rec["seconds"] = time.time() - t0
    rec["protocol"] = "split 70/30 by case start; seed 42; one 1,000-trace draw; N=6, tau=5, mle; v2.6 core; pm4py " + pm4py.__version__
    path = os.path.join(OUT_DIR, f"temporal_unseen_{dkey}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    os.remove(partial)
    print(f"  [{dkey} done in {rec['seconds']:.0f}s -> {path}]", flush=True)


def main():
    keys = sys.argv[1:] or ["D1", "D2", "D5", "D3", "D4"]
    stored = json.load(open(STORED, encoding="utf-8"))
    for k in keys:
        try:
            process(k, stored)
        except Exception as e:  # noqa: BLE001
            print(f"[{k}] DATASET FAIL: {type(e).__name__}: {e}", flush=True)


if __name__ == "__main__":
    main()
