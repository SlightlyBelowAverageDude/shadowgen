"""Singleton length weighting against R1, the paper's headline reference (sensitivity analysis).

Reproduces the benchmark's ShadowGen cell (results/configs/<log>__<miner>__M1g.json: cached nets from
benchmark/models/<key>/, seed 42, 5 draws of 1,000 traces, N=6, tau=5, mle) and adds the singleton-weighted score on
the same nets and the same shadow logs. Weight of a shadow trace = share of the full log's singleton variants in its
length bin / share of that draw in the bin (deciles of the singleton lengths), normalized to mean 1 per draw.
R1 is read from results/configs/<log>__<miner>__R1.json (read only): variant-based 5-fold CV, 3 shuffles, token-
aggregated replay fitness of the held-out cases, on nets rediscovered per fold.

Output: results/singleton_weighting/r1_<key>.json and summary_r1.md (new files).
Run from the repo root:  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/singleton_weighting_r1.py D1 D2 D3 D5 D4
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
import pm4py  # noqa: E402
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay  # noqa: E402

from datasets import DATASETS, get_log_path  # noqa: E402
from miners import MINERS  # noqa: E402
from temporal_holdout import variants  # noqa: E402
from singleton_weighting import length_weights, criteria  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "singleton_weighting")
CFG = os.path.join(_HERE, "results", "configs")
LKEY = {"D1": "L1", "D2": "L2", "D3": "L3", "D4": "L4", "D5": "L5"}
SIX = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
GEN_KW = dict(num_traces=1000, safe_threshold=5, max_n=6, successor_weighting="mle")
DRAWS = 5


def stored(ds, miner, method):
    d = json.load(open(os.path.join(CFG, f"{ds}__{miner}__{method}.json"), encoding="utf-8"))
    return d.get("results", d.get("result"))


def process(dkey):
    t0 = time.time()
    ds = DATASETS[dkey]["name"]
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    vc = variants(log)
    singles = [len(v) for v, c in vc.items() if c == 1]
    lens_case = np.repeat([len(v) for v in vc], list(vc.values())).astype(float)
    gen = load_algorithm("v2.6").generate_shadow_log
    random.seed(42)
    np.random.seed(42)
    draws = []
    for _ in range(DRAWS):
        sh, flags, dup, trunc, cap = gen(log, **GEN_KW)
        sl = [len(t) for t in sh]
        w, info = length_weights(sl, singles, 10)
        draws.append((sh, np.asarray(sl, float), w, info))
    rec = {"log": LKEY[dkey], "dataset": ds, "n_cases": len(log), "n_variants": len(vc), "n_singletons": len(singles),
           "len_mean": {"cases": float(lens_case.mean()), "variants": float(np.mean([len(v) for v in vc])),
                        "singletons": float(np.mean(singles)),
                        "cases_token_weighted": float((lens_case ** 2).sum() / lens_case.sum()),
                        "shadow": float(np.mean([d[1].mean() for d in draws])),
                        "shadow_weighted": float(np.mean([np.dot(d[2], d[1]) / d[2].sum() for d in draws]))},
           "ess": [d[3]["ess"] for d in draws], "miners": {}}
    print(f"\n=== {rec['log']} {ds}: cases {len(log)}, variants {len(vc)}, singletons {len(singles)}; mean length cases "
          f"{rec['len_mean']['cases']:.1f} (token-weighted {rec['len_mean']['cases_token_weighted']:.1f}) variants "
          f"{rec['len_mean']['variants']:.1f} singletons {rec['len_mean']['singletons']:.1f} shadow {rec['len_mean']['shadow']:.1f} "
          f"weighted {rec['len_mean']['shadow_weighted']:.1f}; ESS {np.mean(rec['ess']):.0f} [{time.time() - t0:.0f}s]", flush=True)
    def run(net, im, fm):
        s_u, s_w, a_u, a_w = [], [], [], []
        for sh, sl, w, _ in draws:
            rs = token_replay.apply(sh, net, im, fm)
            f = np.array([r["trace_fitness"] for r in rs])
            a = np.array([1.0 if r["trace_is_fit"] else 0.0 for r in rs])
            s_u.append(f.mean())
            s_w.append(np.dot(w, f) / w.sum())
            a_u.append(a.mean())
            a_w.append(np.dot(w, a) / w.sum())
        return s_u, s_w, a_u, a_w

    for mn in SIX:
        tm = time.time()
        m1g, r1 = stored(ds, mn, "M1g"), stored(ds, mn, "R1")
        net, im, fm = pm4py.read_pnml(os.path.join(_HERE, "models", dkey, f"{mn}.pnml"))
        s_u, s_w, a_u, a_w = run(net, im, fm)
        source, cached_score = "cached PNML", float(np.mean(s_u))
        if abs(cached_score - m1g["mean"]) > 0.001:
            # the cache can differ from the net that produced the stored cell (D2 Alpha+: PNML round trip rewires it)
            net2, im2, fm2 = MINERS[mn](log)
            alt = run(net2, im2, fm2)
            if abs(np.mean(alt[0]) - m1g["mean"]) < abs(cached_score - m1g["mean"]):
                net, (s_u, s_w, a_u, a_w), source = net2, alt, "in-memory discovery (cache does not reproduce the stored cell)"
            print(f"  {mn}: cached net gives {cached_score:.4f} against stored {m1g['mean']:.4f}; in-memory {np.mean(alt[0]):.4f}; using {source}", flush=True)
        r1a = stored(ds, mn, "R1accept") if os.path.exists(os.path.join(CFG, f"{ds}__{mn}__R1accept.json")) else None
        row = {"r1": r1["mean"], "r1_accept": r1a.get("accept_mean", r1a.get("mean")) if r1a else None, "m1g_stored": m1g["mean"],
               "accept_stored": m1g.get("gen_accept"), "score": float(np.mean(s_u)), "score_weighted": float(np.mean(s_w)),
               "score_k1": float(s_u[0]), "score_weighted_k1": float(s_w[0]), "accept": float(np.mean(a_u)),
               "accept_weighted": float(np.mean(a_w)), "n_transitions": len(net.transitions), "net_source": source,
               "cached_net_score": cached_score}
        rec["miners"][mn] = row
        print(f"  {mn:21s} R1 {row['r1']:.3f} | stored {row['m1g_stored']:.3f} fresh {row['score']:.3f} (diff {row['score'] - row['m1g_stored']:+.4f}) "
              f"weighted {row['score_weighted']:.3f} | gap {row['score'] - row['r1']:+.3f} -> {row['score_weighted'] - row['r1']:+.3f} "
              f"| accept {row['accept']:.3f} weighted {row['accept_weighted']:.3f} R1-accept {row['r1_accept']} [{time.time() - tm:.0f}s]", flush=True)
    r1v = [rec["miners"][m]["r1"] for m in SIX]
    rec["criteria"] = {k: criteria([rec["miners"][m][k] for m in SIX], r1v)
                       for k in ("m1g_stored", "score", "score_weighted", "score_k1", "score_weighted_k1")}
    r1a = [rec["miners"][m]["r1_accept"] for m in SIX]
    if all(x is not None for x in r1a) and np.std(r1a) > 1e-9:
        rec["criteria_accept"] = {k: criteria([rec["miners"][m][k] for m in SIX], r1a) for k in ("accept", "accept_weighted")}
    for k in ("m1g_stored", "score", "score_weighted"):
        c = rec["criteria"][k]
        print(f"  {k:15s} Pearson {c['pearson']:.3f} Spearman {c['spearman']:.2f} MAE {c['mae']:.3f} spread {c['spread']:.2f}/{c['spread_ref']:.2f} "
              f"max dev {c['max_abs_dev']:.3f}", flush=True)
    rec["seconds"] = time.time() - t0
    rec["protocol"] = (f"cached nets benchmark/models/{dkey}; seed 42; {DRAWS} draws; " + str(GEN_KW) +
                       "; singleton weights per draw, deciles; pm4py " + pm4py.__version__)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"r1_{dkey}.json"), "w", encoding="utf-8") as fp:
        json.dump(rec, fp, indent=1)


def summarize():
    recs = [json.load(open(os.path.join(OUT_DIR, f"r1_{k}.json"), encoding="utf-8"))
            for k in ("D1", "D2", "D3", "D4", "D5") if os.path.exists(os.path.join(OUT_DIR, f"r1_{k}.json"))]
    L = ["# Singleton length weighting against R1", "",
         "Score: 5 draws of 1,000 shadow traces on the cached benchmark nets (as the stored M1g cell). R1: stored, read only.", "",
         "| log | mean length: cases / token-weighted cases / singletons / shadow / weighted | ESS | score | Pearson | Spearman | tau_b | MAE | spread (R1) | max dev |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in recs:
        lm = r["len_mean"]
        for k, lab in (("m1g_stored", "stored"), ("score", "fresh"), ("score_weighted", "weighted"), ("score_k1", "fresh, K=1"),
                       ("score_weighted_k1", "weighted, K=1")):
            c = r["criteria"][k]
            head = (f"| {r['log']} | {lm['cases']:.1f} / {lm['cases_token_weighted']:.1f} / {lm['singletons']:.1f} / {lm['shadow']:.1f} / "
                    f"{lm['shadow_weighted']:.1f} | {np.mean(r['ess']):.0f} |") if k == "m1g_stored" else "| | | |"
            L.append(f"{head} {lab} | {c['pearson']:.3f} | {c['spearman']:.2f} | {c['kendall_b']:.2f} | {c['mae']:.3f} | {c['spread']:.2f} ({c['spread_ref']:.2f}) | {c['max_abs_dev']:.3f} |")
    L += ["", "## Per miner", "", "| log | miner | R1 | stored | fresh | fresh - stored | weighted | gap fresh | gap weighted |", "|---|---|---|---|---|---|---|---|---|"]
    for r in recs:
        for m in SIX:
            x = r["miners"][m]
            L.append(f"| {r['log']} | {m} | {x['r1']:.3f} | {x['m1g_stored']:.3f} | {x['score']:.3f} | {x['score'] - x['m1g_stored']:+.4f} | "
                     f"{x['score_weighted']:.3f} | {x['score'] - x['r1']:+.3f} | {x['score_weighted'] - x['r1']:+.3f} |")
    L += ["", "## Strict reading against R1-accept", "", "| log | score | Pearson | MAE | max dev |", "|---|---|---|---|---|"]
    for r in recs:
        for k in ("accept", "accept_weighted"):
            if "criteria_accept" in r:
                c = r["criteria_accept"][k]
                L.append(f"| {r['log']} | {k} | {c['pearson']:.3f} | {c['mae']:.3f} | {c['max_abs_dev']:.3f} |")
    open(os.path.join(OUT_DIR, "summary_r1.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    keys = [a for a in sys.argv[1:] if a.startswith("D")] or ["D1", "D2", "D3", "D5", "D4"]
    if "--summary" not in sys.argv:
        for k in keys:
            try:
                process(k)
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                print(f"[{k}] FAIL {type(e).__name__}: {e}", flush=True)
    summarize()


if __name__ == "__main__":
    main()
