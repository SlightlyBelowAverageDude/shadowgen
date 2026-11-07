"""Screen the five temporal splits for a process change at the cut, the L5 mechanism (temporal_l5_variants.py).

Part A (no models), temporal split and a random 70/30 split of the same sizes (seed 0) as calibration:
  activity case share in training and future, the largest shifts, activities whose share rises by more than 0.2
  (the rule that selects Create Purchase Requisition Item on L5), labels absent from training, and the share of
  future cases with a directly-follows pair (start and end included) absent from training.
  For each flagged activity: its case share per start month.
Part B (Alpha and Alpha+, the nets with temporal deviations above 0.05):
  temporal split: replay fitness of the training split itself, of the whole and the unseen future, and of the future
  with and without a flagged activity; ShadowGen and the reference are read from temporal_unseen_<key>.json.
  random split (seed 0): ShadowGen (same protocol, seed 42), training fitness, and fitness of the unseen test cases.

Output: results/temporal_unseen/drift_screen_<key>.json and summary_drift_screen.md (new files, nothing overwritten).
Run from the repo root:  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/temporal_drift_screen.py D1 D2 D3 D5 D4
"""
import os
import sys
import json
import time
import random
from collections import Counter, defaultdict

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["TQDM_DISABLE"] = "1"
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, _HERE)

import pm4py  # noqa: E402
from pm4py.objects.log.obj import EventLog  # noqa: E402
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay  # noqa: E402

from miners import MINERS  # noqa: E402
from datasets import DATASETS, get_log_path  # noqa: E402
from temporal_holdout import temporal_split, variants, case_start, TRAIN_FRAC  # noqa: E402
from temporal_unseen import score_both  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "temporal_unseen")
LKEY = {"D1": "L1", "D2": "L2", "D3": "L3", "D4": "L4", "D5": "L5"}
NETS = ["Alpha", "Alpha+"]
RISE = 0.2


def f3(x):
    return "--" if x is None else f"{x:.3f}"


def act(t):
    return tuple(e["concept:name"] for e in t)


def random_split(log, seed=0):
    idx = list(range(len(log)))
    random.Random(seed).shuffle(idx)
    cut = int(len(log) * TRAIN_FRAC)
    return EventLog([log[i] for i in idx[:cut]]), EventLog([log[i] for i in idx[cut:]])


def case_share(vc):
    n = sum(vc.values())
    cnt = Counter()
    for v, c in vc.items():
        for a in set(v):
            cnt[a] += c
    return {a: c / n for a, c in cnt.items()}


def df_pairs(v):
    s = ("<start>",) + v + ("<end>",)
    return set(zip(s, s[1:]))


def model_free(vtr, vte):
    s_tr, s_te = case_share(vtr), case_share(vte)
    unseen = {v: c for v, c in vte.items() if v not in vtr}
    s_un = case_share(unseen) if unseen else {}
    acts = sorted(set(s_tr) | set(s_te), key=lambda a: -abs(s_te.get(a, 0) - s_tr.get(a, 0)))
    df_tr = set()
    for v in vtr:
        df_tr |= df_pairs(v)
    new_df = lambda v: bool(df_pairs(v) - df_tr)  # noqa: E731
    n_te, n_un = sum(vte.values()), sum(unseen.values())
    return {
        "unseen_share": n_un / n_te,
        "top_shifts": [{"activity": a, "train": s_tr.get(a, 0), "future": s_te.get(a, 0), "future_unseen": s_un.get(a, 0),
                        "delta": s_te.get(a, 0) - s_tr.get(a, 0)} for a in acts[:8]],
        "max_abs_delta": abs(s_te.get(acts[0], 0) - s_tr.get(acts[0], 0)) if acts else 0.0,
        "n_abs_delta_above_0.1": sum(1 for a in acts if abs(s_te.get(a, 0) - s_tr.get(a, 0)) > 0.1),
        "rise_above_0.2": [a for a in acts if s_te.get(a, 0) - s_tr.get(a, 0) > RISE],
        "fall_above_0.2": [a for a in acts if s_tr.get(a, 0) - s_te.get(a, 0) > RISE],
        "labels_absent_from_train": {a: s_te[a] for a in s_te if a not in s_tr},
        "future_with_new_df": sum(c for v, c in vte.items() if new_df(v)) / n_te,
        "unseen_with_new_df": sum(c for v, c in unseen.items() if new_df(v)) / n_un if n_un else None,
    }


def replay_variants(keys, reps, net, im, fm):
    res = token_replay.apply(EventLog([reps[k] for k in keys]), net, im, fm)
    return {k: (1.0 if r["trace_is_fit"] else 0.0, float(r["trace_fitness"])) for k, r in zip(keys, res)}


def wmean(per, vc, pred):
    ks = [k for k in vc if pred(k)]
    n = sum(vc[k] for k in ks)
    if not n:
        return {"n": 0, "graded": None, "strict": None}
    return {"n": n, "graded": sum(per[k][1] * vc[k] for k in ks) / n, "strict": sum(per[k][0] * vc[k] for k in ks) / n}


def process(dkey):
    t0 = time.time()
    lk = LKEY[dkey]
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    reps = {}
    for t in log:
        reps.setdefault(act(t), t)
    train, test, tr0, tr1, te0, te1 = temporal_split(log)
    vtr, vte = variants(train), variants(test)
    rtr, rte = random_split(log)
    rvtr, rvte = variants(rtr), variants(rte)
    rec = {"log": lk, "dataset": DATASETS[dkey]["name"], "cut": str(te0), "n_train": len(train), "n_test": len(test),
           "temporal": model_free(vtr, vte), "random": model_free(rvtr, rvte)}
    tm, rm = rec["temporal"], rec["random"]
    print(f"\n=== {lk} {rec['dataset']} cut {te0} [{time.time() - t0:.0f}s]", flush=True)
    for name, m in (("temporal", tm), ("random", rm)):
        print(f"  {name:8s} unseen {m['unseen_share']:.3f}  max|d| {m['max_abs_delta']:.3f}  n|d|>0.1 {m['n_abs_delta_above_0.1']}  "
              f"rise>0.2 {m['rise_above_0.2']}  fall>0.2 {m['fall_above_0.2']}  new labels {len(m['labels_absent_from_train'])}  "
              f"new DF: future {m['future_with_new_df']:.3f} unseen {m['unseen_with_new_df']}", flush=True)
    for r in tm["top_shifts"][:5]:
        print(f"    {r['activity'][:45]:45s} train {r['train']:.3f} future {r['future']:.3f} unseen {r['future_unseen']:.3f}", flush=True)

    flagged = tm["rise_above_0.2"]
    has_flag = lambda v: any(a in flagged for a in v)  # noqa: E731
    if flagged:
        month = defaultdict(lambda: [0, 0])
        for t in log:
            s = case_start(t)
            k = f"{s.year:04d}-{s.month:02d}"
            month[k][0] += 1
            month[k][1] += has_flag(act(t))
        rec["flagged_by_start_month"] = {k: {"n": n, "share": f / n} for k, (n, f) in sorted(month.items()) if n >= 50}
        rec["share_with_flag"] = {"train": sum(c for v, c in vtr.items() if has_flag(v)) / len(train),
                                  "future": sum(c for v, c in vte.items() if has_flag(v)) / len(test)}

    year_of = None
    if "year" in log[0].attributes:
        year_of = lambda t: str(t.attributes.get("year"))  # noqa: E731
        rec["year_counts"] = {"train": dict(Counter(year_of(t) for t in train)), "future": dict(Counter(year_of(t) for t in test))}
        print(f"  year counts {rec['year_counts']}", flush=True)
    stored = json.load(open(os.path.join(OUT_DIR, f"temporal_unseen_{dkey}.json"), encoding="utf-8"))["models"]
    rec["nets"] = {}
    for mn in NETS:
        tn = time.time()
        row = {"temporal": {"shadowgen": stored[mn]["shadowgen"], "unseen_fit_stored": stored[mn]["unseen_fit"],
                            "holdout_fit_stored": stored[mn]["holdout_fit"]}}
        net, im, fm = MINERS[mn](train)
        per = replay_variants(list(set(vtr) | set(vte)), reps, net, im, fm)
        row["temporal"]["train"] = wmean(per, vtr, lambda v: True)
        row["temporal"]["future"] = wmean(per, vte, lambda v: True)
        row["temporal"]["unseen"] = wmean(per, vte, lambda v: v not in vtr)
        if flagged:
            row["temporal"]["future_with_flag"] = wmean(per, vte, has_flag)
            row["temporal"]["future_without_flag"] = wmean(per, vte, lambda v: not has_flag(v))
            row["temporal"]["unseen_without_flag"] = wmean(per, vte, lambda v: v not in vtr and not has_flag(v))
            row["temporal"]["train_with_flag"] = wmean(per, vtr, has_flag)
        if year_of is not None:
            by = {}
            for split, lg in (("train", train), ("future", test)):
                acc = defaultdict(lambda: [0, 0.0])
                for t in lg:
                    c = acc[year_of(t)]
                    c[0] += 1
                    c[1] += per[act(t)][1]
                for y, (n, g) in acc.items():
                    by[f"{split}_{y}"] = {"n": n, "graded": g / n}
            row["temporal"]["by_year"] = by
            txt = ", ".join(f"{k}: {v['graded']:.3f} (n {v['n']})" for k, v in sorted(by.items()))
            print(f"  {mn:7s} by year {txt}", flush=True)
        net2, im2, fm2 = MINERS[mn](rtr)
        sg, sg_strict, _, _ = score_both(rtr, net2, im2, fm2)
        per2 = replay_variants(list(set(rvtr) | set(rvte)), reps, net2, im2, fm2)
        row["random"] = {"shadowgen": sg, "shadowgen_strict": sg_strict, "train": wmean(per2, rvtr, lambda v: True),
                         "unseen": wmean(per2, rvte, lambda v: v not in rvtr),
                         "n_transitions": len(net2.transitions)}
        row["temporal"]["n_transitions"] = len(net.transitions)
        rec["nets"][mn] = row
        t_, r_ = row["temporal"], row["random"]
        print(f"  {mn:7s} temporal: sg {t_['shadowgen']:.3f} train {t_['train']['graded']:.3f} future {t_['future']['graded']:.3f} "
              f"unseen {t_['unseen']['graded']:.3f} (stored {t_['unseen_fit_stored']:.3f})"
              + (f" with flag {f3(t_['future_with_flag']['graded'])} without {f3(t_['future_without_flag']['graded'])} "
                 f"unseen without {f3(t_['unseen_without_flag']['graded'])} train with flag {f3(t_['train_with_flag']['graded'])} "
                 f"(n {t_['train_with_flag']['n']})" if flagged else "")
              + f" | random: sg {r_['shadowgen']:.3f} train {r_['train']['graded']:.3f} unseen {r_['unseen']['graded']:.3f} "
              f"[{time.time() - tn:.0f}s]", flush=True)
    rec["seconds"] = time.time() - t0
    rec["protocol"] = ("temporal split 70/30 by case start; random split seed 0, same sizes; flag rule: case share up by more "
                       f"than {RISE}; replay per variant, weighted by count; ShadowGen v2.6 seed 42 K=1 N=6 tau=5 mle; pm4py "
                       + pm4py.__version__)
    path = os.path.join(OUT_DIR, f"drift_screen_{dkey}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    print(f"  [{lk} done in {rec['seconds']:.0f}s -> {path}]", flush=True)


def summarize():
    recs = []
    for k in ["D1", "D2", "D3", "D4", "D5"]:
        p = os.path.join(OUT_DIR, f"drift_screen_{k}.json")
        if os.path.exists(p):
            recs.append(json.load(open(p, encoding="utf-8")))
    L = ["# Drift screen of the temporal splits", "",
         "Activity case share in training and future; random split (seed 0, same sizes) as calibration.", "",
         "| log | split | unseen share | max abs shift | shifts above 0.1 | rise above 0.2 | fall above 0.2 | labels new in future | future with new DF pair | unseen with new DF pair |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in recs:
        for s in ("temporal", "random"):
            m = r[s]
            L.append(f"| {r['log']} | {s} | {m['unseen_share']:.3f} | {m['max_abs_delta']:.3f} | {m['n_abs_delta_above_0.1']} | "
                     f"{'; '.join(m['rise_above_0.2']) or '--'} | {'; '.join(m['fall_above_0.2']) or '--'} | "
                     f"{len(m['labels_absent_from_train'])} | {m['future_with_new_df']:.3f} | {f3(m['unseen_with_new_df'])} |")
    L += ["", "## Largest temporal shifts", "", "| log | activity | train | future | future unseen |", "|---|---|---|---|---|"]
    for r in recs:
        for x in r["temporal"]["top_shifts"][:5]:
            L.append(f"| {r['log']} | {x['activity']} | {x['train']:.3f} | {x['future']:.3f} | {x['future_unseen']:.3f} |")
    L += ["", "## Alpha and Alpha+: temporal split against random split (graded)", "",
          "| log | net | temporal ShadowGen | temporal train | train with flag | temporal future | temporal unseen | future without flag | unseen without flag | random ShadowGen | random train | random unseen |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in recs:
        for mn, row in r["nets"].items():
            t, q = row["temporal"], row["random"]
            g = lambda k: t.get(k, {}).get("graded")  # noqa: E731
            L.append(f"| {r['log']} | {mn} | {t['shadowgen']:.3f} | {f3(t['train']['graded'])} | {f3(g('train_with_flag'))} | {f3(t['future']['graded'])} | "
                     f"{f3(t['unseen']['graded'])} | {f3(g('future_without_flag'))} | {f3(g('unseen_without_flag'))} | {q['shadowgen']:.3f} | {f3(q['train']['graded'])} | {f3(q['unseen']['graded'])} |")
    for r in recs:
        if "flagged_by_start_month" in r:
            L += ["", f"## {r['log']}: share of cases with {r['temporal']['rise_above_0.2']} by start month (cut {r['cut'][:10]})", "",
                  "| month | n | share |", "|---|---|---|"]
            for k, v in r["flagged_by_start_month"].items():
                L.append(f"| {k} | {v['n']} | {v['share']:.3f} |")
    open(os.path.join(OUT_DIR, "summary_drift_screen.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    keys = [k for k in sys.argv[1:] if k != "--summary"] or ["D1", "D2", "D3", "D5", "D4"]
    if "--summary" not in sys.argv:
        for k in keys:
            try:
                process(k)
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                print(f"[{k}] FAIL: {type(e).__name__}: {e}", flush=True)
    summarize()


if __name__ == "__main__":
    main()
