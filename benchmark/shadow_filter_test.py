"""Variant test: score ShadowGen on rule-conforming shadow traces only.

shadow_validity_check.py shows that a quarter or more of the shadow traces on L1 and L5 break a
rule that holds in every case of the log, and that this explains the low strict score on the
Inductive models. This script tests a filter as a variant, without changing the method:

  unfiltered   the stored ShadowGen value (all 1,000 shadow traces)
  filter all   shadow traces that keep all six rules of the training split
               (end, count, mandatory, ef, df, length; see shadow_validity_check.py)
  filter cm    shadow traces that keep the count and mandatory rules only
  filter impl  the six rules and the rule "a implies b" (synth_survivor_check.extra_rules)
  filter ext   the six rules, "a implies b" and the balance rule (count(a) - count(b) inside
               the range seen in the training split)
  fitness      training fitness, the baseline

Scoring a filtered subset equals redrawing until enough conforming traces exist (rejection
sampling); only the sample size differs. The rules come from the training split alone.

Models: the eight benchmark miners on the splits of randomization_test.py at p = 0, and the
Trie-k / IM-k ladder of topk_overfit_test.py where a stored run exists. Truth and training
fitness are read from the stored result files (same seeds, same splits); the unfiltered score is
recomputed and compared with the stored one.

Output: results/shadow_filter/filter_<key>[_tag].json and summary_<key>[_tag].md. Nothing else is
written. The first runs (no tag) hold the unfiltered, all and cm columns only; the run with
--tag ext adds impl and ext.
Run from the repo root:
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/shadow_filter_test.py D1 D2 --tag ext
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
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay  # noqa: E402

from miners import MINERS  # noqa: E402
from datasets import DATASETS, get_log_path  # noqa: E402
from randomization_test import randomize, split, acts, SEED, GEN_KW  # noqa: E402
from shadow_validity_check import invariants, violations  # noqa: E402
from topk_overfit_test import variants_by_frequency, build  # noqa: E402
from synth_survivor_check import extra_rules, extra_violations  # noqa: E402
from HybridGen.algorithm.v26 import generate_shadow_log  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "shadow_filter")
REAL = ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]
PREDS = [("unfiltered", "sg"), ("filter all", "all"), ("filter cm", "cm"), ("filter impl", "impl"),
         ("filter ext", "ext"), ("fitness", "fit")]
MASKS = ["all", "cm", "impl", "ext"]


def stored_cells(key):
    for fn in (f"randomization_{key}.json", f"randomization_{key}.partial.json"):
        p = os.path.join(_HERE, "results", "randomization", fn)
        if os.path.exists(p):
            cells = json.load(open(p, encoding="utf-8"))["cells"]
            return {int(k.split("|")[1]): c for k, c in cells.items() if abs(float(k.split("|")[0])) < 1e-9}
    return {}


def stored_ladder(key):
    p = os.path.join(_HERE, "results", "topk_overfit", f"topk_{key}.json")
    if not os.path.exists(p):
        return {}
    out = {}
    for m in json.load(open(p, encoding="utf-8"))["models"].values():
        if not m.get("error") and m["family"] in ("Trie", "IM"):
            out.setdefault(m["rep"], []).append(m)
    return out


def score(shadow, masks, net, im, fm):
    res = token_replay.apply(shadow, net, im, fm)
    g = np.array([float(r["trace_fitness"]) for r in res])
    s = np.array([1.0 if r.get("trace_is_fit", r["trace_fitness"] >= 1.0) else 0.0 for r in res])
    out = {"sg_g": float(g.mean()), "sg_s": float(s.mean())}
    for name, m in masks.items():
        out[f"{name}_g"] = float(g[m].mean()) if m.any() else None
        out[f"{name}_s"] = float(s[m].mean()) if m.any() else None
    return out


def run_rep(log, rep, cell, ladder, save):
    rng = random.Random(1000 * rep + 0)
    traces, _ = randomize(log, 0.0, rng)
    train, test = split(traces, rng)
    order, _ = variants_by_frequency(train)
    vtr = set(order)
    inv = invariants([acts(t) for t in train])
    unseen = [acts(t) for t in test if acts(t) not in vtr]

    random.seed(SEED)
    np.random.seed(SEED)
    shadow, flags, *_ = generate_shadow_log(train, **{k: v for k, v in GEN_KW.items() if k != "iterations"})
    vio = [violations(acts(t), inv) for t in shadow]
    R = extra_rules(order)
    xv = [extra_violations(acts(t), R) for t in shadow]
    six = np.array([not any(v.values()) for v in vio])
    masks = {"all": six,
             "cm": np.array([not (v["count"] or v["mandatory"]) for v in vio]),
             "impl": six & np.array([not x["impl"] for x in xv]),
             "ext": six & np.array([not (x["impl"] or x["balance"]) for x in xv])}
    uv = [violations(s, inv) for s in unseen]
    ux = [extra_violations(s, R) for s in unseen]
    removed = {"all": [any(v.values()) for v in uv],
               "cm": [v["count"] or v["mandatory"] for v in uv],
               "impl": [any(v.values()) or x["impl"] for v, x in zip(uv, ux)],
               "ext": [any(v.values()) or x["impl"] or x["balance"] for v, x in zip(uv, ux)]}
    info = {"rep": rep, "n_unseen": len(unseen), "mutated_share": float(np.mean(flags))}
    for k in MASKS:
        info[f"kept_{k}"] = float(masks[k].mean())
        info[f"real_removed_{k}"] = float(np.mean(removed[k])) if uv else None
    print(f"  rep={rep} kept " + " ".join(f"{k} {info[f'kept_{k}']:.3f}" for k in MASKS) + "; real unseen removed "
          + " ".join(f"{k} {fmt(info[f'real_removed_{k}'])}" for k in MASKS), flush=True)
    rows = []
    jobs = [("miner", mn, None, None) for mn in MINERS]
    jobs += [("ladder", f"{m['family']}-{'all' if m['all'] else m['k']}", m["family"], m["k"]) for m in ladder]
    for kind, name, fam, k in jobs:
        st = cell["models"].get(name, {}) if kind == "miner" else \
            next(m for m in ladder if m["family"] == fam and m["k"] == k)
        row = {"rep": rep, "set": kind, "name": name, "error": st.get("error") if kind == "miner" else None}
        t0 = time.time()
        if not row["error"]:
            try:
                net, im, fm = MINERS[name](train) if kind == "miner" else build(fam, train, order, k)
                row.update(score(shadow, masks, net, im, fm))
                row.update({"truth_g": st.get("unseen_fit"), "truth_s": st.get("unseen_fit_strict"),
                            "fit_g": st.get("train_fit"), "fit_s": st.get("train_fit_strict"),
                            "stored_g": st.get("shadowgen"), "stored_s": st.get("shadowgen_strict")})
            except Exception as e:  # noqa: BLE001
                row["error"] = f"{type(e).__name__}: {e}"
        rows.append(row)
        if row["error"]:
            print(f"    {name:22s} FAIL {row['error']}", flush=True)
        else:
            print(f"    {name:22s} strict truth {row['truth_s']:.3f} | unfiltered {row['sg_s']:.3f} "
                  f"(stored {row['stored_s']:.3f}) " + " ".join(f"{k} {fmt(row[f'{k}_s'])}" for k in MASKS)
                  + f" [{time.time() - t0:.0f}s]", flush=True)
        save(info, rows)
    return info, rows


def ranks(x):
    o = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[o] = np.arange(1, len(x) + 1)
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return r


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else float("nan")


def fmt(v):
    return "-" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.3f}"


def summarize(key, out, tag=""):
    rows = [r for r in out["rows"] if not r.get("error")]
    errors = [r for r in out["rows"] if r.get("error")]
    reps = sorted({r["rep"] for r in rows})
    L = [f"# Rule filter on the shadow traces, {key} ({out['dataset']}), {out['n_cases']} cases, "
         f"{len(reps)} repetitions", "",
         "Protocol: benchmark/shadow_filter_test.py. Truth = stored acceptance of future cases with a variant "
         "absent from training. Errors: " + (", ".join(f"{e['name']} rep {e['rep']}" for e in errors) or "none") + ".", "",
         "## A. What the filter removes (all = six rules, cm = count and mandatory, impl = six rules and "
         "a implies b, ext = impl and balance)", ""]
    mk = [k for k in MASKS if any(f"kept_{k}" in i for i in out["info"])]
    L += ["| rep | mutated share | " + " | ".join(f"shadow kept, {k}" for k in mk) + " | "
          + " | ".join(f"real unseen removed, {k}" for k in mk) + " |", "|---|---|" + "---|" * (2 * len(mk))]
    for i in out["info"]:
        L.append(f"| {i['rep']} | {i['mutated_share']:.3f} | " + " | ".join(fmt(i.get(f"kept_{k}")) for k in mk)
                 + " | " + " | ".join(fmt(i.get(f"real_removed_{k}")) for k in mk) + " |")
    L += ["", "## B. Agreement with the truth (median over repetitions)", "",
          "| models | n | reading | predictor | Pearson | Spearman | MAE | mean signed error |",
          "|---|---|---|---|---|---|---|---|"]
    sets = [("six miners", lambda r: r["set"] == "miner" and r["name"] in REAL)]
    if any(r["set"] == "ladder" for r in rows):
        sets += [("ladder (Trie, IM)", lambda r: r["set"] == "ladder"),
                 ("six miners and ladder", lambda r: r["set"] == "ladder" or r["name"] in REAL)]
    for sname, sel in sets:
        for reading, suf in (("strict", "s"), ("graded", "g")):
            for pname, pk in PREDS:
                per = []
                n = 0
                for rep in reps:
                    ms = [r for r in rows if r["rep"] == rep and sel(r)
                          and r.get(f"{pk}_{suf}") is not None and r.get(f"truth_{suf}") is not None]
                    if len(ms) < 3:
                        continue
                    n = len(ms)
                    a = np.array([r[f"{pk}_{suf}"] for r in ms], float)
                    t = np.array([r[f"truth_{suf}"] for r in ms], float)
                    per.append((corr(a, t), corr(ranks(a), ranks(t)), float(np.mean(np.abs(a - t))),
                                float(np.mean(a - t))))
                if not per:
                    continue
                med = np.nanmedian(np.array(per), axis=0)
                L.append(f"| {sname} | {n} | {reading} | {pname} | {fmt(float(med[0]))} | {fmt(float(med[1]))} | "
                         f"{fmt(float(med[2]))} | {med[3]:+.3f} |")
    keys = ["truth", "sg"] + mk + ["fit"]
    L += ["", "## C. Per model (mean over repetitions): " + " / ".join(
          {"truth": "truth", "sg": "unfiltered", "fit": "fitness"}.get(k, "filter " + k) for k in keys), "",
          "| model | strict | graded |", "|---|---|---|"]
    names = []
    for r in rows:
        if (r["set"], r["name"]) not in names:
            names.append((r["set"], r["name"]))
    for st, nm in names:
        ms = [r for r in rows if r["set"] == st and r["name"] == nm]
        cell = lambda suf: " / ".join(  # noqa: E731
            fmt(float(np.mean([r[f"{k}_{suf}"] for r in ms if r.get(f"{k}_{suf}") is not None]))
                if any(r.get(f"{k}_{suf}") is not None for r in ms) else None)
            for k in keys)
        L.append(f"| {nm} | {cell('s')} | {cell('g')} |")
    L += ["", "## D. Unfiltered score against the stored value", ""]
    for st in ("miner", "ladder"):
        d = [(abs(r["sg_s"] - r["stored_s"]), abs(r["sg_g"] - r["stored_g"]), r["name"]) for r in rows
             if r["set"] == st and r.get("stored_s") is not None]
        if d:
            ws, wg = max(d, key=lambda x: x[0]), max(d, key=lambda x: x[1])
            L.append(f"{st}: largest difference strict {ws[0]:.4f} ({ws[2]}), graded {wg[1]:.4f} ({wg[2]}), "
                     f"{len(d)} models.")
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT_DIR, f"summary_{key}" + (f"_{tag}" if tag else "") + ".md"), "w",
              encoding="utf-8") as fp:
        fp.write(text)
    print(text)


def process(key, max_reps, tag=""):
    t0 = time.time()
    cells, ladders = stored_cells(key), stored_ladder(key)
    reps = sorted(cells)[:max_reps]
    if not reps:
        print(f"[{key}] no stored p = 0 cell")
        return
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(key)))
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"filter_{key}" + (f"_{tag}" if tag else "") + ".json")
    out = {"dataset": DATASETS[key]["name"], "n_cases": len(log), "info": [], "rows": []}
    print(f"=== {key} {DATASETS[key]['name']}: {len(log)} cases, reps {reps} [{time.time() - t0:.0f}s load]",
          flush=True)
    for rep in reps:
        base_info, base_rows = list(out["info"]), list(out["rows"])

        def save(info, rows):
            out["info"], out["rows"] = base_info + [info], base_rows + rows
            with open(path, "w", encoding="utf-8") as fp:
                json.dump(out, fp, indent=1)

        run_rep(log, rep, cells[rep], ladders.get(rep, []), save)
        print(f"  rep {rep} done [{time.time() - t0:.0f}s]", flush=True)
    out["seconds"] = time.time() - t0
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(out, fp, indent=1)
    summarize(key, out, tag)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*", default=["D1", "D2"])
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--summary-only", action="store_true")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    for k in a.keys:
        if a.summary_only:
            stem = f"filter_{k}" + (f"_{a.tag}" if a.tag else "")
            summarize(k, json.load(open(os.path.join(OUT_DIR, stem + ".json"), encoding="utf-8")), a.tag)
        else:
            process(k, a.reps, a.tag)
