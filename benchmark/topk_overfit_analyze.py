"""Summary of the overfitting ladder (benchmark/topk_overfit_test.py).

Reads results/topk_overfit/topk_<key>[_tag].json (or the .partial.json of a run in progress,
complete repetitions only) and writes results/topk_overfit/summary_<key>[_tag][_partial].md:
  A  per family and k: coverage, then training fitness / truth / ShadowGen, graded and strict
     (mean over repetitions)
  B  over the ladder: agreement of ShadowGen and of training fitness with the truth
     (Pearson, Spearman, MAE; median over repetitions), per family and for Trie and IM pooled
Run from the repo root:  env/Scripts/python.exe benchmark/topk_overfit_analyze.py D1 D2
"""
import os
import sys
import json
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(_HERE, "results", "topk_overfit")
FAMILIES = ["Trie", "IM", "Trace"]


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


def label(m):
    return "all" if m["all"] else str(m["k"])


def analyze(key, tag=""):
    stem = f"topk_{key}" + (f"_{tag}" if tag else "")
    final = os.path.join(OUT_DIR, stem + ".json")
    running = not os.path.exists(final)
    rec = json.load(open(final if not running else os.path.join(OUT_DIR, stem + ".partial.json"),
                         encoding="utf-8"))
    models = [m for m in rec["models"].values() if not m.get("error")]
    errors = [m for m in rec["models"].values() if m.get("error")]
    by_rep = {}
    for m in models:
        by_rep.setdefault(m["rep"], []).append(m)
    # a repetition is complete when Trie and IM both reach k = all
    reps = sorted(r for r, ms in by_rep.items()
                  if all(any(m["family"] == f and m["all"] for m in ms) for f in ("Trie", "IM")))
    if not reps:
        print(f"[{key}] no complete repetition yet ({len(models)} models)")
        return
    L = [f"# Overfitting ladder, {key} ({rec['dataset']}), {rec['n_cases']} cases, "
         f"{len(reps)} repetitions" + (f" of {rec['reps']} (run in progress)" if running else ""), "",
         rec.get("protocol", "protocol: see benchmark/topk_overfit_test.py"), ""]
    sp = [rec["splits"][str(r)] for r in reps]
    L.append(f"Training variants {np.mean([s['var_train'] for s in sp]):.0f}, unseen share of the "
             f"future {np.mean([s['unseen_share'] for s in sp]):.3f}, errors {len(errors)}.")
    L.append("")
    L.append("## A. Per family and k (mean over repetitions): training fitness / truth / ShadowGen")
    for fam in FAMILIES:
        rows = {}
        for r in reps:
            for m in by_rep[r]:
                if m["family"] == fam:
                    rows.setdefault(label(m), []).append(m)
        if not rows:
            continue
        L += ["", f"### {fam}", "", "| k | n | coverage | graded | strict |", "|---|---|---|---|---|"]
        order = sorted(rows, key=lambda s: (s == "all", int(s) if s != "all" else 0))
        for k in order:
            ms = rows[k]
            mean = lambda f: float(np.mean([m[f] for m in ms]))  # noqa: E731
            L.append(f"| {k} | {len(ms)} | {mean('coverage'):.3f} | "
                     f"{mean('train_fit'):.3f} / {mean('unseen_fit'):.3f} / {mean('shadowgen'):.3f} | "
                     f"{mean('train_fit_strict'):.3f} / {mean('unseen_fit_strict'):.3f} / "
                     f"{mean('shadowgen_strict'):.3f} |")
    L += ["", "## B. Agreement with the truth over the ladder (median over repetitions)", "",
          "| models | reading | predictor | Pearson | Spearman | MAE | spread predictor | spread truth |",
          "|---|---|---|---|---|---|---|---|"]
    for name, fams in [("Trie", ["Trie"]), ("IM", ["IM"]), ("Trie and IM", ["Trie", "IM"])]:
        for reading, tk, preds in [("graded", "unseen_fit", [("ShadowGen", "shadowgen"), ("fitness", "train_fit")]),
                                   ("strict", "unseen_fit_strict", [("ShadowGen", "shadowgen_strict"),
                                                                    ("fitness", "train_fit_strict")])]:
            for pname, pk in preds:
                out = []
                for r in reps:
                    ms = [m for m in by_rep[r] if m["family"] in fams]
                    a = np.array([m[pk] for m in ms], float)
                    t = np.array([m[tk] for m in ms], float)
                    out.append((corr(a, t), corr(ranks(a), ranks(t)), float(np.mean(np.abs(a - t))),
                                float(a.max() - a.min()), float(t.max() - t.min())))
                med = np.nanmedian(np.array(out), axis=0) if not np.all(np.isnan(np.array(out)[:, 0])) \
                    else np.array([np.nan, np.nan] + list(np.median(np.array(out)[:, 2:], axis=0)))
                f = lambda v: "-" if np.isnan(v) else f"{v:.3f}"  # noqa: E731
                L.append(f"| {name} | {reading} | {pname} | {f(med[0])} | {f(med[1])} | {f(med[2])} | "
                         f"{f(med[3])} | {f(med[4])} |")
    text = "\n".join(L) + "\n"
    path = os.path.join(OUT_DIR, f"summary_{key}" + (f"_{tag}" if tag else "")
                        + ("_partial" if running else "") + ".md")
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(text)
    print(text)
    print(f"[written {path}]")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--tag=")]
    tag = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--tag=")), "")
    for k in args or ["D1", "D2"]:
        analyze(k, tag)
