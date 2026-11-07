"""Data for the visual comparison of the ShadowGen filter variants.

Reads the stored results of shadow_filter_test.py (--tag ext) and synth_filter_check.py (--tag ext),
and draws one example shadow trace per filter outcome from L1 (same split and seed as the tests).
Writes results/shadow_filter/comparison/data.json. Read-only on every other file.
Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/filter_comparison_data.py
"""
import os
import sys
import json
import random
from collections import Counter

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["TQDM_DISABLE"] = "1"
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, _HERE)

import numpy as np  # noqa: E402
import pm4py  # noqa: E402

from datasets import get_log_path  # noqa: E402
from randomization_test import randomize, split, acts, SEED, GEN_KW  # noqa: E402
from shadow_validity_check import invariants, violations  # noqa: E402
from synth_survivor_check import extra_rules  # noqa: E402
from topk_overfit_test import variants_by_frequency  # noqa: E402
from HybridGen.algorithm.v26 import generate_shadow_log  # noqa: E402

RES = os.path.join(_HERE, "results", "shadow_filter")
OUT = os.path.join(RES, "comparison")
LOGS = {"L1": "D1", "L2": "D2", "L3": "D3", "L5": "D5"}
REAL = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
PRED = ["sg", "all", "ext", "fit"]


def r3(v):
    return None if v is None else round(float(v), 4)


def real_logs():
    points, mae, kept, cost, reps = [], {}, {}, {}, {}
    for lid, key in LOGS.items():
        d = json.load(open(os.path.join(RES, f"filter_{key}_ext.json"), encoding="utf-8"))
        rows = [r for r in d["rows"] if not r.get("error") and r["name"] != "Trace_Filtered"]
        reps[lid] = len(d["info"])
        names = []
        for r in rows:
            if (r["set"], r["name"]) not in names:
                names.append((r["set"], r["name"]))
        for st, nm in names:
            ms = [r for r in rows if r["set"] == st and r["name"] == nm]
            p = {"data": lid, "group": "pole" if nm == "Flower" else st, "model": nm}
            for suf in ("s", "g"):
                for k in ["truth"] + PRED:
                    p[f"{k}_{suf}"] = r3(np.mean([r[f"{k}_{suf}"] for r in ms]))
            points.append(p)
        for grp, sel in (("six miners", lambda r: r["set"] == "miner" and r["name"] in REAL),
                         ("ladder", lambda r: r["set"] == "ladder")):
            for suf in ("s", "g"):
                for k in PRED:
                    per = []
                    for rep in sorted({r["rep"] for r in rows}):
                        ms = [r for r in rows if r["rep"] == rep and sel(r)]
                        if ms:
                            per.append(np.mean([abs(r[f"{k}_{suf}"] - r[f"truth_{suf}"]) for r in ms]))
                    if per:
                        mae[f"{lid}|{grp}|{suf}|{k}"] = r3(np.median(per))
        kept[lid] = {k: r3(np.mean([i[f"kept_{k}"] for i in d["info"]])) for k in ("all", "ext")}
        cost[lid] = {k: {"mean": r3(np.mean([i[f"real_removed_{k}"] for i in d["info"]])),
                         "min": r3(min(i[f"real_removed_{k}"] for i in d["info"])),
                         "max": r3(max(i[f"real_removed_{k}"] for i in d["info"]))} for k in ("all", "ext")}
    return points, mae, kept, cost, reps


def known():
    S = json.load(open(os.path.join(RES, "synth_filter_ext.json"), encoding="utf-8"))["systems"]
    points, mae = [], {}
    for s in S:
        for nm in REAL:
            r = s["models"][nm]
            if r["error"] or r.get("truth_s") is None or r.get("ext_s") is None:
                continue
            p = {"data": "Known", "group": "miner", "model": f"{nm}, system {s['mode']}/{s['seed']}"}
            for suf in ("s", "g"):
                for k in ["truth"] + PRED:
                    p[f"{k}_{suf}"] = r3(r[f"{k}_{suf}"])
            points.append(p)
    for suf in ("s", "g"):
        for k in PRED:
            mae[f"Known|six miners|{suf}|{k}"] = r3(np.mean([abs(p[f"{k}_{suf}"] - p[f"truth_{suf}"]) for p in points]))
    n = 1000.0 * len(S)
    kept = {k: r3(sum(1000 * s[f"kept_{k}"] for s in S) / n) for k in ("all", "ext")}
    valid = {"sg": r3(sum(1000 * s["valid"] for s in S) / n)}
    for k in ("all", "ext"):
        valid[k] = r3(sum(1000 * s[f"kept_{k}"] * (s[f"valid_kept_{k}"] or 0.0) for s in S)
                      / sum(1000 * s[f"kept_{k}"] for s in S))
    cost = {k: {"mean": r3(np.mean([s[f"F_unseen_removed_{k}"] for s in S if s[f"F_unseen_removed_{k}"] is not None])),
                "median": r3(np.median([s[f"F_unseen_removed_{k}"] for s in S if s[f"F_unseen_removed_{k}"] is not None]))}
            for k in ("all", "ext")}
    return points, mae, kept, valid, cost, len(S)


def examples():
    """One short L1 shadow trace per outcome: kept by all, removed by a named rule."""
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path("D1")))
    rng = random.Random(0)
    traces, _ = randomize(log, 0.0, rng)
    train, _ = split(traces, rng)
    order, _ = variants_by_frequency(train)
    inv, R = invariants([acts(t) for t in train]), extra_rules(order)
    random.seed(SEED)
    np.random.seed(SEED)
    shadow, flags, *_ = generate_shadow_log(train, **{k: v for k, v in GEN_KW.items() if k != "iterations"})
    found = {}
    for t in sorted(shadow, key=len):
        s = acts(t)
        if len(s) < 5:
            continue
        v, c = violations(s, inv), Counter(s)
        if any(v.values()):
            over = [a for a, n in c.items() if n > inv["maxc"].get(a, 0)]
            miss = sorted(a for a in inv["always"] if a not in c)
            if over and not miss and "count" not in found:
                found["count"] = {"trace": s, "removed_by": "6 rules", "rule": "count",
                                  "why": f"{over[0]} occurs {c[over[0]]} times. In the training log it occurs at most "
                                         f"{inv['maxc'][over[0]]} time per case."}
            if miss and not over and "mandatory" not in found:
                found["mandatory"] = {"trace": s, "removed_by": "6 rules", "rule": "mandatory",
                                      "why": f"{miss[0]} is missing. Every case of the training log contains it."}
            continue
        im = [(a, b) for a, b in R["impl"] if a in c and b not in c]
        if im:
            if "impl" not in found:
                a, b = sorted(im)[0]
                found["impl"] = {"trace": s, "removed_by": "extended rules", "rule": "a implies b",
                                 "why": f"{a} occurs without {b}. Every training case with {a} also contains {b}."}
            continue
        bal = [(a, b, lo, hi, c.get(a, 0) - c.get(b, 0)) for (a, b), (lo, hi) in R["balance"].items()
               if not lo <= c.get(a, 0) - c.get(b, 0) <= hi]
        if bal:
            if "balance" not in found:
                a, b, lo, hi, d = sorted(bal, key=lambda x: -abs(x[4]))[0]
                found["balance"] = {"trace": s, "removed_by": "extended rules", "rule": "balance",
                                    "why": f"{a} occurs {c.get(a, 0)} times and {b} {c.get(b, 0)} times, a difference of "
                                           f"{d}. In the training log the difference stays between {lo} and {hi}."}
            continue
        if "kept" not in found and len(s) >= 8:
            found["kept"] = {"trace": s, "removed_by": "none", "rule": "none", "why": "Keeps every rule of the training log."}
    return [found[k] for k in ("kept", "count", "mandatory", "impl", "balance") if k in found]


def main():
    pts, mae, kept, cost, reps = real_logs()
    kp, kmae, kkept, kvalid, kcost, nsys = known()
    mae.update(kmae)
    kept["Known"] = kkept
    cost["Known"] = kcost
    out = {"points": pts + kp, "mae": mae, "kept": kept, "cost": cost, "valid_known": kvalid,
           "reps": reps, "n_systems": nsys, "examples": examples()}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "data.json"), "w", encoding="utf-8") as fp:
        json.dump(out, fp)
    print("points", len(out["points"]), "| examples", [e["rule"] for e in out["examples"]])
    for k in sorted(mae):
        if "|s|" in k:
            print(f"  {k:34s} {mae[k]}")
    print("kept", kept)
    print("cost", cost)
    print("valid_known", kvalid)
    for e in out["examples"]:
        print(" ", e["rule"], "|", " > ".join(e["trace"]), "|", e["why"])


if __name__ == "__main__":
    main()
