"""Graded readings on the k-window automata of memorize_check.py (idea 19).

memorize_check.py scores the automata A_k with exact membership only. This script adds the graded reading: alignment
fitness with unit costs on the deterministic automaton, the reading pm4py's alignments give on the equivalent
state-machine net, 1 - cost / (|s| + shortest accepted word length). The optimal cost is found by A* over
(trace position, state) with sync moves (cost 0), log moves and model moves (cost 1) and the admissible heuristic
max(0, d_final(q) - remaining events). Check: on the prefix tree A_inf the language equals the trace model T_all, so the
graded values must equal the closed form of memorize_check.py (L1, L2).
Readings as in memorize_check.py: reference (unseen test cases, case-weighted), ShadowGen (seed 42 shadow log of the
training split) and its count-bounded version, singleton (training singletons; 1 by construction on every A_k).
The six benchmark nets enter the extended set with their graded token-replay readings from
results/count_bound/resub_<key>_<split>.json (read only); each model's three readings share one acceptance function.

A model whose queries exceed the wall-clock budget (BUDGET seconds per model and split) or the node cap of one query
is recorded as not completed; no partial means are reported.

Output: results/memorize/graded_<key>_<split>.json, summary_graded.md.
Run from the repo root:  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/memorize_graded.py D1 D2 D3 D5 D4
"""
import os
import sys
import json
import time
import heapq
import random
from collections import deque

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
from count_bound_check import act, bounds, draw_logs, LKEY, SIX  # noqa: E402
from memorize_check import build_automaton, trace_model_fitness, K_LIST, OUT_DIR, CB_DIR  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

BUDGET = int(os.environ.get("MEMO_BUDGET", "1800"))
NODE_CAP = int(os.environ.get("MEMO_NODE_CAP", "2000000"))
USE_H2 = "--no-h2" not in sys.argv
FULL_LOGS = {"D1", "D2"}  # all queries; other logs use a fixed sample
SAMPLE = 300


class Budget(Exception):
    pass


def prepare(delta, finals, n_states):
    out = [dict() for _ in range(n_states)]
    rev = [[] for _ in range(n_states)]
    for (s, a), t in delta.items():
        out[s][a] = t
        rev[t].append(s)
    dfin = [None] * n_states
    dq = deque()
    for f in finals:
        dfin[f] = 0
        dq.append(f)
    while dq:
        q = dq.popleft()
        for p in rev[q]:
            if dfin[p] is None:
                dfin[p] = dfin[q] + 1
                dq.append(p)
    big = 10 ** 9
    return out, [big if d is None else d for d in dfin]


def reach_masks(out, code):
    """Bitmask of the activities on some path from each state (fixed point; the automata can have cycles)."""
    R = [0] * len(out)
    for q, o in enumerate(out):
        for a in o:
            R[q] |= 1 << code[a]
    changed = True
    while changed:
        changed = False
        for q in range(len(out) - 1, -1, -1):
            m = R[q]
            for q2 in out[q].values():
                m |= R[q2]
            if m != R[q]:
                R[q] = m
                changed = True
    return R


def align_cost(seq, out, finals, dfin, R=None, code=None):
    """A* with h = max(h1, h2): h1 = model steps still needed beyond the remaining events, h2 = remaining events whose
    activity no path from the state contains (they must be log moves). Both are consistent, so is their max."""
    n = len(seq)
    if R is not None:
        # suf[i]: (activity bit, count) over the events from position i on; an activity outside the model has bit 0
        suf, cnt = [None] * (n + 1), {}
        suf[n] = []
        for i in range(n - 1, -1, -1):
            b = (1 << code[seq[i]]) if seq[i] in code else 0
            cnt[b] = cnt.get(b, 0) + 1
            suf[i] = list(cnt.items())

        def h2(i, q):
            m = R[q]
            return sum(c for b, c in suf[i] if not (b & m))
    else:
        def h2(i, q):
            return 0
    hh = lambda i, q: max(max(0, dfin[q] - (n - i)), h2(i, q))  # noqa: E731
    best = {(0, 0): 0}
    heap = [(hh(0, 0), 0, 0, 0)]
    pops = 0
    while heap:
        f, g, i, q = heapq.heappop(heap)
        if best.get((i, q), 1 << 60) < g:
            continue
        if i == n and q in finals:
            return g
        pops += 1
        if pops > NODE_CAP:
            raise Budget("node cap")
        moves = []
        if i < n:
            q2 = out[q].get(seq[i])
            if q2 is not None:
                moves.append((i + 1, q2, g))
            moves.append((i + 1, q, g + 1))
        for q2 in out[q].values():
            moves.append((i, q2, g + 1))
        for i2, q2, g2 in moves:
            if g2 < best.get((i2, q2), 1 << 60):
                best[(i2, q2)] = g2
                heapq.heappush(heap, (g2 + hh(i2, q2), g2, i2, q2))
    raise RuntimeError("no accepted word reachable")


def fitness_all(seqs, out, finals, dfin, t_end, cache, R=None, code=None):
    res = []
    for s in seqs:
        if s not in cache:
            if time.time() > t_end:
                raise Budget("time budget")
            c = align_cost(s, out, finals, dfin, R, code)
            cache[s] = 1.0 - c / (len(s) + dfin[0])
        res.append(cache[s])
    return np.array(res)


def process(dkey, split):
    t0 = time.time()
    log = pm4py.convert_to_event_log(pm4py.read_xes(get_log_path(dkey)))
    train, test = temporal_split(log)[:2] if split == "temporal" else random_split(log, seed=0)
    vtr, vte = variants(train), variants(test)
    un = [v for v in vte if v not in vtr]
    uw = np.array([vte[v] for v in un], float)
    gen = load_algorithm("v2.6").generate_shadow_log
    orig, bnd, _ = draw_logs(train, bounds(vtr), 1, gen)
    sh_seq, bd_seq = [act(t) for t in orig[0]], [act(t) for t in bnd[0]]
    strict = json.load(open(os.path.join(OUT_DIR, f"{dkey}_{split}.json"), encoding="utf-8"))["models"]
    sampled = dkey not in FULL_LOGS
    if sampled:
        # case-weighted draw of unseen cases (with replacement, seed 0) and the first SAMPLE shadow and bounded traces
        rng = np.random.default_rng(0)
        idx = rng.choice(len(un), size=SAMPLE, replace=True, p=uw / uw.sum())
        un, uw = [un[i] for i in idx], np.ones(SAMPLE)
        sh_seq, bd_seq = sh_seq[:SAMPLE], bd_seq[:SAMPLE]
    rec = {"log": LKEY[dkey], "split": split, "budget_s": BUDGET, "node_cap": NODE_CAP,
           "sample": SAMPLE if sampled else None, "models": {}}
    print(f"\n=== {rec['log']} {split}: {len(un)} unseen variants, shadow {len(sh_seq)}, bounded {len(bd_seq)} [{time.time() - t0:.0f}s]", flush=True)
    for k in K_LIST:
        tm = time.time()
        name = f"A_{'inf' if k is None else k}"
        delta, finals, n_states = build_automaton(vtr, k)
        out, dfin = prepare(delta, finals, n_states)
        code = {a: i for i, a in enumerate(sorted({a for v in vtr for a in v}))}
        R = reach_masks(out, code) if USE_H2 else None
        cache = {}
        try:
            f_un = fitness_all(un, out, finals, dfin, tm + BUDGET, cache, R, code)
            f_sh = fitness_all(sh_seq, out, finals, dfin, tm + BUDGET, cache, R, code)
            f_bd = fitness_all(bd_seq, out, finals, dfin, tm + BUDGET, cache, R, code)
        except Budget as e:
            if k is not None:
                rec["models"][name] = {"completed": False, "reason": str(e), "seconds": time.time() - tm, "n_states": n_states}
                print(f"  {name:6s} states {n_states:8d} | not completed ({e}) after {time.time() - tm:.0f}s, {len(cache)} queries done", flush=True)
                continue
            # A_inf accepts exactly the training variants: exact closed form of the trace model (checked equal on L1, L2)
            print(f"  {name:6s} A* stopped ({e}) after {time.time() - tm:.0f}s; closed form of the trace model instead", flush=True)
            tcode = {}
            for v in list(vtr) + un + sh_seq + bd_seq:
                for a in v:
                    tcode.setdefault(a, len(tcode))
            mv = list(vtr)
            f_un, f_sh, f_bd = (trace_model_fitness(x, mv, tcode) for x in (un, sh_seq, bd_seq))
            for s, f in zip(un + sh_seq + bd_seq, np.concatenate([f_un, f_sh, f_bd])):
                cache[s] = float(f)
            method = "closed form (trace model of all training variants)"
        else:
            method = "A*"
        row = {"completed": True, "method": method, "n_states": n_states, "ref": float(np.dot(f_un, uw) / uw.sum()), "shadowgen": float(f_sh.mean()),
               "shadowgen_bounded": float(f_bd.mean()), "singleton": 1.0, "seconds": time.time() - tm,
               "strict_ref": strict[name]["ref"], "strict_shadowgen": strict[name]["shadowgen"]}
        if sampled:
            # sampling check: strict reading on the same sample (cost 0 = accepted) against the full strict reading
            row["strict_ref_sample"] = float(np.mean([cache[s] == 1.0 for s in un]))
            row["strict_shadowgen_sample"] = float(np.mean([cache[s] == 1.0 for s in sh_seq]))
        rec["models"][name] = row
        smp = (f" (sample {row['strict_ref_sample']:.3f}, {row['strict_shadowgen_sample']:.3f})" if sampled else "")
        print(f"  {name:6s} states {n_states:8d} | graded ref {row['ref']:.3f} ShadowGen {row['shadowgen']:.3f} bounded "
              f"{row['shadowgen_bounded']:.3f} singleton 1.000 | strict ref {row['strict_ref']:.3f} ShadowGen {row['strict_shadowgen']:.3f}"
              f"{smp} [{row['seconds']:.0f}s]", flush=True)
    t_all = strict.get("T_all", {}).get("graded")
    a_inf = rec["models"].get("A_inf", {})
    if t_all and a_inf.get("completed"):
        rec["check_A_inf_vs_T_all"] = {q: a_inf[q] - t_all[q] for q in ("ref", "shadowgen", "shadowgen_bounded")}
        print(f"  check A_inf - T_all (closed form): {rec['check_A_inf_vs_T_all']}", flush=True)
    done = {m: r for m, r in rec["models"].items() if r.get("completed")}
    if len(done) >= 3:
        ref = [r["ref"] for r in done.values()]
        rec["criteria_automata"] = {}
        for q in ("shadowgen", "shadowgen_bounded", "singleton"):
            x = np.array([r[q] for r in done.values()])
            d = np.abs(x - np.array(ref))
            rec["criteria_automata"][q] = {"mae": float(d.mean()), "max_abs_dev": float(d.max()),
                                           "spearman": float(stats.spearmanr(x, ref).statistic) if np.std(x) > 0 else None}
        p = os.path.join(CB_DIR, f"resub_{dkey}_{split}.json")
        if os.path.exists(p):
            rs = json.load(open(p, encoding="utf-8"))["miners"]
            rows = {m: {"ref": rs[m]["ref"], "shadowgen": rs[m]["score"], "shadowgen_bounded": rs[m]["score_bounded"],
                        "singleton": rs[m]["resub_singleton"]} for m in SIX}
            rows.update(done)
            ref = [r["ref"] for r in rows.values()]
            rec["criteria_extended"] = {"n_models": len(rows), **{q: criteria([r[q] for r in rows.values()], ref)
                                                                  for q in ("shadowgen", "shadowgen_bounded", "singleton")}}
    rec["seconds"] = time.time() - t0
    with open(os.path.join(OUT_DIR, f"graded_{dkey}_{split}.json"), "w", encoding="utf-8") as fp:
        json.dump(rec, fp, indent=1)


def summarize():
    L = ["# Graded readings on the k-window automata (alignment fitness, unit costs)", "",
         "| log | split | model | states | reference | ShadowGen | bounded | singleton | seconds |", "|---|---|---|---|---|---|---|---|---|"]
    C = ["", "## Criteria", "", "| log | split | set | n | ShadowGen MAE / max dev / Spearman | bounded | singleton |", "|---|---|---|---|---|---|---|"]
    for k in ("D1", "D2", "D3", "D4", "D5"):
        for s in ("temporal", "random"):
            p = os.path.join(OUT_DIR, f"graded_{k}_{s}.json")
            if not os.path.exists(p):
                continue
            r = json.load(open(p, encoding="utf-8"))
            for i, (m, x) in enumerate(r["models"].items()):
                head = f"| {r['log'] if i == 0 else ''} | {s if i == 0 else ''} | {m} | {x['n_states']} |"
                if x.get("completed"):
                    cf = " (closed form)" if x.get("method", "A*") != "A*" else ""
                    L.append(f"{head} {x['ref']:.3f} | {x['shadowgen']:.3f} | {x['shadowgen_bounded']:.3f} | 1.000 | {x['seconds']:.0f}{cf} |")
                else:
                    L.append(f"{head} not completed ({x['reason']}) | | | | {x['seconds']:.0f} |")
            if r.get("sample"):
                errs = [abs(x["strict_ref_sample"] - x["strict_ref"]) for x in r["models"].values() if x.get("completed")]
                errs += [abs(x["strict_shadowgen_sample"] - x["strict_shadowgen"]) for x in r["models"].values() if x.get("completed")]
                L.append(f"| | | sample of {r['sample']} unseen cases and {r['sample']} shadow traces; strict reading on the sample "
                         f"against the full one: max abs diff {max(errs):.3f} | | | | | | |" if errs else "| | | sample, no model completed | | | | | | |")
            if "check_A_inf_vs_T_all" in r:
                L.append(f"| | | check A_inf - T_all | | " + " | ".join(f"{v:+.4f}" for v in r["check_A_inf_vs_T_all"].values()) + " | | |")
            ca = r.get("criteria_automata")
            if ca:
                n = sum(1 for x in r["models"].values() if x.get("completed"))
                cell = lambda c: f"{c['mae']:.3f} / {c['max_abs_dev']:.3f}" + (f" / {c['spearman']:.2f}" if c.get("spearman") is not None else "")  # noqa: E731
                C.append(f"| {r['log']} | {s} | automata | {n} | {cell(ca['shadowgen'])} | {cell(ca['shadowgen_bounded'])} | {cell(ca['singleton'])} |")
            ce = r.get("criteria_extended")
            if ce:
                cell = lambda c: f"{c['mae']:.3f} / {c['max_abs_dev']:.3f} / {c['spearman']:.2f}"  # noqa: E731
                C.append(f"| {r['log']} | {s} | six nets + automata | {ce['n_models']} | {cell(ce['shadowgen'])} | {cell(ce['shadowgen_bounded'])} | {cell(ce['singleton'])} |")
    open(os.path.join(OUT_DIR, "summary_graded.md"), "w", encoding="utf-8").write("\n".join(L + C) + "\n")
    print("\n".join(L + C))


def main():
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
