"""Why does the strict reading fail on the L5 temporal split?

On L5 (BPI2019) the infrequent inductive net discovered on the earliest 70 percent of cases accepts 0.957 of its
shadow log but only 0.168 of the future cases whose variant is unseen in training (temporal_unseen_D5.json).
Three explanations are separated here:

  shadow log too easy   the net also rejects much of its own training split, so real traces are harder than shadow traces
  drift                 the net accepts its training split, and acceptance falls with the time since training
  censoring             late cases are cut off by the end of the extract; their unseen variants are prefixes of
                        complete behavior and fail strict replay because the final marking is not reached

Per model (Inductive_Infrequent, Inductive_Strict) the script records strict acceptance (trace_is_fit) and graded
fitness, per trace, on the training split, the test split (seen and unseen variants), and the regenerated shadow log
(seed 42, K=1, N=6, tau=5, mle; same call sequence as the v2.6 core). It groups them by start-time decile, by last
activity, by whether an unseen variant is a proper prefix of a training variant, and by case end time. A random 70/30
split of the cases (three seeds) is the control without time order.

Output: results/temporal_unseen/l5_check.json and summary_l5_check.md (new files, nothing overwritten).
Run from the repo root:  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/temporal_l5_check.py
"""
import os
import sys
import json
import time
import random
from collections import Counter

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["TQDM_DISABLE"] = "1"
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
sys.path.insert(0, _REPO)
sys.path.insert(0, _HERE)

import numpy as np  # noqa: E402
import pm4py  # noqa: E402
from pm4py.objects.log.obj import EventLog  # noqa: E402
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay  # noqa: E402

from miners import MINERS  # noqa: E402
from datasets import get_log_path  # noqa: E402
from temporal_holdout import temporal_split, variants, case_start  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

try:
    import pm4py.util.constants as _pmc
    _pmc.SHOW_PROGRESS_BAR = False
except Exception:  # noqa: BLE001
    pass

DKEY = "D5"
SEED = 42
GEN_KW = dict(num_traces=1000, safe_threshold=5, max_n=6, successor_weighting="mle")
MODELS = ["Inductive_Infrequent", "Inductive_Strict"]
CONTROL_SEEDS = [0, 1, 2]
OUT_DIR = os.path.join(_HERE, "results", "temporal_unseen")
STORED = os.path.join(OUT_DIR, "temporal_unseen_D5.json")
gen = load_algorithm("v2.6").generate_shadow_log


def act(t):
    return tuple(e["concept:name"] for e in t)


def case_end(t):
    ts = [e["time:timestamp"] for e in t if "time:timestamp" in e]
    return max(ts) if ts else None


def replay(log, net, im, fm):
    """Per trace: (strict, graded), as in the v2.6 core."""
    res = token_replay.apply(log, net, im, fm)
    return [(1.0 if r.get("trace_is_fit", r["trace_fitness"] >= 1.0) else 0.0, float(r["trace_fitness"])) for r in res]


def agg(rows):
    if not rows:
        return {"n": 0, "strict": None, "graded": None}
    return {"n": len(rows), "strict": float(np.mean([r[0] for r in rows])), "graded": float(np.mean([r[1] for r in rows]))}


def shadow(train):
    random.seed(SEED)
    np.random.seed(SEED)
    s, flags, dup, trunc, cap = gen(train, **GEN_KW)
    return s, flags, int(dup), int(trunc), cap


def deciles(keys):
    """Index lists of 10 equal-count groups by key order."""
    order = sorted(range(len(keys)), key=lambda i: keys[i])
    return [order[int(len(order) * k / 10):int(len(order) * (k + 1) / 10)] for k in range(10)]


def length_q(log):
    v = sorted(len(t) for t in log)
    return {q: v[min(len(v) - 1, int(len(v) * q))] for q in (0.1, 0.25, 0.5, 0.75, 0.9)} | {"mean": float(np.mean(v))}


def main():
    t0 = time.time()
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(DKEY)))
    train, test, tr0, tr1, te0, te1 = temporal_split(log)
    vtr = variants(train)
    prefixes = set()
    for v in vtr:
        for k in range(1, len(v)):
            prefixes.add(v[:k])
    log_end = max(case_end(t) for t in log)
    end_tr = Counter(act(t)[-1] for t in train if len(t))
    END = {a for a, c in end_tr.items() if c / len(train) >= 0.01}
    stored = json.load(open(STORED, encoding="utf-8"))["models"]
    print(f"|train|={len(train)} |test|={len(test)} train {tr0}..{tr1} test {te0}..{te1} log end {log_end}; "
          f"end activities >= 1% of training cases: {sorted(END)}", flush=True)

    test_info = []
    for t in test:
        v = act(t)
        test_info.append({"unseen": v not in vtr, "prefix": v in prefixes, "end_ok": bool(v) and v[-1] in END,
                          "start": case_start(t), "end": case_end(t), "len": len(v)})
    tr_start = [case_start(t) for t in train]
    te_start = [x["start"] for x in test_info]
    unseen_idx = [i for i, x in enumerate(test_info) if x["unseen"]]

    rec = {"dataset": "BPI2019", "n_train": len(train), "n_test": len(test), "n_unseen": len(unseen_idx),
           "train_range": [str(tr0), str(tr1)], "test_range": [str(te0), str(te1)], "log_end": str(log_end),
           "end_activities": {a: end_tr[a] / len(train) for a in sorted(END)},
           "lengths": {"train": length_q(train), "test_unseen": length_q(EventLog([test[i] for i in unseen_idx]))},
           "unseen_profile": {
               "prefix_of_training_variant": float(np.mean([test_info[i]["prefix"] for i in unseen_idx])),
               "last_activity_is_training_end": float(np.mean([test_info[i]["end_ok"] for i in unseen_idx])),
               "seen_last_activity_is_training_end": float(np.mean([x["end_ok"] for x in test_info if not x["unseen"]])),
               "train_last_activity_is_training_end": float(np.mean([bool(len(t)) and act(t)[-1] in END for t in train]))},
           "models": {}}

    sh, flags, dup, trunc, cap = shadow(train)
    sh_vars = [act(t) for t in sh]
    rec["shadow"] = {"n": len(sh), "mutated": int(sum(flags)), "duplicates_kept": dup, "truncated": trunc, "cap": cap,
                     "seen_share": float(np.mean([v in vtr for v in sh_vars])),
                     "prefix_of_training_variant": float(np.mean([v in prefixes for v in sh_vars])),
                     "last_activity_is_training_end": float(np.mean([bool(v) and v[-1] in END for v in sh_vars])),
                     "lengths": length_q(sh)}
    print(f"shadow: {rec['shadow']}", flush=True)

    for mn in MODELS:
        tm = time.time()
        net, im, fm = MINERS[mn](train)
        m = {"n_transitions": len(net.transitions)}
        r_sh = replay(sh, net, im, fm)
        r_tr = replay(train, net, im, fm)
        r_te = replay(test, net, im, fm)
        m["shadow"] = agg(r_sh)
        m["shadow_regular"] = agg([r for r, f in zip(r_sh, flags) if not f])
        m["shadow_mutated"] = agg([r for r, f in zip(r_sh, flags) if f])
        m["train"] = agg(r_tr)
        m["test_all"] = agg(r_te)
        m["test_seen"] = agg([r_te[i] for i, x in enumerate(test_info) if not x["unseen"]])
        m["test_unseen"] = agg([r_te[i] for i in unseen_idx])
        m["reproduces_stored"] = {"shadow_strict": [m["shadow"]["strict"], stored[mn]["shadowgen_strict"]],
                                  "shadow_graded": [m["shadow"]["graded"], stored[mn]["shadowgen"]],
                                  "unseen_strict": [m["test_unseen"]["strict"], stored[mn]["unseen_fit_strict"]],
                                  "unseen_graded": [m["test_unseen"]["graded"], stored[mn]["unseen_fit"]]}
        m["train_deciles"] = []
        for g in deciles(tr_start):
            a = agg([r_tr[i] for i in g])
            a["from"] = str(tr_start[g[0]])
            m["train_deciles"].append(a)
        m["test_deciles_all"], m["test_deciles_unseen"] = [], []
        for g in deciles(te_start):
            a = agg([r_te[i] for i in g])
            a["from"] = str(te_start[g[0]])
            m["test_deciles_all"].append(a)
            u = agg([r_te[i] for i in g if test_info[i]["unseen"]])
            u["from"] = str(te_start[g[0]])
            m["test_deciles_unseen"].append(u)
        m["unseen_by_profile"] = {
            "prefix": agg([r_te[i] for i in unseen_idx if test_info[i]["prefix"]]),
            "not_prefix": agg([r_te[i] for i in unseen_idx if not test_info[i]["prefix"]]),
            "end_ok": agg([r_te[i] for i in unseen_idx if test_info[i]["end_ok"]]),
            "end_not_ok": agg([r_te[i] for i in unseen_idx if not test_info[i]["end_ok"]]),
            "end_ok_not_prefix": agg([r_te[i] for i in unseen_idx if test_info[i]["end_ok"] and not test_info[i]["prefix"]])}
        m["train_by_end"] = {"end_ok": agg([r for r, t in zip(r_tr, train) if len(t) and act(t)[-1] in END]),
                             "end_not_ok": agg([r for r, t in zip(r_tr, train) if not (len(t) and act(t)[-1] in END)])}
        m["shadow_by_end"] = {"end_ok": agg([r for r, v in zip(r_sh, sh_vars) if v and v[-1] in END]),
                              "end_not_ok": agg([r for r, v in zip(r_sh, sh_vars) if not (v and v[-1] in END)])}
        m["seconds"] = time.time() - tm
        rec["models"][mn] = m
        print(f"{mn}: ntr {m['n_transitions']} shadow {m['shadow']} train {m['train']} test_seen {m['test_seen']} "
              f"test_unseen {m['test_unseen']} [{m['seconds']:.0f}s]", flush=True)

    # control without time order: random 70/30 case split
    rec["random_split"] = []
    cases = list(log)
    for cs in CONTROL_SEEDS:
        perm = np.random.RandomState(cs).permutation(len(cases))
        cut = int(len(cases) * 0.70)
        rtrain = EventLog([cases[i] for i in perm[:cut]])
        rtest = EventLog([cases[i] for i in perm[cut:]])
        rv = variants(rtrain)
        runseen = EventLog([t for t in rtest if act(t) not in rv])
        rsh, rflags, _, _, _ = shadow(rtrain)
        row = {"seed": cs, "n_train": len(rtrain), "n_test": len(rtest), "n_unseen": len(runseen), "models": {}}
        for mn in MODELS:
            net, im, fm = MINERS[mn](rtrain)
            row["models"][mn] = {"n_transitions": len(net.transitions), "shadow": agg(replay(rsh, net, im, fm)),
                                 "train": agg(replay(rtrain, net, im, fm)), "test_all": agg(replay(rtest, net, im, fm)),
                                 "test_unseen": agg(replay(runseen, net, im, fm))}
        rec["random_split"].append(row)
        print(f"random split seed {cs}: unseen {len(runseen)}; " + "; ".join(
            f"{mn} shadow {v['shadow']['strict']:.3f} train {v['train']['strict']:.3f} unseen {v['test_unseen']['strict']:.3f}"
            for mn, v in row["models"].items()), flush=True)

    rec["seconds"] = time.time() - t0
    rec["protocol"] = "temporal split 70/30 by case start; random split control seeds 0,1,2; shadow seed 42, K=1, N=6, tau=5, mle; v2.6 core; pm4py " + pm4py.__version__
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "l5_check.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    write_summary(rec)
    print(f"done in {rec['seconds']:.0f}s", flush=True)


def f3(x):
    return "--" if x is None else f"{x:.3f}"


def write_summary(rec):
    L = [f"# L5 strict-reading gap on the temporal split ({rec['protocol']})", "",
         f"Train {rec['n_train']} cases ({rec['train_range'][0]} to {rec['train_range'][1]}), test {rec['n_test']} "
         f"({rec['test_range'][0]} to {rec['test_range'][1]}), unseen test {rec['n_unseen']}; last event {rec['log_end']}.", "",
         f"Training end activities (>= 1 % of training cases): {rec['end_activities']}", "",
         f"Unseen test profile: {rec['unseen_profile']}", "", f"Shadow log: {rec['shadow']}", "",
         f"Lengths: {rec['lengths']}", ""]
    for mn, m in rec["models"].items():
        L += [f"## {mn} ({m['n_transitions']} transitions)", "", "| set | n | strict | graded |", "|---|---|---|---|"]
        for k in ("shadow", "shadow_regular", "shadow_mutated", "train", "test_all", "test_seen", "test_unseen"):
            L.append(f"| {k} | {m[k]['n']} | {f3(m[k]['strict'])} | {f3(m[k]['graded'])} |")
        for k, v in m["unseen_by_profile"].items():
            L.append(f"| unseen, {k} | {v['n']} | {f3(v['strict'])} | {f3(v['graded'])} |")
        for k, v in m["train_by_end"].items():
            L.append(f"| train, {k} | {v['n']} | {f3(v['strict'])} | {f3(v['graded'])} |")
        for k, v in m["shadow_by_end"].items():
            L.append(f"| shadow, {k} | {v['n']} | {f3(v['strict'])} | {f3(v['graded'])} |")
        L += ["", f"Reproduces stored (fresh, stored): {m['reproduces_stored']}", "",
              "| decile | train from | train strict | test from | test strict | unseen n | unseen strict |", "|---|---|---|---|---|---|---|"]
        for k in range(10):
            a, b, c = m["train_deciles"][k], m["test_deciles_all"][k], m["test_deciles_unseen"][k]
            L.append(f"| {k + 1} | {a['from'][:10]} | {f3(a['strict'])} | {b['from'][:10]} | {f3(b['strict'])} | {c['n']} | {f3(c['strict'])} |")
        L.append("")
    L += ["## Random 70/30 split (no time order)", "", "| seed | model | shadow strict | train strict | test strict | unseen n | unseen strict | unseen graded |",
          "|---|---|---|---|---|---|---|---|"]
    for row in rec["random_split"]:
        for mn, v in row["models"].items():
            L.append(f"| {row['seed']} | {mn} | {f3(v['shadow']['strict'])} | {f3(v['train']['strict'])} | {f3(v['test_all']['strict'])} | "
                     f"{v['test_unseen']['n']} | {f3(v['test_unseen']['strict'])} | {f3(v['test_unseen']['graded'])} |")
    open(os.path.join(OUT_DIR, "summary_l5_check.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
