"""Memorizing models: separate ShadowGen from fitness on the training singletons (idea 16, control of resub_check.py).

On the six benchmark nets, replaying the training singletons on the training net matches the unseen-only reference as
well as ShadowGen does (results/count_bound/summary_resub_split.md). The two readings can differ only on a model that
memorizes training behavior. This script adds two model families, both built on the training split, and scores each
with three readings of one acceptance function:
  reference      share of the unseen test cases (variant absent from training) the model accepts, case-weighted
  ShadowGen      share of the shadow log the model accepts (seed 42, 1,000 traces, N=6, tau=5, mle; also the
                 count-bounded shadow log of count_bound_check.py)
  singleton      share of the training singleton variants the model accepts (resubstitution, no generator)

Families:
  A_k     k-window automaton of the training variants: state = last k activities (k = inf: the whole prefix, i.e.
          the prefix tree, which accepts exactly the training variants). Small k generalizes, large k memorizes.
  T_*     trace models: top 50 variants (the benchmark pole Trace_Filtered), all non-singleton variants, all
          non-singletons plus a random half of the singletons (seed 0), all training variants.

Strict acceptance is exact membership (deterministic automaton run, final state observed). For the trace models a
graded acceptance is also computed on L1 and L2: alignment fitness with unit costs, which on a trace model has the
closed form 1 - min_v (|s| + |v| - 2 LCS(s, v)) / (|s| + min_v |v|) (pm4py's alignment fitness on that net).
The six benchmark nets enter the extended criteria with their stored strict and graded readings from
results/count_bound/resub_<key>_<split>.json (read only).

Output: results/memorize/<key>_<split>.json, summary.md (new folder).
Run from the repo root:  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/memorize_check.py D1 D2 D3 D5 D4
"""
import os
import sys
import json
import time
import random

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["TQDM_DISABLE"] = "1"
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, _HERE)

import numpy as np  # noqa: E402
import pm4py  # noqa: E402
from scipy import stats  # noqa: E402

from datasets import get_log_path  # noqa: E402
from temporal_holdout import temporal_split, variants  # noqa: E402
from temporal_drift_screen import random_split  # noqa: E402
from singleton_weighting import criteria  # noqa: E402
from count_bound_check import act, bounds, draw_logs, GEN_KW, LKEY, SIX  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

OUT_DIR = os.path.join(_HERE, "results", "memorize")
CB_DIR = os.path.join(_HERE, "results", "count_bound")
K_LIST = [1, 2, 3, 4, 6, 10, None]  # None = whole prefix
GRADED_LOGS = {"D1", "D2"}


# ---------- k-window automaton ----------
def build_automaton(train_variants, k):
    ids, delta, finals = {(): 0}, {}, set()
    for v in train_variants:
        s, hist = 0, ()
        for a in v:
            hist = hist + (a,)
            key = hist if k is None else hist[-k:]
            nxt = ids.setdefault(key, len(ids))
            delta[(s, a)] = nxt
            s = nxt
        finals.add(s)
    return delta, finals, len(ids)


def accepts(seq, delta, finals):
    s = 0
    for a in seq:
        s = delta.get((s, a))
        if s is None:
            return False
    return s in finals


# ---------- graded acceptance on a trace model (closed-form alignment) ----------
def lcs_masks(v, code):
    m = {}
    for i, a in enumerate(v):
        c = code[a]
        m[c] = m.get(c, 0) | (1 << i)
    return m


def lcs_len(masks, n, seq_codes):
    """Bit-parallel LCS length of a pattern (masks over n positions) and a sequence (Crochemore et al. 2001)."""
    full = (1 << n) - 1
    V = full
    for c in seq_codes:
        U = V & masks.get(c, 0)
        V = ((V + U) | (V - U)) & full
    return n - bin(V).count("1")


def trace_model_fitness(seqs, model_variants, code):
    pats = sorted(((len(v), lcs_masks(v, code)) for v in model_variants), key=lambda x: x[0])
    min_len = pats[0][0]
    out = []
    for s in seqs:
        sc = [code.get(a, -1) for a in s]
        ls = len(sc)
        best = None
        for n, masks in pats:
            if best is not None and abs(ls - n) >= best:
                if n > ls:
                    break
                continue
            cost = ls + n - 2 * lcs_len(masks, n, sc)
            if best is None or cost < best:
                best = cost
                if best == 0:
                    break
        out.append(1.0 - best / (ls + min_len))
    return np.array(out)


def check_lcs():
    rng = random.Random(1)
    for _ in range(300):
        a = [rng.randint(0, 4) for _ in range(rng.randint(1, 12))]
        b = [rng.randint(0, 4) for _ in range(rng.randint(0, 12))]
        dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        for i in range(len(a)):
            for j in range(len(b)):
                dp[i + 1][j + 1] = dp[i][j] + 1 if a[i] == b[j] else max(dp[i][j + 1], dp[i + 1][j])
        masks = {}
        for i, c in enumerate(a):
            masks[c] = masks.get(c, 0) | (1 << i)
        assert lcs_len(masks, len(a), b) == dp[-1][-1], (a, b)


def process(dkey, split):
    t0 = time.time()
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    train, test = temporal_split(log)[:2] if split == "temporal" else random_split(log, seed=0)
    vtr, vte = variants(train), variants(test)
    un = [v for v in vte if v not in vtr]
    uw = np.array([vte[v] for v in un], float)
    singles = [v for v, c in vtr.items() if c == 1]
    nonsingle = [v for v, c in vtr.items() if c > 1]
    gen = load_algorithm("v2.6").generate_shadow_log
    random.seed(42)
    np.random.seed(42)
    sh, flags, *_ = gen(train, **GEN_KW)
    orig, bnd, info = draw_logs(train, bounds(vtr), 1, gen)
    sh_seq = [act(t) for t in sh]
    assert sh_seq == [act(t) for t in orig[0]], "shadow log differs from the count-bound stream"
    bd_seq = [act(t) for t in bnd[0]]
    mutated = np.array([bool(f) for f in flags]) if len(flags) == len(sh_seq) else None
    seen_in_shadow = sum(1 for s in sh_seq if s in vtr)
    rec = {"log": LKEY[dkey], "split": split, "n_train_cases": len(train), "n_train_variants": len(vtr),
           "n_singletons": len(singles), "n_nonsingleton_variants": len(nonsingle), "n_unseen_cases": int(uw.sum()),
           "n_unseen_variants": len(un), "shadow_in_training": seen_in_shadow,
           "mutated_share": float(mutated.mean()) if mutated is not None else None, "models": {}}
    print(f"\n=== {rec['log']} {split}: train {len(train)} cases, {len(vtr)} variants ({len(singles)} singletons); unseen "
          f"{int(uw.sum())} cases; shadow traces in training {seen_in_shadow}; mutated {rec['mutated_share']} [{time.time() - t0:.0f}s]", flush=True)

    def strict_row(acc):
        a_un = np.array([acc(v) for v in un], float)
        a_sh = np.array([acc(s) for s in sh_seq], float)
        a_bd = np.array([acc(s) for s in bd_seq], float)
        a_si = np.array([acc(v) for v in singles], float)
        a_tr = float(np.dot([acc(v) for v in vtr], list(vtr.values())) / sum(vtr.values()))
        row = {"ref": float(np.dot(a_un, uw) / uw.sum()), "shadowgen": float(a_sh.mean()), "shadowgen_bounded": float(a_bd.mean()),
               "singleton": float(a_si.mean()), "train_cases": a_tr}
        if mutated is not None:
            row["shadowgen_regular"] = float(a_sh[~mutated].mean()) if (~mutated).any() else None
            row["shadowgen_mutated"] = float(a_sh[mutated].mean()) if mutated.any() else None
        return row

    for k in K_LIST:
        tm = time.time()
        delta, finals, n_states = build_automaton(vtr, k)
        row = strict_row(lambda s: accepts(s, delta, finals))
        row["n_states"] = n_states
        name = f"A_{'inf' if k is None else k}"
        rec["models"][name] = row
        print(f"  {name:12s} states {n_states:8d} | ref {row['ref']:.3f} ShadowGen {row['shadowgen']:.3f} (regular "
              f"{row.get('shadowgen_regular')}, mutated {row.get('shadowgen_mutated')}) bounded {row['shadowgen_bounded']:.3f} "
              f"singleton {row['singleton']:.3f} [{time.time() - tm:.0f}s]", flush=True)

    rng = random.Random(0)
    half = rng.sample(singles, len(singles) // 2)
    top50 = [v for v, c in sorted(vtr.items(), key=lambda i: i[1], reverse=True)[:50]]
    code = {}
    for v in list(vtr) + un + sh_seq + bd_seq:
        for a in v:
            code.setdefault(a, len(code))
    for name, mv in (("T_top50", top50), ("T_nonsingleton", nonsingle), ("T_half", nonsingle + half), ("T_all", list(vtr))):
        tm = time.time()
        mset = set(mv)
        row = strict_row(lambda s: s in mset)
        row["n_variants"] = len(mv)
        if dkey in GRADED_LOGS:
            f_un = trace_model_fitness(un, mv, code)
            f_sh = trace_model_fitness(sh_seq, mv, code)
            f_bd = trace_model_fitness(bd_seq, mv, code)
            f_si = trace_model_fitness(singles, mv, code)
            row["graded"] = {"ref": float(np.dot(f_un, uw) / uw.sum()), "shadowgen": float(f_sh.mean()),
                             "shadowgen_bounded": float(f_bd.mean()), "singleton": float(f_si.mean())}
        rec["models"][name] = row
        g = row.get("graded")
        gtxt = (f" | graded ref {g['ref']:.3f} ShadowGen {g['shadowgen']:.3f} bounded {g['shadowgen_bounded']:.3f} "
                f"singleton {g['singleton']:.3f}") if g else ""
        print(f"  {name:14s} variants {len(mv):6d} | strict ref {row['ref']:.3f} ShadowGen {row['shadowgen']:.3f} "
              f"singleton {row['singleton']:.3f}{gtxt} [{time.time() - tm:.0f}s]", flush=True)

    # extended criteria: six benchmark nets (stored readings) plus the memorizing models
    p = os.path.join(CB_DIR, f"resub_{dkey}_{split}.json")
    if os.path.exists(p):
        rs = json.load(open(p, encoding="utf-8"))["miners"]
        nets = {m: {"ref": rs[m]["ref_strict"], "shadowgen": rs[m]["accept"], "shadowgen_bounded": rs[m]["accept_bounded"],
                    "singleton": rs[m]["resub_singleton_strict"]} for m in SIX}
        sets = {"six nets": nets, "six nets + A_k": {**nets, **{m: r for m, r in rec["models"].items() if m.startswith("A_")}},
                "six nets + A_k + T_*": {**nets, **rec["models"]}}
        rec["criteria_strict"] = {}
        for sname, rows in sets.items():
            ref = [r["ref"] for r in rows.values()]
            rec["criteria_strict"][sname] = {q: criteria([r[q] for r in rows.values()], ref)
                                             for q in ("shadowgen", "shadowgen_bounded", "singleton")}
        if dkey in GRADED_LOGS:
            gnets = {m: {"ref": rs[m]["ref"], "shadowgen": rs[m]["score"], "shadowgen_bounded": rs[m]["score_bounded"],
                         "singleton": rs[m]["resub_singleton"]} for m in SIX}
            grows = {**gnets, **{m: r["graded"] for m, r in rec["models"].items() if "graded" in r}}
            ref = [r["ref"] for r in grows.values()]
            rec["criteria_graded"] = {"six nets + T_*": {q: criteria([r[q] for r in grows.values()], ref)
                                                         for q in ("shadowgen", "shadowgen_bounded", "singleton")}}
        for sname, cs in rec["criteria_strict"].items():
            print(f"  strict, {sname:22s} " + " | ".join(f"{q} MAE {c['mae']:.3f} Pearson {c['pearson']:.3f} Spearman {c['spearman']:.2f}"
                                                       for q, c in cs.items()), flush=True)
        for sname, cs in rec.get("criteria_graded", {}).items():
            print(f"  graded, {sname:22s} " + " | ".join(f"{q} MAE {c['mae']:.3f} Pearson {c['pearson']:.3f} Spearman {c['spearman']:.2f}"
                                                       for q, c in cs.items()), flush=True)
    rec["generation"] = info
    rec["seconds"] = time.time() - t0
    rec["protocol"] = "training split; seed 42; " + str(GEN_KW) + "; strict = exact membership; graded = closed-form alignment on trace models"
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"{dkey}_{split}.json"), "w", encoding="utf-8") as fp:
        json.dump(rec, fp, indent=1)


def summarize():
    L = ["# Memorizing models: ShadowGen against fitness on the training singletons", "",
         "Strict acceptance (exact membership). Reference: unseen test cases, case-weighted. Singleton: training singleton variants.", "",
         "| log | split | model | size | reference | ShadowGen | regular / mutated | bounded | singleton |", "|---|---|---|---|---|---|---|---|---|"]
    C = ["", "## Criteria over the extended model set (strict)", "",
         "| log | split | model set | n | ShadowGen MAE / Pearson / Spearman | bounded | singleton |", "|---|---|---|---|---|---|---|"]
    A = ["", "## Automaton family alone (A_1 to A_inf, 7 models; singleton is constant 1, so it has no rank)", "",
         "| log | split | ShadowGen MAE / max dev / Spearman | bounded | singleton MAE / max dev |", "|---|---|---|---|---|"]
    G = ["", "## Graded (closed-form alignment on trace models; L1, L2)", "",
         "| log | split | model | reference | ShadowGen | bounded | singleton |", "|---|---|---|---|---|---|---|"]
    f3 = lambda x: "-" if x is None else f"{x:.3f}"  # noqa: E731
    for k in ("D1", "D2", "D3", "D4", "D5"):
        for s in ("temporal", "random"):
            p = os.path.join(OUT_DIR, f"{k}_{s}.json")
            if not os.path.exists(p):
                continue
            r = json.load(open(p, encoding="utf-8"))
            for i, (m, x) in enumerate(r["models"].items()):
                size = x.get("n_states", x.get("n_variants"))
                L.append(f"| {r['log'] if i == 0 else ''} | {s if i == 0 else ''} | {m} | {size} | {x['ref']:.3f} | {x['shadowgen']:.3f} | "
                         f"{f3(x.get('shadowgen_regular'))} / {f3(x.get('shadowgen_mutated'))} | {x['shadowgen_bounded']:.3f} | {x['singleton']:.3f} |")
                if "graded" in x:
                    g = x["graded"]
                    G.append(f"| {r['log']} | {s} | {m} | {g['ref']:.3f} | {g['shadowgen']:.3f} | {g['shadowgen_bounded']:.3f} | {g['singleton']:.3f} |")
            am = [m for m in r["models"] if m.startswith("A_")]
            aref = np.array([r["models"][m]["ref"] for m in am])
            cells = []
            for q in ("shadowgen", "shadowgen_bounded", "singleton"):
                x = np.array([r["models"][m][q] for m in am])
                d = np.abs(x - aref)
                rho = f" / {stats.spearmanr(x, aref).statistic:.2f}" if np.std(x) > 0 else ""
                cells.append(f"{d.mean():.3f} / {d.max():.3f}{rho}")
            A.append(f"| {r['log']} | {s} | " + " | ".join(cells) + " |")
            n_mem = {"six nets": 6, "six nets + A_k": 6 + len(K_LIST), "six nets + A_k + T_*": len(r["models"]) + 6}
            for sname, cs in r.get("criteria_strict", {}).items():
                C.append(f"| {r['log']} | {s} | {sname} | {n_mem[sname]} | " + " | ".join(
                    f"{c['mae']:.3f} / {c['pearson']:.3f} / {c['spearman']:.2f}" for c in cs.values()) + " |")
            for sname, cs in r.get("criteria_graded", {}).items():
                C.append(f"| {r['log']} | {s} | graded, {sname} | {6 + 4} | " + " | ".join(
                    f"{c['mae']:.3f} / {c['pearson']:.3f} / {c['spearman']:.2f}" for c in cs.values()) + " |")
    open(os.path.join(OUT_DIR, "summary.md"), "w", encoding="utf-8").write("\n".join(L + C + A + G) + "\n")
    print("\n".join(L + C + A + G))


def main():
    check_lcs()
    keys = [a for a in sys.argv[1:] if a.startswith("D")] or ["D1", "D2", "D3", "D5", "D4"]
    if "--summary" not in sys.argv:
        for k in keys:
            for s in ("temporal", "random"):
                try:
                    process(k, s)
                except Exception as e:  # noqa: BLE001
                    import traceback
                    traceback.print_exc()
                    print(f"[{k} {s}] FAIL {type(e).__name__}: {e}", flush=True)
    summarize()


if __name__ == "__main__":
    main()
