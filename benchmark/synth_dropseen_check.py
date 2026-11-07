"""Seen shadow traces: keep them (v2.6) or drop them, tested on the synthetic known systems.

The v2.6 generator retries 100 times to draw a trace whose variant is absent from the training log
and then keeps a seen one (duplicates_kept). Eq. (1) conditions on unseen behavior, so a seen trace
does not belong in the scored set. This script scores every variant twice on the same shadow log:

  keep   all traces of the variant (as stored: unfiltered, six rules, extended rules)
  drop   the same traces without those whose variant is in the training log (suffix _u)

Setup as synth_filter_check.py (same systems, seeds, generator settings, rules, models). pm4py's
play-out is not reproducible across processes, so the logs are a resample and the keep columns are
recomputed here; they are compared with the stored run in the summary.

Reference: acceptance of the unseen part of the 2,500 fresh traces (as before). Where that part
holds fewer than MIN_REF traces, a second reference is drawn from N_BIG fresh traces (seed + 3) and
reported beside the first one.

Output: results/shadow_filter/synth_dropseen[_tag].json and summary_synth_dropseen[_tag].md.
Nothing else is written. Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/synth_dropseen_check.py [--limit N] [--tag T]
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

import synth_ground_truth as sgt  # noqa: E402
from shadow_validity_check import invariants, violations  # noqa: E402
from synth_survivor_check import extra_rules, extra_violations  # noqa: E402
from synth_filter_check import seq, replay, m, SEED, GEN_KW, STORED, OUT_DIR  # noqa: E402
from HybridGen.algorithm.v26 import generate_shadow_log  # noqa: E402

MIN_REF = 250
N_BIG = 25000
BASE = ["sg", "all", "ext"]
PREDS = [("unfiltered, keep", "sg"), ("unfiltered, drop", "sg_u"), ("six rules, keep", "all"),
         ("six rules, drop", "all_u"), ("extended, keep", "ext"), ("extended, drop", "ext_u"), ("fitness", "fit")]


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
        F_big = None
        if len(F_unseen) < MIN_REF:
            FB = sgt.playout(S_net, S_im, S_fm, N_BIG, seed + 3)
            F_big = EventLog([t for t in FB if seq(t) not in vL])
        inv = invariants([seq(t) for t in L])
        R = extra_rules(list(vL))

        random.seed(SEED)
        np.random.seed(SEED)
        shadow, flags, dup, trunc, cap = generate_shadow_log(L, **GEN_KW)
        seqs = [seq(t) for t in shadow]
        unseen = np.array([q not in vL for q in seqs])
        vio = [violations(q, inv) for q in seqs]
        xv = [extra_violations(q, R) for q in seqs]
        six = np.array([not any(v.values()) for v in vio])
        masks = {"sg": np.ones(len(seqs), bool), "all": six,
                 "ext": six & np.array([not (x["impl"] or x["balance"]) for x in xv])}
        for k in BASE:
            masks[k + "_u"] = masks[k] & unseen
        _, valid = replay(shadow, S_net, S_im, S_fm)
        valid = valid.astype(bool)
        rec = {"mode": mode, "seed": seed, "tree_matches_stored": str(tree)[:200] == s["tree"],
               "var_L": len(vL), "n_F_unseen": len(F_unseen), "n_F_big_unseen": None if F_big is None else len(F_big),
               "duplicates_kept": int(dup), "seen_in_shadow": int((~unseen).sum()),
               "unseen_shadow_variants": len({q for q, u in zip(seqs, unseen) if u}),
               "mutated_share": float(np.mean(flags)), "models": {}}
        for k, mk in masks.items():
            rec[f"n_{k}"] = int(mk.sum())
            rec[f"valid_{k}"] = m(valid[mk])
        for name, fn in sgt.MINERS.items():
            r = {"error": None}
            try:
                net, im, fm = fn(L)
                g, st = replay(shadow, net, im, fm)
                for k, mk in masks.items():
                    r[f"{k}_g"], r[f"{k}_s"] = m(g[mk]), m(st[mk])
                r["fit_g"], r["fit_s"] = sgt.avg_fit(L, net, im, fm)
                r["truth_g"], r["truth_s"] = sgt.avg_fit(F_unseen, net, im, fm) if len(F_unseen) else (None, None)
                r["big_g"], r["big_s"] = sgt.avg_fit(F_big, net, im, fm) if F_big is not None and len(F_big) else (None, None)
            except Exception as e:  # noqa: BLE001
                r["error"] = f"{type(e).__name__}: {e}"
            rec["models"][name] = r
        out.append(rec)
        print(f"[{idx + 1}/{len(stored)}] mode={mode} seed={seed} dup {dup} (seen {rec['seen_in_shadow']}) "
              f"scored ext keep {rec['n_ext']} drop {rec['n_ext_u']} | unseen fresh {len(F_unseen)}"
              + (f" big {len(F_big)}" if F_big is not None else "") + f" [{time.time() - t0:.0f}s]", flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    res = {"protocol": "seed 42; 1,000 shadow traces; N=6, tau=5, mle; v2.6 generator; rules from the 300-trace "
                       f"training log; second reference from {N_BIG} fresh traces where the first holds fewer than "
                       f"{MIN_REF} unseen traces; pm4py " + pm4py.__version__,
           "n_systems": len(out), "runtime_s": time.time() - t0, "systems": out}
    json.dump(res, open(os.path.join(OUT_DIR, "synth_dropseen" + (f"_{tag}" if tag else "") + ".json"), "w",
                        encoding="utf-8"), indent=1)
    return res


def pairs(S, ref, need):
    """(system, model record) pairs of the six miners where the reference and every needed predictor exist."""
    return [(s, r) for s in S for n, r in s["models"].items() if n in sgt.REAL_MINERS and not r["error"]
            and all(r.get(f"{ref}_{suf}") is not None for suf in "sg")
            and all(r.get(f"{k}_s") is not None for k in need)]


def table(P, ref):
    L = ["| reading | predictor | pairs | MAE | signed | off by > 0.2 |", "|---|---|---|---|---|---|"]
    for reading, suf in (("strict", "s"), ("graded", "g")):
        for pname, pk in PREDS:
            a = np.array([r[f"{pk}_{suf}"] for _, r in P])
            t = np.array([r[f"{ref}_{suf}"] for _, r in P])
            L.append(f"| {reading} | {pname} | {len(P)} | {np.mean(np.abs(a - t)):.3f} | {np.mean(a - t):+.3f} | "
                     f"{int(np.sum(np.abs(a - t) > 0.2))} |")
    return L


def summarize(res, tag=""):
    S = res["systems"]
    need = [k for _, k in PREDS]
    pad = [s for s in S if s["duplicates_kept"] > 0]
    L = [f"# Seen shadow traces kept or dropped, synthetic known systems ({res['n_systems']} systems; {res['protocol']})", "",
         f"Trees match the stored study on {sum(s['tree_matches_stored'] for s in S)} of {len(S)}; logs resampled. "
         f"Model errors: {sum(1 for s in S for r in s['models'].values() if r['error'])}. "
         f"Seen traces in the shadow log equal duplicates_kept on {sum(s['seen_in_shadow'] == s['duplicates_kept'] for s in S)} "
         f"of {len(S)} systems.", "",
         "## A. Padding", "",
         f"Systems where the generator keeps seen traces: {len(pad)} of {len(S)} "
         f"(more than 500 of 1,000 on {sum(s['duplicates_kept'] > 500 for s in S)}; all 1,000 on "
         f"{sum(s['duplicates_kept'] == 1000 for s in S)}).",
         f"Systems with no unseen trace in the 2,500 fresh traces: {sum(s['n_F_unseen'] == 0 for s in S)}; "
         f"of these, systems with no unseen shadow trace: "
         f"{sum(s['n_F_unseen'] == 0 and s['n_sg_u'] == 0 for s in S)}.",
         f"Systems with no trace left to score after the drop: unfiltered {sum(s['n_sg_u'] == 0 for s in S)}, "
         f"six rules {sum(s['n_all_u'] == 0 for s in S)}, extended {sum(s['n_ext_u'] == 0 for s in S)} "
         f"(extended, keep: {sum(s['n_ext'] == 0 for s in S)}).", ""]
    if pad:
        L += ["| padded system | variants in L | seen kept | unseen shadow traces (variants) | scored, extended drop | "
              "valid share of those | unseen fresh, 2,500 | unseen fresh, 25,000 |", "|---|---|---|---|---|---|---|---|"]
        for s in sorted(pad, key=lambda s: -s["duplicates_kept"]):
            L.append(f"| {s['mode']}/{s['seed']} | {s['var_L']} | {s['duplicates_kept']} | {s['n_sg_u']} "
                     f"({s['unseen_shadow_variants']}) | {s['n_ext_u']} | "
                     f"{'-' if s['valid_ext_u'] is None else format(s['valid_ext_u'], '.3f')} | {s['n_F_unseen']} | "
                     f"{'-' if s['n_F_big_unseen'] is None else s['n_F_big_unseen']} |")
    groups = [("all systems", S),
              ("padded (seen traces kept)", pad),
              ("no padding, scored set (extended) below 0.9 valid",
               [s for s in S if s["duplicates_kept"] == 0 and (s["valid_ext"] or 0) < 0.9]),
              ("no padding, scored set (extended) at least 0.9 valid",
               [s for s in S if s["duplicates_kept"] == 0 and (s["valid_ext"] or 0) >= 0.9])]
    L += ["", "## B. Score accuracy, six miners, every predictor on the same pairs; reference = unseen part of 2,500 fresh traces"]
    for gname, G in groups:
        P = pairs(G, "truth", need)
        L += ["", f"### {gname}: {len({(s['mode'], s['seed']) for s, _ in P})} of {len(G)} systems", ""]
        L += table(P, "truth") if P else ["no pair"]
    big = [s for s in S if s["n_F_big_unseen"]]
    L += ["", f"## C. Systems with the second reference (unseen part of {N_BIG} fresh traces): {len(big)}", ""]
    if big:
        nb = [s["n_F_big_unseen"] for s in big]
        d = [abs(r["big_s"] - r["truth_s"]) for s in big for n, r in s["models"].items()
             if n in sgt.REAL_MINERS and not r["error"] and r.get("big_s") is not None and r.get("truth_s") is not None]
        L += [f"Unseen traces in the second reference: median {np.median(nb):.0f}, min {min(nb)}, max {max(nb)}. "
              f"Strict reference values, first against second: mean absolute difference "
              f"{np.mean(d) if d else float('nan'):.3f} over {len(d)} pairs."]
        for gname, G in (("padded", [s for s in big if s["duplicates_kept"] > 0]),
                         ("not padded", [s for s in big if s["duplicates_kept"] == 0])):
            P = pairs(G, "big", need)
            L += ["", f"### {gname}: {len({(s['mode'], s['seed']) for s, _ in P})} of {len(G)} systems", ""]
            L += table(P, "big") if P else ["no pair"]
    keys = ["truth", "big"] + need
    L += ["", "## D. Poles (mean over systems with a value): " + " / ".join(
          {"truth": "reference", "big": "second reference"}.get(k, dict((b, a) for a, b in PREDS).get(k, k)) for k in keys), "",
          "| model | group | strict | graded |", "|---|---|---|---|"]
    for name in sgt.POLES:
        for gname, G in (("all", S), ("padded", pad)):
            def cell(suf):
                out = []
                for k in keys:
                    v = [s["models"][name][f"{k}_{suf}"] for s in G if not s["models"][name]["error"]
                         and s["models"][name].get(f"{k}_{suf}") is not None]
                    out.append(f"{np.mean(v):.3f}" if v else "-")
                return " / ".join(out)
            L.append(f"| {name} | {gname} | {cell('s')} | {cell('g')} |")
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT_DIR, "summary_synth_dropseen" + (f"_{tag}" if tag else "") + ".md"), "w",
              encoding="utf-8") as fp:
        fp.write(text)
    print(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--summary-only", action="store_true")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    stem = "synth_dropseen" + (f"_{a.tag}" if a.tag else "")
    summarize(json.load(open(os.path.join(OUT_DIR, stem + ".json"), encoding="utf-8")) if a.summary_only
              else run(a.limit, a.tag), a.tag)
