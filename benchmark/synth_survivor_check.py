"""Which invalid shadow traces pass the rule filter on the synthetic known systems, and why?

synth_filter_check.py shows that the six log rules (end, count, mandatory, ef, df, length) remove
about half of the invalid shadow traces on the known systems. This script looks at the rest: the
survivors, shadow traces that keep all six rules of the training log L and are rejected by the system S.

Four further rule kinds are derived from L (the information a filter may use):
  excl     two activities that never occur in the same case
  impl     a implies b: every case with a also contains b
  balance  count(a) - count(b) stays inside the range seen in L (loop bodies, parallel branches)
  tri      every three consecutive activities occur consecutively in some case
and one diagnostic comes from the replay on S:
  incomplete  no activity of the trace fires while disabled in S; the trace only fails to reach the end
              (an obligatory part is missing)

Reported: the share of the survivors each kind catches; the price of each kind (share of the valid
shadow traces and of the fresh unseen system traces it would remove); and the filter quality of the
six rules extended by these kinds.

pm4py's play-out is not reproducible across processes, so the logs are a resample of the stored study.
Output: results/shadow_filter/synth_survivors.json and summary_synth_survivors.md.
Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/synth_survivor_check.py [--limit N]
"""
import os
import sys
import json
import time
import random
import argparse
from collections import Counter

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["TQDM_DISABLE"] = "1"
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, _HERE)

import numpy as np  # noqa: E402
import pm4py  # noqa: E402
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay  # noqa: E402

import synth_ground_truth as sgt  # noqa: E402
from shadow_validity_check import invariants, violations  # noqa: E402
from HybridGen.algorithm.v26 import generate_shadow_log  # noqa: E402

SEED = 42
GEN_KW = dict(num_traces=1000, safe_threshold=5, max_n=6, successor_weighting="mle")
STORED = os.path.join(_HERE, "results", "synth_ground_truth.json")
OUT_DIR = os.path.join(_HERE, "results", "shadow_filter")
NEW = ["excl", "impl", "balance", "tri"]
COMBOS = [("six rules", []), ("+ excl", ["excl"]), ("+ impl", ["impl"]), ("+ balance", ["balance"]),
          ("+ tri", ["tri"]), ("+ excl, impl", ["excl", "impl"]),
          ("+ excl, impl, balance", ["excl", "impl", "balance"]), ("+ all four", NEW)]


def seq(t):
    return tuple(e["concept:name"] for e in t)


def extra_rules(seqs):
    alph = sorted({a for s in seqs for a in s})
    cooc, impl_bad, bal, tri = set(), set(), {}, set()
    for s in seqs:
        c = Counter(s)
        for a in c:
            for b in alph:
                if b in c:
                    if a < b:
                        cooc.add((a, b))
                else:
                    impl_bad.add((a, b))
        for i, a in enumerate(alph):
            for b in alph[i + 1:]:
                d = c.get(a, 0) - c.get(b, 0)
                lo, hi = bal.get((a, b), (d, d))
                bal[(a, b)] = (min(lo, d), max(hi, d))
        tri.update(zip(s, s[1:], s[2:]))
    excl = {(a, b) for i, a in enumerate(alph) for b in alph[i + 1:] if (a, b) not in cooc}
    impl = {(a, b) for a in alph for b in alph if a != b and (a, b) not in impl_bad}
    return {"excl": excl, "impl": impl, "balance": bal, "tri": tri}


def extra_violations(s, R):
    c = Counter(s)
    return {"excl": any(a in c and b in c for a, b in R["excl"]),
            "impl": any(a in c and b not in c for a, b in R["impl"]),
            "balance": any(not lo <= c.get(a, 0) - c.get(b, 0) <= hi for (a, b), (lo, hi) in R["balance"].items()),
            "tri": any(g not in R["tri"] for g in zip(s, s[1:], s[2:]))}


def run(limit):
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
        inv, R = invariants(list(vL)), extra_rules(list(vL))
        fresh = [seq(t) for t in F if seq(t) not in vL]

        random.seed(SEED)
        np.random.seed(SEED)
        shadow, flags, *_ = generate_shadow_log(L, **GEN_KW)
        res = token_replay.apply(shadow, S_net, S_im, S_fm)
        traces = []
        for t, mut, r in zip(shadow, flags, res):
            q = seq(t)
            traces.append({"valid": bool(r.get("trace_is_fit", r["trace_fitness"] >= 1.0)), "mut": bool(mut),
                           "pass6": not any(violations(q, inv).values()),
                           "incomplete": len(r["transitions_with_problems"]) == 0,
                           "x": extra_violations(q, R), "s": q})
        fr = [{"pass6": not any(violations(q, inv).values()), "x": extra_violations(q, R)} for q in fresh]
        surv = [t for t in traces if t["pass6"] and not t["valid"]]
        rec = {"mode": mode, "seed": seed, "tree": str(tree)[:400], "var_L": len(vL), "n_fresh": len(fr),
               "n_valid": sum(t["valid"] for t in traces), "n_pass6": sum(t["pass6"] for t in traces),
               "n_survivors": len(surv),
               "shadow": [{k: t[k] for k in ("valid", "mut", "pass6", "incomplete", "x")} for t in traces],
               "fresh": fr,
               "examples": [" > ".join(t["s"]) for t in surv if not any(t["x"].values())][:3]}
        out.append(rec)
        print(f"[{idx + 1}/{len(stored)}] mode={mode} seed={seed} invalid {1000 - rec['n_valid']} survivors "
              f"{len(surv)} uncaught by the four kinds {sum(not any(t['x'].values()) for t in surv)} "
              f"[{time.time() - t0:.0f}s]", flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    res = {"protocol": "seed 42; 1,000 shadow traces; N=6, tau=5, mle; v2.6 generator; rules from the 300-trace "
                       "training log; pm4py " + pm4py.__version__,
           "n_systems": len(out), "runtime_s": time.time() - t0, "systems": out}
    json.dump(res, open(os.path.join(OUT_DIR, "synth_survivors.json"), "w", encoding="utf-8"))
    return res


def sh(xs):
    return f"{np.mean(xs):.3f}" if len(xs) else "-"


def summarize(res):
    S = res["systems"]
    shadow = [t for s in S for t in s["shadow"]]
    fresh = [t for s in S for t in s["fresh"]]
    inval = [t for t in shadow if not t["valid"]]
    surv = [t for t in inval if t["pass6"]]
    good = [t for t in shadow if t["valid"] and t["pass6"]]
    fresh6 = [t for t in fresh if t["pass6"]]
    L = [f"# Invalid shadow traces that pass the six rules ({res['n_systems']} known systems; {res['protocol']})", "",
         f"Shadow traces {len(shadow)}; invalid {len(inval)} ({len(inval) / len(shadow):.3f}); removed by the six rules "
         f"{len(inval) - len(surv)}; survivors {len(surv)} ({len(surv) / max(len(inval), 1):.3f} of the invalid), in "
         f"{sum(s['n_survivors'] > 0 for s in S)} systems. Survivors that are mutated traces: {sh([t['mut'] for t in surv])} "
         f"(all shadow traces: {sh([t['mut'] for t in shadow])}).", "",
         "## A. What the survivors break, and what each rule kind costs", "",
         "| rule kind | survivors caught | valid shadow traces (passing the six rules) removed | fresh unseen system traces "
         "(passing the six rules) removed |", "|---|---|---|---|"]
    for k in NEW:
        L.append(f"| {k} | {sh([t['x'][k] for t in surv])} | {sh([t['x'][k] for t in good])} | {sh([t['x'][k] for t in fresh6])} |")
    L.append(f"| any of the four | {sh([any(t['x'].values()) for t in surv])} | {sh([any(t['x'].values()) for t in good])} | "
             f"{sh([any(t['x'].values()) for t in fresh6])} |")
    L.append(f"| any of excl, impl, balance | {sh([any(t['x'][k] for k in NEW[:3]) for t in surv])} | "
             f"{sh([any(t['x'][k] for k in NEW[:3]) for t in good])} | {sh([any(t['x'][k] for k in NEW[:3]) for t in fresh6])} |")
    L += ["", f"Survivors that are only incomplete (no activity fires while disabled in the system, an obligatory part is missing):{sh([t['incomplete'] for t in surv])}; "
              f"among the survivors caught by none of the four kinds: "
              f"{sh([t['incomplete'] for t in surv if not any(t['x'].values())])} "
              f"(n = {sum(not any(t['x'].values()) for t in surv)}).", "",
          "## B. The six rules extended (pooled over all shadow traces; systems = per-system counts)", "",
          "| filter | kept | valid share after | invalid removed | valid removed | fresh unseen removed, pooled | "
          "fresh unseen removed, median system | systems with valid share >= 0.9 | systems with no trace kept |",
          "|---|---|---|---|---|---|---|---|---|"]
    L.append(f"| none | 1.000 | {sh([t['valid'] for t in shadow])} | 0.000 | 0.000 | 0.000 | 0.000 | "
             f"{sum(s['n_valid'] >= 900 for s in S)} | 0 |")
    for name, ks in COMBOS:
        keep = lambda t: t["pass6"] and not any(t["x"][k] for k in ks)  # noqa: E731
        kept = [t for t in shadow if keep(t)]
        per_fresh, ok, empty = [], 0, 0
        for s in S:
            kk = [t for t in s["shadow"] if keep(t)]
            if not kk:
                empty += 1
            elif np.mean([t["valid"] for t in kk]) >= 0.9:
                ok += 1
            if s["fresh"]:
                per_fresh.append(np.mean([not keep(t) for t in s["fresh"]]))
        L.append(f"| {name} | {len(kept) / len(shadow):.3f} | {sh([t['valid'] for t in kept])} | "
                 f"{sh([not keep(t) for t in inval])} | {sh([not keep(t) for t in shadow if t['valid']])} | "
                 f"{sh([not keep(t) for t in fresh])} | {np.median(per_fresh):.3f} | {ok} | {empty} |")
    ex = [(s, e) for s in S for e in s["examples"]]
    if ex:
        L += ["", "## C. Survivors caught by none of the four kinds (first examples)", ""]
        seen = 0
        for s in S:
            if s["examples"] and seen < 6:
                seen += 1
                L.append(f"- system mode {s['mode']} seed {s['seed']}: `{s['tree']}`")
                for e in s["examples"][:2]:
                    L.append(f"  - {e}")
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT_DIR, "summary_synth_survivors.md"), "w", encoding="utf-8") as fp:
        fp.write(text)
    print(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--summary-only", action="store_true")
    a = ap.parse_args()
    summarize(json.load(open(os.path.join(OUT_DIR, "synth_survivors.json"), encoding="utf-8")) if a.summary_only
              else run(a.limit))
