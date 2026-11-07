"""Check of HybridGen/algorithm/v27.py against the tested variant (extended rules, seen traces dropped).

v27 re-implements the rules inside the method module. This script checks, without changing any
stored file:

  A  real logs (random 70/30 split of randomization_test.py at p = 0, stored repetitions):
     the traces v27 scores are exactly the drawn traces that are unseen and pass the six rules,
     "a implies b" and balance of the test scripts (shadow_validity_check, synth_survivor_check);
     the v27 score of every stored model equals the stored "filter ext" value of
     results/shadow_filter/filter_<key>_ext.json (no seen trace is kept on these logs, so the
     stored value is the extended-rules, drop-seen value).
  B  known systems (first --systems systems of the stored study, same process, resampled logs):
     same trace identity; the v27 score of every model equals the score computed with the test
     functions on the same shadow log; an empty scored set gives None.

Output: results/v27_check/check.json and summary.md. Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/v27_check.py [D1 D2] [--systems 12]
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

import synth_ground_truth as sgt  # noqa: E402
from miners import MINERS  # noqa: E402
from datasets import DATASETS, get_log_path  # noqa: E402
from randomization_test import randomize, split, acts, SEED, GEN_KW  # noqa: E402
from shadow_validity_check import invariants, violations  # noqa: E402
from synth_survivor_check import extra_rules, extra_violations  # noqa: E402
from synth_filter_check import replay, STORED  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

V26, V27 = load_algorithm("v2.6"), load_algorithm("v2.7")
OUT_DIR = os.path.join(_HERE, "results", "v27_check")
FILTER_DIR = os.path.join(_HERE, "results", "shadow_filter")
KW = {k: v for k, v in GEN_KW.items() if k != "iterations"}


def seed():
    random.seed(SEED)
    np.random.seed(SEED)


def reference(train):
    """Drawn traces and the tested mask (unseen, six rules, implies, balance), with the test functions."""
    variants = {acts(t) for t in train}
    inv, R = invariants([acts(t) for t in train]), extra_rules(list(variants))
    seed()
    drawn, flags, dup, *_ = V26.generate_shadow_log(train, **KW)
    seqs = [acts(t) for t in drawn]
    mask = np.array([q not in variants and not any(violations(q, inv).values())
                     and not (extra_violations(q, R)["impl"] or extra_violations(q, R)["balance"]) for q in seqs])
    return drawn, seqs, mask, int(dup), int(sum(q in variants for q in seqs))


def v27_traces(train):
    seed()
    shadow, flags, info = V27.generate_shadow_log(train, **KW)
    return [acts(t) for t in shadow], info


def v27_score(train, net, im, fm):
    seed()
    return V27.calculate_gen_shadow_stable(train, net, im, fm, **GEN_KW)


def real(key, max_reps):
    stored = json.load(open(os.path.join(FILTER_DIR, f"filter_{key}_ext.json"), encoding="utf-8"))
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(key)))
    reps = sorted({r["rep"] for r in stored["rows"]})[:max_reps]
    out = []
    for rep in reps:
        rng = random.Random(1000 * rep + 0)
        traces, _ = randomize(log, 0.0, rng)
        train, _ = split(traces, rng)
        drawn, seqs, mask, dup, seen = reference(train)
        got, info = v27_traces(train)
        want = [q for q, k in zip(seqs, mask) if k]
        rec = {"key": key, "rep": rep, "drawn": len(seqs), "seen": seen, "v26_duplicates": dup,
               "scored_reference": len(want), "scored_v27": len(got), "traces_identical": got == want,
               "info": info, "models": []}
        print(f"[{key}] rep {rep}: scored {len(got)} (reference {len(want)}), identical {got == want}, "
              f"seen dropped {info['seen_dropped']}, rule dropped {info['rule_dropped']}", flush=True)
        for row in stored["rows"]:
            if row["rep"] != rep or row["set"] != "miner" or row.get("error"):
                continue
            net, im, fm = MINERS[row["name"]](train)
            r = v27_score(train, net, im, fm)
            m = {"name": row["name"], "v27_s": r["accept_mean"], "stored_s": row["ext_s"],
                 "v27_g": r["mean"], "stored_g": row["ext_g"]}
            m["diff_s"] = abs(m["v27_s"] - m["stored_s"])
            m["diff_g"] = abs(m["v27_g"] - m["stored_g"])
            rec["models"].append(m)
            print(f"    {row['name']:22s} strict {m['v27_s']:.6f} stored {m['stored_s']:.6f} | "
                  f"graded {m['v27_g']:.6f} stored {m['stored_g']:.6f}", flush=True)
        out.append(rec)
    return out


def known(n):
    stored = json.load(open(STORED, encoding="utf-8"))["systems"][:n]
    out = []
    for s in stored:
        mode, sd = s["mode"], s["seed"]
        _, S_net, S_im, S_fm = sgt.gen_system(mode, sd)
        L = sgt.playout(S_net, S_im, S_fm, sgt.N_L, sd + 2)
        drawn, seqs, mask, dup, seen = reference(L)
        got, info = v27_traces(L)
        want = [q for q, k in zip(seqs, mask) if k]
        rec = {"mode": mode, "seed": sd, "v26_duplicates": dup, "seen": seen, "scored_reference": len(want),
               "scored_v27": len(got), "traces_identical": got == want, "info": info, "models": []}
        for name, fn in sgt.MINERS.items():
            net, im, fm = fn(L)
            g, st = replay(drawn, net, im, fm)
            ref_s = float(st[mask].mean()) if mask.any() else None
            ref_g = float(g[mask].mean()) if mask.any() else None
            r = v27_score(L, net, im, fm)
            same = (r["accept_mean"] is None and ref_s is None) or (
                ref_s is not None and r["accept_mean"] is not None
                and abs(r["accept_mean"] - ref_s) < 1e-12 and abs(r["mean"] - ref_g) < 1e-9)
            rec["models"].append({"name": name, "v27_s": r["accept_mean"], "ref_s": ref_s, "v27_g": r["mean"],
                                  "ref_g": ref_g, "equal": bool(same)})
        out.append(rec)
        print(f"[known] {mode}/{sd}: seen {seen} scored {len(got)} (reference {len(want)}), identical {got == want}, "
              f"models equal {sum(m['equal'] for m in rec['models'])} of {len(rec['models'])}", flush=True)
    return out


def summarize(res):
    L = ["# v27 against the tested variant (extended rules, seen traces dropped)", "",
         f"pm4py {res['pm4py']}; seed {SEED}; 1,000 drawn traces; N=6, tau=5, mle; {res['seconds']:.0f} s.", "",
         "## A. Real logs", "",
         "| log | rep | drawn | seen dropped | rule dropped | scored | same traces as the tested mask | models | "
         "largest strict difference to stored | largest graded difference to stored |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["real"]:
        ds = max(r["models"], key=lambda m: m["diff_s"])
        dg = max(r["models"], key=lambda m: m["diff_g"])
        L.append(f"| {r['key']} | {r['rep']} | {r['drawn']} | {r['info']['seen_dropped']} | {r['info']['rule_dropped']} | "
                 f"{r['scored_v27']} | {'yes' if r['traces_identical'] else 'NO'} | {len(r['models'])} | "
                 f"{ds['diff_s']:.2e} ({ds['name']}) | {dg['diff_g']:.2e} ({dg['name']}) |")
    K = res["known"]
    L += ["", "## B. Known systems", "",
          f"Systems: {len(K)}. Same traces as the tested mask: {sum(k['traces_identical'] for k in K)} of {len(K)}. "
          f"Models with the same score: {sum(m['equal'] for k in K for m in k['models'])} of "
          f"{sum(len(k['models']) for k in K)}. Systems with seen traces dropped: {sum(k['info']['seen_dropped'] > 0 for k in K)}. "
          f"Systems with an empty scored set (score None): {sum(k['scored_v27'] == 0 for k in K)}. "
          f"v27 seen-dropped count equals the v26 duplicates count on "
          f"{sum(k['info']['seen_dropped'] == k['v26_duplicates'] for k in K)} of {len(K)}."]
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT_DIR, "summary.md"), "w", encoding="utf-8") as fp:
        fp.write(text)
    print(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*", default=["D1", "D2"])
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--systems", type=int, default=12)
    a = ap.parse_args()
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    res = {"pm4py": pm4py.__version__, "known": known(a.systems), "real": []}
    for k in a.keys:
        res["real"] += real(k, a.reps)
    res["seconds"] = time.time() - t0
    with open(os.path.join(OUT_DIR, "check.json"), "w", encoding="utf-8") as fp:
        json.dump(res, fp, indent=1)
    summarize(res)
