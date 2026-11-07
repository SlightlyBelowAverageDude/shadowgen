"""Strict reading of ShadowGen on the synthetic known-system study.

The study in synth_ground_truth.py recorded only the graded reading (mean token-replay
fitness of the shadow log). This script regenerates every stored system and its training
log with the same seeds, rediscovers the eight models, and scores ShadowGen once more with
the benchmark protocol (seed 42, one 1,000-trace draw, N=6, tau=5, mle), this time keeping
both readings:

  graded  = mean token-replay trace fitness of the shadow log   (must reproduce the stored value)
  strict  = share of shadow traces replayed perfectly (trace_is_fit)

pm4py's play-out is not reproducible across processes (transition order depends on object
identity), so the regenerated training logs and fresh samples differ from the original run
even with the same seeds. The script therefore recomputes true recall (graded and strict,
from a fresh 2,500-trace sample), true precision, and M2 for the rediscovered nets, which
makes it a replication of the study under resampling. The stored values are joined from
results/synth_ground_truth.json (read only) for comparison.

Two references are recorded per model: the full fresh sample F (as in the original study) and
the unseen part of F, the traces whose variant does not occur in the training log, which is the
reference Eq. (1) of the paper asks for (future valid behavior not in the log).

Output: results/synth_strict/<name>.json (new folder, nothing overwritten; default name
synth_strict_check.json, pass --out for another run).
Run from the repo root with the project environment:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/synth_strict_check.py [--limit N] [--out NAME.json]
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
from pm4py.objects.log.obj import EventLog  # noqa: E402

import synth_ground_truth as sgt  # noqa: E402  (importing is safe: run() sits under a __main__ guard)
from HybridGen.algorithm import load_algorithm  # noqa: E402

SEED = 42
GEN_KW = dict(num_traces=1000, iterations=1, safe_threshold=5, max_n=6, successor_weighting="mle")
STORED = os.path.join(_HERE, "results", "synth_ground_truth.json")
OUT_DIR = os.path.join(_HERE, "results", "synth_strict")


def score_both(log, net, im, fm):
    """Same seeding as shadowgen.gen_shadow, then the v2.6 core, which reports both readings."""
    random.seed(SEED)
    np.random.seed(SEED)
    core = load_algorithm("v2.6").calculate_gen_shadow_stable
    r = core(log, net, im, fm, **GEN_KW)
    n_mut = sum(r["mutation_counts"])
    return {
        "graded": float(r["mean"]),
        "strict": float(r["accept_mean"]),
        "graded_regular": float(r["reg_mean"]),
        "graded_mutated": float(r["mut_mean"]),
        "strict_regular": float(r["accept_reg_mean"]),
        "strict_mutated": float(r["accept_mut_mean"]),
        "mutated_share": n_mut / float(GEN_KW["num_traces"]),
        "duplicates_kept": int(r["duplicates_kept"]),
        "truncated": int(r["truncated"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="only the first N stored systems (smoke test)")
    ap.add_argument("--out", default="synth_strict_check.json", help="output file name inside results/synth_strict/")
    args = ap.parse_args()

    stored = json.load(open(STORED, encoding="utf-8"))
    systems = stored["systems"]
    if args.limit:
        systems = systems[: args.limit]
    os.makedirs(OUT_DIR, exist_ok=True)

    out_systems = []
    t0 = time.time()
    worst = 0.0
    for idx, s in enumerate(systems):
        mode, seed = s["mode"], s["seed"]
        tree, S_net, S_im, S_fm = sgt.gen_system(mode, seed)
        F = sgt.playout(S_net, S_im, S_fm, sgt.N_F, seed + 1)
        L = sgt.playout(S_net, S_im, S_fm, sgt.N_L, seed + 2)
        vL, vF = sgt.variants(L), sgt.variants(F)
        cov = sum(c for v, c in vF.items() if v in vL) / max(sum(vF.values()), 1)
        F_unseen = EventLog([t for t in F if tuple(e["concept:name"] for e in t) not in vL])
        rec = {"mode": mode, "seed": seed, "tree": str(tree)[:200], "n_L": len(L), "n_F": len(F),
               "n_F_unseen": len(F_unseen),
               "var_L": len(vL), "var_F": len(vF), "coverage": cov, "coverage_stored": s.get("coverage"),
               "tree_matches_stored": str(tree)[:200] == s["tree"], "models": {}}
        for name, fn in sgt.MINERS.items():
            st = s["models"].get(name) or {}
            m = {"error": None}
            try:
                net, im, fm = fn(L)
                m["n_transitions"] = len(net.transitions)
                m["n_transitions_stored"] = st.get("n_transitions")
                m.update(score_both(L, net, im, fm))
                m["graded_stored"] = st.get("shadowgen")
                m["graded_diff"] = (m["graded"] - st["shadowgen"]) if st.get("shadowgen") is not None else None
                rg, rs = sgt.avg_fit(F, net, im, fm)
                m["true_recall"] = rg
                m["true_recall_strict"] = rs
                m["true_recall_stored"] = st.get("true_recall")
                m["true_recall_strict_stored"] = st.get("true_recall_strict")
                if len(F_unseen) > 0:
                    ru, rsu = sgt.avg_fit(F_unseen, net, im, fm)
                    m["true_recall_unseen"] = ru
                    m["true_recall_strict_unseen"] = rsu
                else:
                    m["true_recall_unseen"] = None
                    m["true_recall_strict_unseen"] = None
                try:
                    Mp = sgt.playout(net, im, fm, sgt.N_M, seed + 3)
                    m["true_precision"] = sgt.avg_fit(Mp, S_net, S_im, S_fm)[0]
                except Exception:  # noqa: BLE001
                    m["true_precision"] = None
                m["true_precision_stored"] = st.get("true_precision")
                try:
                    m["m2"] = float(sgt.gen_eval.apply(L, net, im, fm))
                except Exception:  # noqa: BLE001
                    m["m2"] = None
                m["m2_stored"] = st.get("m2")
                if m["graded_diff"] is not None:
                    worst = max(worst, abs(m["graded_diff"]))
            except Exception as e:  # noqa: BLE001
                m["error"] = f"{type(e).__name__}: {e}"
            rec["models"][name] = m
        out_systems.append(rec)
        diffs = [abs(v["graded_diff"]) for v in rec["models"].values() if v.get("graded_diff") is not None]
        print(f"[{idx + 1}/{len(systems)}] mode={mode} seed={seed} tree_ok={rec['tree_matches_stored']} "
              f"max|graded diff|={max(diffs) if diffs else float('nan'):.4f} [{time.time() - t0:.0f}s]", flush=True)

    out = {
        "protocol": "seed 42; one 1,000-trace draw; N=6, tau=5, mle; v2.6 core; pm4py " + pm4py.__version__,
        "stored_file": os.path.relpath(STORED, _REPO),
        "n_systems": len(out_systems),
        "worst_graded_reproduction_diff": worst,
        "runtime_s": time.time() - t0,
        "systems": out_systems,
    }
    path = os.path.join(OUT_DIR, args.out)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {path}; worst |graded diff| {worst:.4f}; {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
