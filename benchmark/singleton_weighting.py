"""Sensitivity analysis: reweight the shadow log to the length distribution of the training singletons.

Real unseen traces are as long as the training variants that occur once (L2, L5), while the shadow log is shorter.
Good-Turing, which ShadowGen uses for its mutation rate, takes singletons as the proxy for unseen mass. This script
weights each shadow trace by (singleton share of its length bin) / (shadow share of its length bin) and compares the
four criteria over the six miners before and after, against the unseen reference on the same nets.

Splits: temporal 70/30 by case start, and random 70/30 (seed 0). Shadow log: v2.6 core, seed 42, N=6, tau=5, mle,
1,000 traces (identical to the score). Bins: deciles of the target lengths (also 5 and 20 as a check). Weighting to
the unseen lengths themselves is reported as the oracle (not available from the log).

Output: results/singleton_weighting/<key>_<split>.json and summary_<keys>.md (new folder).
Run from the repo root:  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/singleton_weighting.py D1 D2 D3 D5
"""
import os
import sys
import json
import time
import random

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["TQDM_DISABLE"] = "1"
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, _HERE)

import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402
import pm4py  # noqa: E402
from pm4py.objects.log.obj import EventLog  # noqa: E402
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay  # noqa: E402

from miners import MINERS  # noqa: E402
from datasets import get_log_path  # noqa: E402
from temporal_holdout import temporal_split, variants  # noqa: E402
from temporal_drift_screen import random_split  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "singleton_weighting")
LKEY = {"D1": "L1", "D2": "L2", "D3": "L3", "D4": "L4", "D5": "L5"}
SIX = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
GEN_KW = dict(num_traces=1000, safe_threshold=5, max_n=6, successor_weighting="mle")


def act(t):
    return tuple(e["concept:name"] for e in t)


def length_weights(sh_len, target_len, nbins):
    sh_len, target_len = np.asarray(sh_len, float), np.asarray(target_len, float)
    edges = np.unique(np.quantile(target_len, np.linspace(0, 1, nbins + 1)))
    if len(edges) < 2:
        edges = np.array([edges[0], edges[0] + 1])
    edges[0] = min(edges[0], sh_len.min())
    edges[-1] = max(edges[-1], sh_len.max()) + 1

    def b(x):
        return np.clip(np.searchsorted(edges, x, side="right") - 1, 0, len(edges) - 2)
    bs, bt = b(sh_len), b(target_len)
    k = len(edges) - 1
    s_share = np.bincount(bs, minlength=k) / len(bs)
    t_share = np.bincount(bt, minlength=k) / len(bt)
    covered = t_share[s_share > 0].sum()
    w = np.where(s_share[bs] > 0, t_share[bs] / np.maximum(s_share[bs], 1e-12), 0.0)
    w = w / w.mean()
    return w, {"bins": k, "covered_target_mass": float(covered), "ess": float(w.sum() ** 2 / (w ** 2).sum())}


def criteria(score, ref):
    s, r = np.asarray(score, float), np.asarray(ref, float)
    rank = lambda v: np.argsort(np.argsort(v)).astype(float)  # noqa: E731
    return {"pearson": float(np.corrcoef(s, r)[0, 1]), "spearman": float(np.corrcoef(rank(s), rank(r))[0, 1]),
            "spearman_ties": float(stats.spearmanr(s, r).statistic), "kendall_b": float(stats.kendalltau(s, r).statistic),
            "mae": float(np.mean(np.abs(s - r))), "spread": float(s.max() - s.min()), "spread_ref": float(r.max() - r.min()),
            "max_abs_dev": float(np.max(np.abs(s - r)))}


def process(dkey, split):
    t0 = time.time()
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    train, test = temporal_split(log)[:2] if split == "temporal" else random_split(log, seed=0)
    vtr, vte = variants(train), variants(test)
    reps = {}
    for t in log:
        reps.setdefault(act(t), t)
    un = [v for v in vte if v not in vtr]
    uw = np.array([vte[v] for v in un], float)
    singles = [len(v) for v, c in vtr.items() if c == 1]
    unseen_len = np.repeat([len(v) for v in un], uw.astype(int))
    random.seed(42)
    np.random.seed(42)
    shadow, flags, dup, trunc, cap = load_algorithm("v2.6").generate_shadow_log(train, **GEN_KW)
    sh_len = [len(t) for t in shadow]
    W = {}
    for nb in (5, 10, 20):
        W[f"singleton_{nb}"] = length_weights(sh_len, singles, nb)
    W["oracle_10"] = length_weights(sh_len, unseen_len, 10)
    rec = {"log": LKEY[dkey], "split": split, "n_train": len(train), "n_singletons": len(singles),
           "singleton_share_of_cases": len(singles) / len(train), "n_unseen_cases": int(uw.sum()),
           "len_mean": {"cases": float(np.mean(np.repeat([len(v) for v in vtr], list(vtr.values())))),
                        "singletons": float(np.mean(singles)), "shadow": float(np.mean(sh_len)), "unseen": float(unseen_len.mean())},
           "weights": {k: v[1] for k, v in W.items()}, "miners": {}}
    for k, (w, info) in W.items():
        rec["len_mean"][f"shadow_weighted_{k}"] = float(np.dot(w, sh_len) / w.sum())
    print(f"\n=== {rec['log']} {split}: singletons {len(singles)} ({rec['singleton_share_of_cases']:.3f} of cases); mean length cases "
          f"{rec['len_mean']['cases']:.1f} singletons {rec['len_mean']['singletons']:.1f} shadow {rec['len_mean']['shadow']:.1f} "
          f"weighted {rec['len_mean']['shadow_weighted_singleton_10']:.1f} unseen {rec['len_mean']['unseen']:.1f}; "
          f"ESS {W['singleton_10'][1]['ess']:.0f}, covered {W['singleton_10'][1]['covered_target_mass']:.3f} [{time.time() - t0:.0f}s]", flush=True)
    for mn in SIX:
        tm = time.time()
        net, im, fm = MINERS[mn](train)
        rs = token_replay.apply(shadow, net, im, fm)
        f = np.array([r["trace_fitness"] for r in rs])
        a = np.array([1.0 if r["trace_is_fit"] else 0.0 for r in rs])
        ru = token_replay.apply(EventLog([reps[k] for k in un]), net, im, fm)
        ref = float(np.dot([r["trace_fitness"] for r in ru], uw) / uw.sum())
        ref_s = float(np.dot([1.0 if r["trace_is_fit"] else 0.0 for r in ru], uw) / uw.sum())
        row = {"ref": ref, "ref_strict": ref_s, "score": float(f.mean()), "score_strict": float(a.mean())}
        for k, (w, _) in W.items():
            row[f"score_{k}"] = float(np.dot(w, f) / w.sum())
            row[f"score_strict_{k}"] = float(np.dot(w, a) / w.sum())
        rec["miners"][mn] = row
        print(f"  {mn:21s} ref {ref:.3f} score {row['score']:.3f} ({row['score'] - ref:+.3f}) singleton {row['score_singleton_10']:.3f} "
              f"({row['score_singleton_10'] - ref:+.3f}) oracle {row['score_oracle_10']:.3f} ({row['score_oracle_10'] - ref:+.3f}) | strict ref "
              f"{ref_s:.3f} score {row['score_strict']:.3f} singleton {row['score_strict_singleton_10']:.3f} [{time.time() - tm:.0f}s]", flush=True)
    refs = [rec["miners"][m]["ref"] for m in SIX]
    refs_s = [rec["miners"][m]["ref_strict"] for m in SIX]
    rec["criteria"] = {}
    for k in ["score"] + [f"score_{x}" for x in W]:
        rec["criteria"][k] = criteria([rec["miners"][m][k] for m in SIX], refs)
    for k in ["score_strict"] + [f"score_strict_{x}" for x in W]:
        if np.std(refs_s) > 1e-9:
            rec["criteria"][k] = criteria([rec["miners"][m][k] for m in SIX], refs_s)
    for k in ("score", "score_singleton_10", "score_oracle_10"):
        c = rec["criteria"][k]
        print(f"  {k:20s} Pearson {c['pearson']:.3f} Spearman {c['spearman']:.2f} MAE {c['mae']:.3f} spread {c['spread']:.2f}/{c['spread_ref']:.2f} "
              f"max dev {c['max_abs_dev']:.3f}", flush=True)
    rec["seconds"] = time.time() - t0
    rec["protocol"] = ("v2.6 generate_shadow_log seed 42 " + str(GEN_KW) + "; weights = target share / shadow share per length bin "
                       "(deciles of the target lengths), normalized to mean 1; target = training singletons (or unseen cases, oracle); "
                       "pm4py " + pm4py.__version__)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"{dkey}_{split}.json"), "w", encoding="utf-8") as fp:
        json.dump(rec, fp, indent=1)
    return rec


def summarize(keys):
    recs = []
    for k in keys:
        for s in ("temporal", "random"):
            p = os.path.join(OUT_DIR, f"{k}_{s}.json")
            if os.path.exists(p):
                recs.append(json.load(open(p, encoding="utf-8")))
    L = ["# Singleton length weighting of the shadow log (sensitivity analysis)", "",
         "Reference: replay fitness of the test cases whose variant is absent from training, same nets as the score.", "",
         "| log | split | singleton share of cases | mean length: cases / singletons / shadow / weighted / unseen | ESS | weighting | Pearson | Spearman | tau_b | MAE | spread (ref) | max dev |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in recs:
        lm = r["len_mean"]
        for k, lab in (("score", "none"), ("score_singleton_10", "singleton"), ("score_singleton_5", "singleton, 5 bins"),
                       ("score_singleton_20", "singleton, 20 bins"), ("score_oracle_10", "oracle (unseen lengths)")):
            c = r["criteria"][k]
            head = (f"| {r['log']} | {r['split']} | {r['singleton_share_of_cases']:.3f} | {lm['cases']:.1f} / {lm['singletons']:.1f} / {lm['shadow']:.1f} / "
                    f"{lm['shadow_weighted_singleton_10']:.1f} / {lm['unseen']:.1f} | {r['weights']['singleton_10']['ess']:.0f} |") if k == "score" else "| | | | | |"
            L.append(f"{head} {lab} | {c['pearson']:.3f} | {c['spearman']:.2f} | {c['kendall_b']:.2f} | {c['mae']:.3f} | {c['spread']:.2f} ({c['spread_ref']:.2f}) | {c['max_abs_dev']:.3f} |")
    L += ["", "## Per miner: score minus reference (graded)", "", "| log | split | miner | reference | none | singleton | oracle |", "|---|---|---|---|---|---|---|"]
    for r in recs:
        for m in SIX:
            x = r["miners"][m]
            L.append(f"| {r['log']} | {r['split']} | {m} | {x['ref']:.3f} | {x['score'] - x['ref']:+.3f} | {x['score_singleton_10'] - x['ref']:+.3f} | {x['score_oracle_10'] - x['ref']:+.3f} |")
    L += ["", "## Strict reading against the perfect-replay share of the unseen cases", "", "| log | split | weighting | Pearson | MAE | max dev |", "|---|---|---|---|---|---|"]
    for r in recs:
        for k, lab in (("score_strict", "none"), ("score_strict_singleton_10", "singleton"), ("score_strict_oracle_10", "oracle")):
            if k in r["criteria"]:
                c = r["criteria"][k]
                L.append(f"| {r['log']} | {r['split']} | {lab} | {c['pearson']:.3f} | {c['mae']:.3f} | {c['max_abs_dev']:.3f} |")
    name = "summary_" + "_".join(keys) + ".md"
    open(os.path.join(OUT_DIR, name), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    keys = [a for a in sys.argv[1:] if a.startswith("D")] or ["D1", "D2", "D3", "D5"]
    splits = ["random"] if "--random-only" in sys.argv else ["temporal", "random"]
    if "--summary" not in sys.argv:
        for k in keys:
            for s in splits:
                try:
                    process(k, s)
                except Exception as e:  # noqa: BLE001
                    import traceback
                    traceback.print_exc()
                    print(f"[{k} {s}] FAIL {type(e).__name__}: {e}", flush=True)
    summarize(keys)


if __name__ == "__main__":
    main()
