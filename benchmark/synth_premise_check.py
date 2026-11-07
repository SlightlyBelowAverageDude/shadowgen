"""Generator premise on the synthetic known systems: how much of the shadow log is valid system behavior.

For every stored system the script regenerates the system S and its 300-trace training log L with the
stored seeds (synth_ground_truth.py), generates the shadow log once with the benchmark protocol (seed 42,
1,000 traces, N=6, tau=5, mle; generation depends on the log only), and replays it on S itself:

  valid_strict   share of shadow traces that S replays perfectly (traces in the language of S)
  valid_graded   mean token-replay fitness of the shadow log on S
  split by regular and mutated (novel activity in context) shadow traces
  hit_unseen     share of shadow traces whose variant occurs among the unseen variants of the fresh
                 2,500-trace sample F (seed+1), the known-system analogue of the hit rate on real logs
  random floor   uniformly random traces over the alphabet of L with the shadow traces' lengths,
                 replayed on S (strict share, graded mean) and matched against the unseen variants of F

pm4py's play-out is not reproducible across processes, so the logs are a resample of the stored study.
Output: results/synth_strict/synth_premise_check.json (nothing overwritten).
Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/synth_premise_check.py [--limit N]
"""
import os
import sys
import json
import time
import random
import argparse

os.environ["TQDM_DISABLE"] = "1"
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
sys.path.insert(0, _REPO)
sys.path.insert(0, _HERE)

import numpy as np  # noqa: E402
import pm4py  # noqa: E402
from pm4py.objects.log.obj import EventLog, Trace, Event  # noqa: E402
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay  # noqa: E402

import synth_ground_truth as sgt  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

SEED = 42
GEN_KW = dict(num_traces=1000, safe_threshold=5, max_n=6, successor_weighting="mle")
STORED = os.path.join(_HERE, "results", "synth_ground_truth.json")
OUT = os.path.join(_HERE, "results", "synth_strict", "synth_premise_check.json")


def replay(log, net, im, fm):
    res = token_replay.apply(log, net, im, fm)
    fit = [r["trace_fitness"] for r in res]
    acc = [1.0 if r.get("trace_is_fit", r["trace_fitness"] >= 1.0) else 0.0 for r in res]
    return fit, acc


def mean(v):
    return float(np.mean(v)) if len(v) else None


def random_log(alphabet, lengths, seed):
    rng = random.Random(seed)
    log = EventLog()
    for n in lengths:
        t = Trace()
        for _ in range(n):
            t.append(Event({"concept:name": rng.choice(alphabet)}))
        log.append(t)
    return log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    stored = json.load(open(STORED, encoding="utf-8"))["systems"]
    if args.limit:
        stored = stored[: args.limit]
    gen = load_algorithm("v2.6").generate_shadow_log

    out, t0 = [], time.time()
    for idx, s in enumerate(stored):
        mode, seed = s["mode"], s["seed"]
        tree, S_net, S_im, S_fm = sgt.gen_system(mode, seed)
        F = sgt.playout(S_net, S_im, S_fm, sgt.N_F, seed + 1)
        L = sgt.playout(S_net, S_im, S_fm, sgt.N_L, seed + 2)
        vL, vF = sgt.variants(L), sgt.variants(F)
        unseen_F = {v for v in vF if v not in vL}

        random.seed(SEED)
        np.random.seed(SEED)
        shadow, flags, dup_kept, truncated, cap = gen(L, **GEN_KW)
        shadow_vars = [tuple(e["concept:name"] for e in t) for t in shadow]
        fit, acc = replay(shadow, S_net, S_im, S_fm)
        reg = [i for i, f in enumerate(flags) if not f]
        mut = [i for i, f in enumerate(flags) if f]

        alphabet = sorted({e["concept:name"] for t in L for e in t})
        lengths = [len(t) for t in shadow]
        rnd = random_log(alphabet, lengths, SEED)
        rnd_vars = [tuple(e["concept:name"] for e in t) for t in rnd]
        rfit, racc = replay(rnd, S_net, S_im, S_fm)

        rec = {
            "mode": mode, "seed": seed, "tree_matches_stored": str(tree)[:200] == s["tree"],
            "n_L": len(L), "var_L": len(vL), "var_F": len(vF), "n_unseen_variants_F": len(unseen_F),
            "n_shadow": len(shadow), "n_mutated": len(mut), "duplicates_kept": int(dup_kept), "truncated": int(truncated),
            "shadow_in_L": sum(v in vL for v in shadow_vars) / len(shadow),
            "shadow_distinct": len(set(shadow_vars)),
            "valid_strict": mean(acc), "valid_graded": mean(fit),
            "valid_strict_regular": mean([acc[i] for i in reg]), "valid_graded_regular": mean([fit[i] for i in reg]),
            "valid_strict_mutated": mean([acc[i] for i in mut]), "valid_graded_mutated": mean([fit[i] for i in mut]),
            "hit_unseen": sum(v in unseen_F for v in shadow_vars) / len(shadow),
            "hit_unseen_regular": mean([1.0 if shadow_vars[i] in unseen_F else 0.0 for i in reg]),
            "hit_unseen_mutated": mean([1.0 if shadow_vars[i] in unseen_F else 0.0 for i in mut]),
            "unseen_variants_covered": len({v for v in shadow_vars if v in unseen_F}) / len(unseen_F) if unseen_F else None,
            "random_valid_strict": mean(racc), "random_valid_graded": mean(rfit),
            "random_hit_unseen": sum(v in unseen_F for v in rnd_vars) / len(rnd),
        }
        out.append(rec)
        print(f"[{idx + 1}/{len(stored)}] mode={mode} seed={seed} valid_strict={rec['valid_strict']:.3f} "
              f"(regular {rec['valid_strict_regular'] if rec['valid_strict_regular'] is not None else float('nan'):.3f}, "
              f"mutated {rec['valid_strict_mutated'] if rec['valid_strict_mutated'] is not None else float('nan'):.3f}) "
              f"hit_unseen={rec['hit_unseen']:.3f} random_valid={rec['random_valid_strict']:.3f} [{time.time() - t0:.0f}s]", flush=True)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"protocol": "seed 42; 1,000 shadow traces; N=6, tau=5, mle; v2.6 generator; pm4py " + pm4py.__version__,
               "n_systems": len(out), "runtime_s": time.time() - t0, "systems": out}, open(OUT, "w", encoding="utf-8"), indent=1)
    print(f"wrote {OUT} [{time.time() - t0:.0f}s]")


if __name__ == "__main__":
    main()
