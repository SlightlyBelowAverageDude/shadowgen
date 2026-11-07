"""Sensitivity of the Alpha+ gap to the generator's context length N and backoff threshold tau (L1, L2).

Same nets for score and reference (training split: temporal 70/30 by case start, or random 70/30 seed 0); reference =
replay fitness of the test cases whose variant is absent from training. For each (N, tau): the six-miner score, the
gap per miner, MAE and Pearson over the six miners, the share of shadow traces that break a count bound of training
(an activity occurring more often than in any training trace, or less often than in every training trace), mean
shadow length, and Alpha+ on the shadow traces that keep every count bound.

Output: results/alphaplus_check/sweep_<key>.json and summary_sweep_<keys>.md (new files).
Run from the repo root:  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/alphaplus_sweep.py D1 D2
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
from datasets import get_log_path  # noqa: E402
from temporal_holdout import temporal_split, variants  # noqa: E402
from temporal_drift_screen import random_split  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "alphaplus_check")
LKEY = {"D1": "L1", "D2": "L2", "D3": "L3", "D4": "L4", "D5": "L5"}
SIX = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
CONFIGS = [(6, 5), (3, 5), (10, 5), (15, 5), (6, 2), (10, 2), (15, 2), (6, 10)]


def act(t):
    return tuple(e["concept:name"] for e in t)


def main():
    keys = [a for a in sys.argv[1:] if a.startswith("D")] or ["D1", "D2"]
    gen = load_algorithm("v2.6").generate_shadow_log
    out_all = {}
    for dkey in keys:
        log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
        reps = {}
        for t in log:
            reps.setdefault(act(t), t)
        out = {}
        for split in ("temporal", "random"):
            train, test = temporal_split(log)[:2] if split == "temporal" else random_split(log, seed=0)
            vtr, vte = variants(train), variants(test)
            un = [v for v in vte if v not in vtr]
            uw = np.array([vte[v] for v in un], float)
            alpha = sorted({a for v in vtr for a in v})
            mx = {a: max(Counter(v)[a] for v in vtr) for a in alpha}
            mn_ = {a: min(Counter(v)[a] for v in vtr) for a in alpha}

            def bounded(s):
                c = Counter(s)
                return all(mn_.get(a, 0) <= c.get(a, 0) <= mx.get(a, 0) for a in set(alpha) | set(c))
            nets = {m: MINERS[m](train) for m in SIX}
            ref = {}
            for m, (net, im, fm) in nets.items():
                ru = token_replay.apply(EventLog([reps[k] for k in un]), net, im, fm)
                ref[m] = float(np.dot([r["trace_fitness"] for r in ru], uw) / uw.sum())
            rows = []
            for n_, tau in CONFIGS:
                t0 = time.time()
                random.seed(42)
                np.random.seed(42)
                shadow, flags, dup, trunc, cap = gen(train, num_traces=1000, safe_threshold=tau, max_n=n_, successor_weighting="mle")
                seqs = [act(t) for t in shadow]
                ok = np.array([bounded(s) for s in seqs])
                row = {"N": n_, "tau": tau, "mutated": int(sum(flags)), "duplicates_kept": dup, "truncated": trunc,
                       "len_mean": float(np.mean([len(s) for s in seqs])), "bound_violation": float(1 - ok.mean()), "miners": {}}
                for m, (net, im, fm) in nets.items():
                    f = np.array([r["trace_fitness"] for r in token_replay.apply(shadow, net, im, fm)])
                    row["miners"][m] = {"score": float(f.mean()), "ref": ref[m], "gap": float(f.mean() - ref[m]),
                                        "score_bounded": float(f[ok].mean()) if ok.any() else None}
                sc = np.array([row["miners"][m]["score"] for m in SIX])
                rf = np.array([ref[m] for m in SIX])
                row["mae"] = float(np.mean(np.abs(sc - rf)))
                row["pearson"] = float(np.corrcoef(sc, rf)[0, 1])
                row["mae_without_alpha_plus"] = float(np.mean([abs(row["miners"][m]["gap"]) for m in SIX if m != "Alpha+"]))
                rows.append(row)
                a = row["miners"]["Alpha+"]
                print(f"{LKEY[dkey]} {split:8s} N={n_:2d} tau={tau:2d}: Alpha+ {a['score']:.3f} vs {a['ref']:.3f} gap {a['gap']:+.3f} "
                      f"(bounded {a['score_bounded']:.3f}) | MAE {row['mae']:.3f} (without Alpha+ {row['mae_without_alpha_plus']:.3f}) "
                      f"Pearson {row['pearson']:.3f} | violation {row['bound_violation']:.3f} len {row['len_mean']:.1f} "
                      f"mutated {row['mutated']} dup {dup} [{time.time() - t0:.0f}s]", flush=True)
            out[split] = {"n_unseen_cases": int(uw.sum()), "reference": ref, "rows": rows}
        out_all[dkey] = out
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, f"sweep_{dkey}.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
    L = ["# Alpha+ gap against generator context length N and backoff threshold tau", "",
         "| log | split | N | tau | Alpha+ score | Alpha+ ref | Alpha+ gap | Alpha+ on bounded traces | MAE six | MAE without Alpha+ | Pearson six | bound violation | mean length | mutated |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for dkey, out in out_all.items():
        for split, o in out.items():
            for r in o["rows"]:
                a = r["miners"]["Alpha+"]
                L.append(f"| {LKEY[dkey]} | {split} | {r['N']} | {r['tau']} | {a['score']:.3f} | {a['ref']:.3f} | {a['gap']:+.3f} | {a['score_bounded']:.3f} | "
                         f"{r['mae']:.3f} | {r['mae_without_alpha_plus']:.3f} | {r['pearson']:.3f} | {r['bound_violation']:.3f} | {r['len_mean']:.1f} | {r['mutated']} |")
    open(os.path.join(OUT_DIR, "summary_sweep_" + "_".join(keys) + ".md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
