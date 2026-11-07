"""Rule filter on the shadow traces, tested on the synthetic known systems.

On a known system S the validity of a shadow trace is exact (S replays it or not), so the filter of
shadow_filter_test.py can be judged directly. For every stored system the script regenerates S, the
300-trace training log L and the fresh 2,500-trace sample F with the stored seeds (as
synth_premise_check.py does), draws the shadow log once (seed 42, 1,000 traces, N=6, tau=5, mle),
derives the rules from L (shadow_validity_check.invariants) and records:

  filter quality   valid share of the shadow traces before and after the filter; share of the valid
                   and of the invalid shadow traces the filter removes; share of the fresh unseen
                   traces of F (all valid by construction) the filter would remove
  score accuracy   for the eight models discovered from L: ShadowGen unfiltered, filter all,
                   filter cm (count and mandatory rules only), and training fitness, against the
                   acceptance of the unseen part of F (strict and graded)

pm4py's play-out is not reproducible across processes, so the logs are a resample of the stored study.
Two further filters come from synth_survivor_check.extra_rules: impl (the six rules and "a implies b")
and ext (impl and the balance rule).

Output: results/shadow_filter/synth_filter[_tag].json and summary_synth[_tag].md (nothing overwritten
elsewhere). The first run (no tag) holds the all and cm filters only; the run with --tag ext adds impl and ext.
Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/synth_filter_check.py [--limit N] [--tag ext]
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
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, _HERE)

import numpy as np  # noqa: E402
import pm4py  # noqa: E402
from pm4py.objects.log.obj import EventLog  # noqa: E402
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay  # noqa: E402

import synth_ground_truth as sgt  # noqa: E402
from shadow_validity_check import invariants, violations  # noqa: E402
from synth_survivor_check import extra_rules, extra_violations  # noqa: E402
from HybridGen.algorithm.v26 import generate_shadow_log  # noqa: E402

SEED = 42
GEN_KW = dict(num_traces=1000, safe_threshold=5, max_n=6, successor_weighting="mle")
STORED = os.path.join(_HERE, "results", "synth_ground_truth.json")
OUT_DIR = os.path.join(_HERE, "results", "shadow_filter")
PREDS = [("unfiltered", "sg"), ("filter all", "all"), ("filter cm", "cm"), ("filter impl", "impl"),
         ("filter ext", "ext"), ("fitness", "fit")]
LABELS = {"all": "all rules", "cm": "count and mandatory", "impl": "six rules and impl",
          "ext": "six rules, impl and balance"}


def seq(t):
    return tuple(e["concept:name"] for e in t)


def replay(log, net, im, fm):
    res = token_replay.apply(log, net, im, fm)
    g = np.array([float(r["trace_fitness"]) for r in res])
    s = np.array([1.0 if r.get("trace_is_fit", r["trace_fitness"] >= 1.0) else 0.0 for r in res])
    return g, s


def m(v):
    return float(np.mean(v)) if len(v) else None


def run(limit, tag=""):
    stored = json.load(open(STORED, encoding="utf-8"))["systems"]
    if limit:
        stored = stored[:limit]
    out, t0 = [], time.time()
    for idx, s in enumerate(stored):
        mode, seed = s["mode"], s["seed"]
        tree, S_net, S_im, S_fm = sgt.gen_system(mode, seed)
        F = sgt.playout(S_net, S_im, S_fm, sgt.N_F, seed + 1)
        L = sgt.playout(S_net, S_im, S_fm, sgt.N_L, seed + 2)
        vL = sgt.variants(L)
        F_unseen = EventLog([t for t in F if seq(t) not in vL])
        inv = invariants([seq(t) for t in L])
        R = extra_rules(list(vL))

        random.seed(SEED)
        np.random.seed(SEED)
        shadow, flags, dup, trunc, cap = generate_shadow_log(L, **GEN_KW)
        vio = [violations(seq(t), inv) for t in shadow]
        xv = [extra_violations(seq(t), R) for t in shadow]
        six = np.array([not any(v.values()) for v in vio])
        masks = {"all": six,
                 "cm": np.array([not (v["count"] or v["mandatory"]) for v in vio]),
                 "impl": six & np.array([not x["impl"] for x in xv]),
                 "ext": six & np.array([not (x["impl"] or x["balance"]) for x in xv])}
        _, valid = replay(shadow, S_net, S_im, S_fm)
        valid = valid.astype(bool)
        fv = [violations(seq(t), inv) for t in F_unseen]
        fx = [extra_violations(seq(t), R) for t in F_unseen]
        rec = {"mode": mode, "seed": seed, "tree_matches_stored": str(tree)[:200] == s["tree"],
               "var_L": len(vL), "n_F_unseen": len(F_unseen), "mutated_share": float(np.mean(flags)),
               "duplicates_kept": int(dup), "valid": float(valid.mean()), "models": {}}
        for name, mk in masks.items():
            rec[f"kept_{name}"] = float(mk.mean())
            rec[f"valid_kept_{name}"] = m(valid[mk])
            rec[f"valid_removed_{name}"] = m(~mk[valid])        # share of the valid traces removed
            rec[f"invalid_removed_{name}"] = m(~mk[~valid])     # share of the invalid traces removed
        rec["F_unseen_removed_all"] = m([any(v.values()) for v in fv])
        rec["F_unseen_removed_cm"] = m([v["count"] or v["mandatory"] for v in fv])
        rec["F_unseen_removed_impl"] = m([any(v.values()) or x["impl"] for v, x in zip(fv, fx)])
        rec["F_unseen_removed_ext"] = m([any(v.values()) or x["impl"] or x["balance"] for v, x in zip(fv, fx)])
        for name, fn in sgt.MINERS.items():
            r = {"error": None}
            try:
                net, im, fm = fn(L)
                g, st = replay(shadow, net, im, fm)
                r["sg_g"], r["sg_s"] = float(g.mean()), float(st.mean())
                for mn, mk in masks.items():
                    r[f"{mn}_g"] = m(g[mk])
                    r[f"{mn}_s"] = m(st[mk])
                r["fit_g"], r["fit_s"] = sgt.avg_fit(L, net, im, fm)
                if len(F_unseen):
                    r["truth_g"], r["truth_s"] = sgt.avg_fit(F_unseen, net, im, fm)
                else:
                    r["truth_g"], r["truth_s"] = None, None
            except Exception as e:  # noqa: BLE001
                r["error"] = f"{type(e).__name__}: {e}"
            rec["models"][name] = r
        out.append(rec)
        print(f"[{idx + 1}/{len(stored)}] mode={mode} seed={seed} valid {rec['valid']:.3f} -> "
              f"all {rec['valid_kept_all'] if rec['valid_kept_all'] is not None else float('nan'):.3f} "
              f"(kept {rec['kept_all']:.3f}) ext "
              f"{rec['valid_kept_ext'] if rec['valid_kept_ext'] is not None else float('nan'):.3f} "
              f"(kept {rec['kept_ext']:.3f}) [{time.time() - t0:.0f}s]", flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    res = {"protocol": "seed 42; 1,000 shadow traces; N=6, tau=5, mle; v2.6 generator; rules from the 300-trace "
                       "training log; pm4py " + pm4py.__version__,
           "n_systems": len(out), "runtime_s": time.time() - t0, "systems": out}
    json.dump(res, open(os.path.join(OUT_DIR, "synth_filter" + (f"_{tag}" if tag else "") + ".json"), "w",
                        encoding="utf-8"), indent=1)
    return res


def row(label, vals):
    v = np.array([x for x in vals if x is not None], float)
    if not len(v):
        return f"| {label} | 0 | - | - | - | - | - | - |"
    q = np.percentile(v, [0, 25, 50, 75, 100])
    return f"| {label} | {len(v)} | {v.mean():.3f} | {q[0]:.3f} | {q[1]:.3f} | {q[2]:.3f} | {q[3]:.3f} | {q[4]:.3f} |"


def b2(S, names):
    """Six miners, every predictor on the same (system, model) pairs."""
    out = []
    last = names[-1]
    for reading, suf in (("strict", "s"), ("graded", "g")):
        pairs = [r for s in S for n, r in s["models"].items() if n in sgt.REAL_MINERS and not r["error"]
                 and r.get(f"truth_{suf}") is not None and r.get(f"{last}_{suf}") is not None]
        for pname, pk in PREDS:
            if pk in LABELS and pk not in names:
                continue
            a = np.array([r[f"{pk}_{suf}"] for r in pairs])
            t = np.array([r[f"truth_{suf}"] for r in pairs])
            out.append(f"| {reading} | {pname} | {len(pairs)} | {np.mean(np.abs(a - t)):.3f} | {np.mean(a - t):+.3f} |")
    return out


def summarize(res, tag=""):
    S = res["systems"]
    names = [n for n in LABELS if f"kept_{n}" in S[0]]
    L = [f"# Rule filter on the synthetic known systems ({res['n_systems']} systems; {res['protocol']})", "",
         f"Trees match the stored study on {sum(s['tree_matches_stored'] for s in S)} of {len(S)}; logs resampled. "
         f"Model errors: {sum(1 for s in S for r in s['models'].values() if r['error'])}.", "",
         "## A. Filter quality (per system)", "",
         "| quantity | n | mean | min | Q1 | median | Q3 | max |", "|---|---|---|---|---|---|---|---|",
         row("shadow traces in the system's language, unfiltered", [s["valid"] for s in S])]
    for n in names:
        lab = LABELS[n]
        L += [row(f"same, after the filter ({lab})", [s[f"valid_kept_{n}"] for s in S]),
              row(f"shadow traces kept ({lab})", [s[f"kept_{n}"] for s in S]),
              row(f"invalid shadow traces removed ({lab})", [s[f"invalid_removed_{n}"] for s in S]),
              row(f"valid shadow traces removed ({lab})", [s[f"valid_removed_{n}"] for s in S]),
              row(f"fresh unseen system traces the filter would remove ({lab})", [s[f"F_unseen_removed_{n}"] for s in S])]
    tot = {"n": 0.0, "valid": 0.0}
    for s in S:
        tot["n"] += 1000
        tot["valid"] += 1000 * s["valid"]
        for n in names:
            k = 1000 * s[f"kept_{n}"]
            tot[f"kept_{n}"] = tot.get(f"kept_{n}", 0.0) + k
            tot[f"vk_{n}"] = tot.get(f"vk_{n}", 0.0) + k * (s[f"valid_kept_{n}"] or 0.0)
    L += ["", f"Pooled over all {int(tot['n'])} shadow traces: valid {tot['valid'] / tot['n']:.3f}; after the filter: "
          + "; ".join(f"{LABELS[n]} {tot[f'vk_{n}'] / max(tot[f'kept_{n}'], 1):.3f} ({tot[f'kept_{n}'] / tot['n']:.3f} kept)"
                      for n in names) + ".",
          f"Systems with a valid share below 0.9: unfiltered {sum(s['valid'] < 0.9 for s in S)}; "
          + "; ".join(f"{LABELS[n]} {sum((s[f'valid_kept_{n}'] or 0) < 0.9 for s in S)} "
                      f"(no trace kept on {sum(s[f'kept_{n}'] == 0 for s in S)})" for n in names) + ".",
          "", "## B. Score accuracy against the acceptance of unseen system traces", "",
          "Per system: mean absolute error over the models; then mean and median over systems. Pooled: all (system, model) pairs.",
          "", "| models | reading | predictor | systems | mean MAE | median MAE | pooled pairs | pooled MAE | pooled signed | pooled Pearson |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for sname, mset in (("six miners", sgt.REAL_MINERS), ("Inductive_Strict", ["Inductive_Strict"]),
                         ("Inductive_Infrequent", ["Inductive_Infrequent"])):
        for reading, suf in (("strict", "s"), ("graded", "g")):
            for pname, pk in PREDS:
                if pk in LABELS and pk not in names:
                    continue
                per, pa, pt = [], [], []
                for s in S:
                    ms = [r for n, r in s["models"].items() if n in mset and not r["error"]
                          and r.get(f"truth_{suf}") is not None and r.get(f"{pk}_{suf}") is not None]
                    if not ms:
                        continue
                    a = np.array([r[f"{pk}_{suf}"] for r in ms])
                    t = np.array([r[f"truth_{suf}"] for r in ms])
                    per.append(float(np.mean(np.abs(a - t))))
                    pa += list(a)
                    pt += list(t)
                pa, pt = np.array(pa), np.array(pt)
                pr = float(np.corrcoef(pa, pt)[0, 1]) if np.std(pa) > 0 and np.std(pt) > 0 else float("nan")
                L.append(f"| {sname} | {reading} | {pname} | {len(per)} | {np.mean(per):.3f} | {np.median(per):.3f} | "
                         f"{len(pa)} | {np.mean(np.abs(pa - pt)):.3f} | {np.mean(pa - pt):+.3f} | {pr:.3f} |")
    keys = ["truth", "sg"] + names + ["fit"]
    L += ["", "## B2. Six miners, every predictor on the same pairs (systems where the last filter keeps a trace)", "",
          "| reading | predictor | pairs | pooled MAE | pooled signed |", "|---|---|---|---|---|"] + b2(S, names)
    L += ["", "## C. Poles (mean over systems): " + " / ".join(
          {"truth": "truth", "sg": "unfiltered", "fit": "fitness"}.get(k, "filter " + k) for k in keys), "",
          "| model | strict | graded |", "|---|---|---|"]
    for name in sgt.POLES:
        def cell(suf):
            out = []
            for k in keys:
                v = [s["models"][name][f"{k}_{suf}"] for s in S if not s["models"][name]["error"]
                     and s["models"][name].get(f"{k}_{suf}") is not None]
                out.append(f"{np.mean(v):.3f}" if v else "-")
            return " / ".join(out)
        L.append(f"| {name} | {cell('s')} | {cell('g')} |")
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT_DIR, "summary_synth" + (f"_{tag}" if tag else "") + ".md"), "w", encoding="utf-8") as fp:
        fp.write(text)
    print(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--summary-only", action="store_true")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    stem = "synth_filter" + (f"_{a.tag}" if a.tag else "")
    summarize(json.load(open(os.path.join(OUT_DIR, stem + ".json"), encoding="utf-8")) if a.summary_only
              else run(a.limit, a.tag), a.tag)
