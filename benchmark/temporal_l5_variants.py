"""Which variants and activities carry the L5 shift at the temporal cut?

Follow-up to temporal_l5_check.py: the infrequent inductive net accepts 0.987 of its training split and 0.448 of the
future cases whose variant does occur in training. This script lists the most frequent future variants with their
training frequency and acceptance, the activities whose case share changes most between the splits, and strict
acceptance by month of case start (the net is discovered on the training split).

Output: results/temporal_unseen/l5_variants.json and summary_l5_variants.md (new files).
Run from the repo root:  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/temporal_l5_variants.py
"""
import os
import sys
import json
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
from datasets import get_log_path  # noqa: E402
from temporal_holdout import temporal_split, variants, case_start  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "temporal_unseen")


def act(t):
    return tuple(e["concept:name"] for e in t)


def main():
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path("D5")))
    train, test, *_ = temporal_split(log)
    vtr, vte = variants(train), variants(test)
    net, im, fm = MINERS["Inductive_Infrequent"](train)
    # one representative trace per variant; strict acceptance is a property of the variant under replay
    reps = {}
    for t in log:
        reps.setdefault(act(t), t)
    keys = list(reps)
    res = token_replay.apply(EventLog([reps[k] for k in keys]), net, im, fm)
    fit = {k: bool(r["trace_is_fit"]) for k, r in zip(keys, res)}
    rec = {"n_transitions": len(net.transitions), "n_train": len(train), "n_test": len(test)}

    # acceptance re-derived from variant flags, to check against l5_check.json
    rec["train_strict_from_variants"] = sum(c for v, c in vtr.items() if fit[v]) / len(train)
    rec["test_seen_strict_from_variants"] = sum(c for v, c in vte.items() if v in vtr and fit[v]) / sum(c for v, c in vte.items() if v in vtr)

    top = []
    for v, c in vte.most_common(15):
        top.append({"variant": list(v), "test_count": c, "test_share": c / len(test), "train_count": vtr.get(v, 0),
                    "train_share": vtr.get(v, 0) / len(train), "accepted": fit[v]})
    rec["top_test_variants"] = top
    # rejected seen mass: which training-rare variants carry it
    rej = [(v, c) for v, c in vte.items() if v in vtr and not fit[v]]
    rec["rejected_seen_test_cases"] = sum(c for _, c in rej)
    rec["rejected_seen_top"] = [{"variant": list(v), "test_count": c, "train_count": vtr[v]} for v, c in sorted(rej, key=lambda x: -x[1])[:10]]

    def act_share(lg):
        cnt = Counter()
        for t in lg:
            for a in set(e["concept:name"] for e in t):
                cnt[a] += 1
        return {a: c / len(lg) for a, c in cnt.items()}
    s_tr, s_te = act_share(train), act_share(test)
    acts = sorted(set(s_tr) | set(s_te), key=lambda a: -abs(s_te.get(a, 0) - s_tr.get(a, 0)))
    rec["activity_shift"] = [{"activity": a, "train": s_tr.get(a, 0), "test": s_te.get(a, 0)} for a in acts[:12]]

    # repeated activities per case (a frequent kind of deviation on L5)
    def rep_share(lg):
        return sum(1 for t in lg if len(act(t)) != len(set(act(t)))) / len(lg)
    rec["cases_with_repeated_activity"] = {"train": rep_share(train), "test": rep_share(test)}

    # activities that enter the future: case share up by more than 0.2
    new_acts = [a for a in acts if s_te.get(a, 0) - s_tr.get(a, 0) > 0.2]
    rec["new_activities"] = new_acts
    has_new = lambda v: any(a in new_acts for a in v)  # noqa: E731
    rec["infrequent_net_has_label"] = {a: any(t.label == a for t in net.transitions) for a in new_acts}

    # all six miners on the future, split by whether the case contains a new activity
    stored = json.load(open(os.path.join(OUT_DIR, "temporal_unseen_D5.json"), encoding="utf-8"))["models"]
    tkeys = list(vte)
    tlog = EventLog([reps[k] for k in tkeys])
    groups = {"all": lambda v: True, "unseen": lambda v: v not in vtr,
              "with_new": lambda v: has_new(v), "without_new": lambda v: not has_new(v),
              "unseen_without_new": lambda v: v not in vtr and not has_new(v)}
    rec["share_with_new"] = {"test": sum(c for v, c in vte.items() if has_new(v)) / len(test),
                             "test_unseen": sum(c for v, c in vte.items() if v not in vtr and has_new(v)) / sum(c for v, c in vte.items() if v not in vtr),
                             "train": sum(c for v, c in vtr.items() if has_new(v)) / len(train)}
    rec["miners"] = {}
    for mn in ["Alpha", "Alpha+", "Heuristics", "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent"]:
        n2, i2, f2 = (net, im, fm) if mn == "Inductive_Infrequent" else MINERS[mn](train)
        rr = token_replay.apply(tlog, n2, i2, f2)
        per = {k: (1.0 if r["trace_is_fit"] else 0.0, float(r["trace_fitness"])) for k, r in zip(tkeys, rr)}
        row = {"shadowgen": stored[mn]["shadowgen"], "shadowgen_strict": stored[mn]["shadowgen_strict"],
               "has_new_label": {a: any(t.label == a for t in n2.transitions) for a in new_acts}}
        for g, pred in groups.items():
            ks = [k for k in tkeys if pred(k)]
            n = sum(vte[k] for k in ks)
            row[g] = {"n": n, "strict": sum(per[k][0] * vte[k] for k in ks) / n if n else None,
                      "graded": sum(per[k][1] * vte[k] for k in ks) / n if n else None}
        rec["miners"][mn] = row
        print(f"{mn}: sg {row['shadowgen']:.3f} all {row['all']['graded']:.3f} unseen {row['unseen']['graded']:.3f} "
              f"without_new {row['without_new']['graded']:.3f} unseen_without_new {row['unseen_without_new']['graded']:.3f}", flush=True)

    month = defaultdict(lambda: [0, 0])
    for t in log:
        s = case_start(t)
        k = f"{s.year:04d}-{s.month:02d}"
        month[k][0] += 1
        month[k][1] += fit[act(t)]
    rec["by_start_month"] = {k: {"n": n, "strict": a / n} for k, (n, a) in sorted(month.items()) if n >= 200}

    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(rec, open(os.path.join(OUT_DIR, "l5_variants.json"), "w", encoding="utf-8"), indent=1)
    L = [f"# L5 variants and activities at the temporal cut (Inductive_Infrequent, {rec['n_transitions']} transitions)", "",
         f"Strict from variant flags: train {rec['train_strict_from_variants']:.3f}, seen test {rec['test_seen_strict_from_variants']:.3f}; "
         f"rejected seen test cases {rec['rejected_seen_test_cases']}.", "",
         f"Cases with a repeated activity: {rec['cases_with_repeated_activity']}", "",
         "## Top test variants", "", "| test n | test share | train n | train share | accepted | variant |", "|---|---|---|---|---|---|"]
    for r in top:
        L.append(f"| {r['test_count']} | {r['test_share']:.3f} | {r['train_count']} | {r['train_share']:.4f} | {r['accepted']} | {' > '.join(r['variant'])} |")
    L += ["", "## Rejected seen variants, by test count", "", "| test n | train n | variant |", "|---|---|---|"]
    for r in rec["rejected_seen_top"]:
        L.append(f"| {r['test_count']} | {r['train_count']} | {' > '.join(r['variant'])} |")
    L += ["", "## Activity case share, largest changes", "", "| activity | train | test |", "|---|---|---|"]
    for r in rec["activity_shift"]:
        L.append(f"| {r['activity']} | {r['train']:.3f} | {r['test']:.3f} |")
    L += ["", f"## Future split by new activities {rec['new_activities']}", "",
          f"Share of cases with a new activity: {rec['share_with_new']}; infrequent net has the label: {rec['infrequent_net_has_label']}", "",
          "| miner | label in net | ShadowGen | all | unseen | with new | without new | unseen without new | strict SG | strict all | strict with new | strict without new | strict unseen without new |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for mn, r in rec["miners"].items():
        g = lambda k, m: "--" if r[k][m] is None else f"{r[k][m]:.3f}"  # noqa: E731
        L.append(f"| {mn} | {r['has_new_label']} | {r['shadowgen']:.3f} | {g('all', 'graded')} | {g('unseen', 'graded')} | {g('with_new', 'graded')} | "
                 f"{g('without_new', 'graded')} | {g('unseen_without_new', 'graded')} | {r['shadowgen_strict']:.3f} | {g('all', 'strict')} | "
                 f"{g('with_new', 'strict')} | {g('without_new', 'strict')} | {g('unseen_without_new', 'strict')} |")
    L.append("")
    L.append(f"n: " + str({k: v["n"] for k, v in next(iter(rec["miners"].values())).items() if isinstance(v, dict) and "n" in v}))
    L += ["", "## Strict acceptance by start month (months with >= 200 cases)", "", "| month | n | strict |", "|---|---|---|"]
    for k, v in rec["by_start_month"].items():
        L.append(f"| {k} | {v['n']} | {v['strict']:.3f} |")
    open(os.path.join(OUT_DIR, "summary_l5_variants.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
