"""Why is the strict ShadowGen value below the strict truth on the Inductive models?

On L1 and L5 the Inductive Miner nets accept nearly every real future case with an unseen
variant, and reject a large share of the shadow traces. This script compares the two trace
populations on the same split:

  real    future cases whose variant is absent from the training split
  shadow  the 1,000 shadow traces ShadowGen draws from the training split (regular and mutated)

Every trace is checked against log invariants, properties that hold for every case of a
reference log:
  end        the last activity ends some reference case
  count      no activity occurs more often than in any reference case (unknown activity = violation)
  mandatory  every activity present in all reference cases is present
  ef         every ordered pair (a before b) occurs in some reference case
  df         every directly-follows pair occurs in some reference case
  length     the trace is not longer than the longest reference case
Reference "train" = the training split (the same information ShadowGen has; real unseen cases
may violate it). Reference "full" = the whole log (training and future cases; a real case never
violates it, a shadow trace that does breaks a rule without exception in the data).

Protocol identical to randomization_test.py at p = 0 (same seeds, same splits, same shadow
traces), models Inductive_Strict and Inductive_Infrequent from miners.py.

Output: results/shadow_validity/shadow_validity_<key>.json and summary_<key>.md.
Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/shadow_validity_check.py D1 --reps 3
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
from pm4py.objects.log.obj import EventLog  # noqa: E402
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay  # noqa: E402

from miners import MINERS  # noqa: E402
from datasets import DATASETS, get_log_path  # noqa: E402
from randomization_test import randomize, split, acts, SEED, GEN_KW  # noqa: E402
from HybridGen.algorithm.v26 import generate_shadow_log  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "shadow_validity")
MODELS = ["Inductive_Strict", "Inductive_Infrequent"]
KINDS = ["end", "count", "mandatory", "ef", "df", "length"]
GROUPS = ["real", "shadow", "shadow_regular", "shadow_mutated"]


def invariants(seqs):
    inv = {"ends": set(), "maxc": Counter(), "always": None, "ef": set(), "df": set(), "maxlen": 0}
    for s in seqs:
        inv["ends"].add(s[-1] if s else None)      # None = the empty trace (synthetic systems)
        inv["maxlen"] = max(inv["maxlen"], len(s))
        c = Counter(s)
        for a, n in c.items():
            if n > inv["maxc"][a]:
                inv["maxc"][a] = n
        inv["always"] = set(c) if inv["always"] is None else inv["always"] & set(c)
        inv["df"].update(zip(s, s[1:]))
        seen = set()
        for a in s:
            for b in seen:
                inv["ef"].add((b, a))
            seen.add(a)
    return inv


def violations(s, inv):
    c = Counter(s)
    v = {"end": (s[-1] if s else None) not in inv["ends"],
         "count": any(n > inv["maxc"].get(a, 0) for a, n in c.items()),
         "mandatory": not inv["always"] <= set(c),
         "df": any(p not in inv["df"] for p in zip(s, s[1:])),
         "length": len(s) > inv["maxlen"],
         "ef": False}
    seen = set()
    for a in s:
        if any((b, a) not in inv["ef"] for b in seen):
            v["ef"] = True
            break
        seen.add(a)
    return v


def replay(log, net, im, fm):
    out = []
    for r in token_replay.apply(log, net, im, fm):
        out.append({"fit": bool(r["trace_is_fit"]), "missing": int(r["missing_tokens"]),
                    "remaining": int(r["remaining_tokens"]),
                    "problems": sorted({str(t.label) for t in r["transitions_with_problems"]})})
    return out


def run_rep(log, rep, stored):
    rng = random.Random(1000 * rep + 0)
    traces, _ = randomize(log, 0.0, rng)
    train, test = split(traces, rng)
    vtr = set(acts(t) for t in train)
    unseen = EventLog([t for t in test if acts(t) not in vtr])
    inv_train = invariants([acts(t) for t in train])
    inv_full = invariants([acts(t) for t in traces])

    random.seed(SEED)
    np.random.seed(SEED)
    kw = {k: v for k, v in GEN_KW.items() if k != "iterations"}
    shadow, flags, dup, trunc, cap = generate_shadow_log(train, **kw)

    pop = []   # one record per trace: group, sequence, violations
    for t in unseen:
        s = acts(t)
        pop.append({"g": "real", "mut": None, "s": s, "vt": violations(s, inv_train), "vf": None})
    for t, m in zip(shadow, flags):
        s = acts(t)
        pop.append({"g": "shadow", "mut": bool(m), "s": s, "vt": violations(s, inv_train),
                    "vf": violations(s, inv_full), "in_test": s in set()})
    test_variants = set(acts(t) for t in unseen)
    for p in pop:
        if p["g"] == "shadow":
            p["in_test"] = p["s"] in test_variants

    rec = {"rep": rep, "n_train": len(train), "n_unseen": len(unseen), "var_train": len(vtr),
           "duplicates_kept": dup, "truncated": trunc, "cap": cap,
           "mutated_share": sum(flags) / len(flags), "models": {}, "tree": None, "examples": []}
    if rep == 0:
        rec["tree"] = str(pm4py.discover_process_tree_inductive(train, noise_threshold=0.0))
    for mn in MODELS:
        net, im, fm = MINERS[mn](train)
        res = replay(EventLog(list(unseen) + list(shadow)), net, im, fm)
        for p, r in zip(pop, res):
            p[mn] = r
        sg = float(np.mean([p[mn]["fit"] for p in pop if p["g"] == "shadow"]))
        truth = float(np.mean([p[mn]["fit"] for p in pop if p["g"] == "real"])) if len(unseen) else None
        st = (stored or {}).get(mn, {})
        rec["models"][mn] = {"shadowgen_strict": sg, "truth_strict": truth,
                             "stored_shadowgen_strict": st.get("shadowgen_strict"),
                             "stored_truth_strict": st.get("unseen_fit_strict")}
        print(f"    rep={rep} {mn:22s} strict score {sg:.4f} (stored {st.get('shadowgen_strict')}) "
              f"truth {truth} (stored {st.get('unseen_fit_strict')})", flush=True)
    rec["pop"] = [{"g": p["g"], "mut": p["mut"], "len": len(p["s"]), "vt": p["vt"], "vf": p["vf"],
                   "in_test": p.get("in_test"),
                   **{mn: p[mn] for mn in MODELS}} for p in pop]
    if rep == 0:
        rej = [p for p in pop if p["g"] == "shadow" and not p["Inductive_Strict"]["fit"]]
        for p in rej[:12]:
            rec["examples"].append({"trace": list(p["s"]), "mutated": p["mut"],
                                    "train": [k for k in KINDS if p["vt"][k]],
                                    "full": [k for k in KINDS if p["vf"][k]],
                                    "missing": p["Inductive_Strict"]["missing"],
                                    "remaining": p["Inductive_Strict"]["remaining"],
                                    "problems": p["Inductive_Strict"]["problems"]})
    return rec


def in_group(p, g):
    if g == "real":
        return p["g"] == "real"
    if p["g"] != "shadow":
        return False
    return g == "shadow" or (g == "shadow_regular" and not p["mut"]) or (g == "shadow_mutated" and p["mut"])


def share(xs):
    return f"{np.mean(xs):.3f}" if len(xs) else "-"


def summarize(key, out):
    pop = [p for r in out["reps"] for p in r["pop"]]
    L = [f"# Shadow trace validity, {key} ({out['dataset']}), {out['n_cases']} cases, "
         f"{len(out['reps'])} repetitions pooled", "",
         "real = future cases with a variant absent from training; shadow = ShadowGen's 1,000 traces "
         "per repetition (seed 42, N=6, tau=5, mle, v2.6). Invariants: see benchmark/shadow_validity_check.py.", ""]
    r0 = out["reps"]
    L.append("Per repetition: " + "; ".join(
        f"rep {r['rep']}: {r['n_unseen']} real unseen cases, mutated share {r['mutated_share']:.3f}, "
        f"duplicates kept {r['duplicates_kept']}, truncated {r['truncated']}" for r in r0))
    L += ["", "## A. Share of traces that violate an invariant", "",
          "| reference | group | n | any | " + " | ".join(KINDS) + " |", "|---|---|---|---|" + "---|" * len(KINDS)]
    for ref, vk in (("train", "vt"), ("full", "vf")):
        for g in GROUPS:
            if ref == "full" and g == "real":
                continue
            ps = [p for p in pop if in_group(p, g)]
            L.append(f"| {ref} | {g} | {len(ps)} | {share([any(p[vk].values()) for p in ps])} | "
                     + " | ".join(share([p[vk][k] for p in ps]) for k in KINDS) + " |")
    L += ["", "## B. Strict acceptance by group and invariant status", "",
          "| model | group | n | accepted | n clean (train) | accepted, clean | n violating (train) | accepted, violating |",
          "|---|---|---|---|---|---|---|---|"]
    for mn in MODELS:
        for g in GROUPS:
            ps = [p for p in pop if in_group(p, g)]
            cl = [p for p in ps if not any(p["vt"].values())]
            vi = [p for p in ps if any(p["vt"].values())]
            L.append(f"| {mn} | {g} | {len(ps)} | {share([p[mn]['fit'] for p in ps])} | {len(cl)} | "
                     f"{share([p[mn]['fit'] for p in cl])} | {len(vi)} | {share([p[mn]['fit'] for p in vi])} |")
    L += ["", "## C. Shadow traces by full-log invariant status", "",
          "| model | n clean (full) | accepted, clean | n violating (full) | accepted, violating |", "|---|---|---|---|---|"]
    for mn in MODELS:
        ps = [p for p in pop if p["g"] == "shadow"]
        cl = [p for p in ps if not any(p["vf"].values())]
        vi = [p for p in ps if any(p["vf"].values())]
        L.append(f"| {mn} | {len(cl)} | {share([p[mn]['fit'] for p in cl])} | {len(vi)} | "
                 f"{share([p[mn]['fit'] for p in vi])} |")
    L += ["", "## D. Rejected shadow traces", "",
          "| model | rejected | violates train | violates full | by kind (full): " + ", ".join(KINDS)
          + " | incomplete only (no missing token) | mutated |", "|---|---|---|---|---|---|---|"]
    for mn in MODELS:
        rj = [p for p in pop if p["g"] == "shadow" and not p[mn]["fit"]]
        L.append(f"| {mn} | {len(rj)} | {share([any(p['vt'].values()) for p in rj])} | "
                 f"{share([any(p['vf'].values()) for p in rj])} | "
                 + ", ".join(share([p['vf'][k] for p in rj]) for k in KINDS)
                 + f" | {share([p[mn]['missing'] == 0 for p in rj])} | {share([p['mut'] for p in rj])} |")
        c = Counter(lbl for p in rj for lbl in p[mn]["problems"])
        L.append("")
        L.append(f"{mn}, transitions with problems (share of rejected traces): "
                 + ", ".join(f"{a} {n / max(len(rj), 1):.2f}" for a, n in c.most_common(8)))
        L.append("")
    L += ["## E. Shadow traces that are a real unseen future variant", ""]
    ps = [p for p in pop if p["g"] == "shadow"]
    L.append(f"{share([p['in_test'] for p in ps])} of the shadow traces equal a real unseen future variant "
             f"(regular {share([p['in_test'] for p in ps if not p['mut']])}, "
             f"mutated {share([p['in_test'] for p in ps if p['mut']])}).")
    L += ["", "## F. Stored values reproduced", ""]
    for r in out["reps"]:
        for mn in MODELS:
            m = r["models"][mn]
            L.append(f"rep {r['rep']} {mn}: strict score {m['shadowgen_strict']:.4f} (stored "
                     f"{m['stored_shadowgen_strict']}), truth {m['truth_strict']} (stored {m['stored_truth_strict']})")
    ex = out["reps"][0]["examples"]
    if ex:
        L += ["", "## G. First rejected shadow traces, Inductive_Strict, repetition 0", ""]
        for e in ex:
            L.append(f"- {' > '.join(e['trace'])}  [mutated {e['mutated']}; train {e['train']}; full {e['full']}; "
                     f"missing {e['missing']}, remaining {e['remaining']}; problems {e['problems']}]")
    if out["reps"][0].get("tree"):
        L += ["", "## H. Inductive_Strict process tree, repetition 0", "", "```", out["reps"][0]["tree"], "```"]
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT_DIR, f"summary_{key}.md"), "w", encoding="utf-8") as fp:
        fp.write(text)
    print(text)


def process(key, reps):
    t0 = time.time()
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(key)))
    os.makedirs(OUT_DIR, exist_ok=True)
    stored = {}
    for fn in (f"randomization_{key}.json", f"randomization_{key}.partial.json"):
        p = os.path.join(_HERE, "results", "randomization", fn)
        if os.path.exists(p):
            stored = json.load(open(p, encoding="utf-8"))["cells"]
            break
    print(f"=== {key} {DATASETS[key]['name']}: {len(log)} cases [{time.time() - t0:.0f}s load]", flush=True)
    out = {"dataset": DATASETS[key]["name"], "n_cases": len(log), "reps": []}
    for rep in range(reps):
        out["reps"].append(run_rep(log, rep, stored.get(f"0.00|{rep}", {}).get("models")))
        print(f"  rep {rep} done [{time.time() - t0:.0f}s]", flush=True)
    out["seconds"] = time.time() - t0
    with open(os.path.join(OUT_DIR, f"shadow_validity_{key}.json"), "w", encoding="utf-8") as fp:
        json.dump(out, fp)
    summarize(key, out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*", default=["D1"])
    ap.add_argument("--reps", type=int, default=3)
    a = ap.parse_args()
    for k in a.keys:
        process(k, a.reps)
