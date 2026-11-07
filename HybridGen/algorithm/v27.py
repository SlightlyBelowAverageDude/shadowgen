import random
import time
from collections import Counter

import numpy as np
import pandas as pd

from pm4py.objects.log.obj import EventLog
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay

from .v26 import generate_shadow_log as _draw_v26

__all__ = ["log_rules", "broken_rules", "generate_shadow_log", "calculate_gen_shadow_stable", "evaluate_miner"]

# =====================================================================
# Generative Behavioral Analysis (v27 - Unseen and rule-conforming probe)
#
# The walk of v26 is unchanged (same draws for the same seed). Two
# changes decide which drawn traces are scored:
#   1. Seen traces are dropped. v26 retries 100 times to draw a trace
#      whose variant is absent from the log and then keeps a seen one.
#      The score is defined on unseen behavior, so v27 scores unseen
#      traces only and reports how many seen traces it dropped.
#   2. Rule filter. A drawn trace is scored only if it keeps every rule
#      that holds in all cases of the log:
#        end        the trace ends in an activity that ends a case
#        count      no activity occurs more often than in any case
#        mandatory  every activity present in all cases is present
#        df         every directly-follows pair occurs in the log
#        ef         every eventually-follows pair occurs in the log
#        length     the trace is no longer than the longest case
#        implies    if every case with a contains b, a comes with b
#        balance    count(a) - count(b) stays inside the range seen
#      Scoring the conforming subset equals redrawing until a
#      conforming trace appears; only the sample size differs.
# The scored set can be smaller than num_traces and can be empty. An
# empty set gives no score (None).
# =====================================================================


def _variants(event_log):
    """Set of activity sequences (tuples) of the log, the empty case included."""
    if isinstance(event_log, pd.DataFrame):
        return {tuple(g["concept:name"]) for _, g in event_log.groupby("case:concept:name")}
    return {tuple(e["concept:name"] for e in trace) for trace in event_log}


def log_rules(seqs):
    """Rules that hold in every sequence of seqs (one tuple per case or per variant)."""
    seqs = {tuple(s) for s in seqs}
    alphabet = sorted({a for s in seqs for a in s})
    ends, max_count, always, df, ef, max_len = set(), Counter(), None, set(), set(), 0
    not_implied, balance = set(), {}
    for s in seqs:
        c = Counter(s)
        ends.add(s[-1] if s else None)
        max_len = max(max_len, len(s))
        for a, n in c.items():
            if n > max_count[a]:
                max_count[a] = n
        always = set(c) if always is None else always & set(c)
        df.update(zip(s, s[1:]))
        seen = set()
        for a in s:
            for b in seen:
                ef.add((b, a))
            seen.add(a)
        for a in c:
            for b in alphabet:
                if b not in c:
                    not_implied.add((a, b))
        for i, a in enumerate(alphabet):
            for b in alphabet[i + 1:]:
                d = c.get(a, 0) - c.get(b, 0)
                lo, hi = balance.get((a, b), (d, d))
                balance[(a, b)] = (min(lo, d), max(hi, d))
    implies = {(a, b) for a in alphabet for b in alphabet if a != b and (a, b) not in not_implied}
    return {"ends": ends, "max_count": max_count, "always": always or set(), "df": df, "ef": ef,
            "max_len": max_len, "implies": implies, "balance": balance}


def broken_rules(seq, rules):
    """Names of the rules the sequence breaks (empty list: the sequence conforms)."""
    c = Counter(seq)
    out = []
    if (seq[-1] if seq else None) not in rules["ends"]:
        out.append("end")
    if any(n > rules["max_count"].get(a, 0) for a, n in c.items()):
        out.append("count")
    if not rules["always"] <= set(c):
        out.append("mandatory")
    if any(p not in rules["df"] for p in zip(seq, seq[1:])):
        out.append("df")
    seen = set()
    for a in seq:
        if any((b, a) not in rules["ef"] for b in seen):
            out.append("ef")
            break
        seen.add(a)
    if len(seq) > rules["max_len"]:
        out.append("length")
    if any(a in c and b not in c for a, b in rules["implies"]):
        out.append("implies")
    if any(not lo <= c.get(a, 0) - c.get(b, 0) <= hi for (a, b), (lo, hi) in rules["balance"].items()):
        out.append("balance")
    return out


def generate_shadow_log(event_log, num_traces=1000, max_trace_length=None,
                        safe_threshold=5, max_n=6, successor_weighting="log"):
    """
    Draws num_traces traces with the v26 walk and keeps the unseen, rule-conforming ones.
    Returns (shadow_log, mutation_flags, info); info counts what was drawn, dropped and kept.
    """
    drawn, flags, duplicates, truncated, cap_used = _draw_v26(
        event_log, num_traces=num_traces, max_trace_length=max_trace_length,
        safe_threshold=safe_threshold, max_n=max_n, successor_weighting=successor_weighting)
    variants = _variants(event_log)
    rules = log_rules(variants)

    shadow_log, kept_flags = EventLog(), []
    seen_dropped, rule_dropped, broken = 0, 0, Counter()
    for trace, flag in zip(drawn, flags):
        seq = tuple(e["concept:name"] for e in trace)
        if seq in variants:
            seen_dropped += 1
            continue
        b = broken_rules(seq, rules)
        if b:
            rule_dropped += 1
            broken.update(b)
            continue
        shadow_log.append(trace)
        kept_flags.append(flag)

    info = {"drawn": len(drawn), "seen_dropped": seen_dropped, "rule_dropped": rule_dropped,
            "scored": len(shadow_log), "broken_rules": dict(broken),
            "v26_duplicates_kept": duplicates, "truncated": truncated, "max_trace_length_used": cap_used}
    return shadow_log, kept_flags, info


def calculate_gen_shadow_stable(event_log, net, im, fm, num_traces, iterations=5,
                                safe_threshold=5, max_n=6, successor_weighting="log"):
    """Runs generation iteratively, evaluates fitness AND acceptance on the scored traces."""
    scores, accept_scores = [], []
    regular_scores, mutated_scores, mutation_counts = [], [], []
    accept_regular, accept_mutated = [], []
    scored_counts, seen_dropped, rule_dropped, truncated_total = [], 0, 0, 0
    broken, cap_used = Counter(), None

    for _ in range(iterations):
        shadow_log, mutation_flags, info = generate_shadow_log(
            event_log, num_traces=num_traces, safe_threshold=safe_threshold,
            max_n=max_n, successor_weighting=successor_weighting
        )
        scored_counts.append(info["scored"])
        seen_dropped += info["seen_dropped"]
        rule_dropped += info["rule_dropped"]
        truncated_total += info["truncated"]
        broken.update(info["broken_rules"])
        cap_used = info["max_trace_length_used"]
        if not len(shadow_log):
            continue
        replayed = token_replay.apply(shadow_log, net, im, fm)
        trace_fitnesses = [res['trace_fitness'] for res in replayed]
        trace_accepts = [1.0 if res.get('trace_is_fit', res['trace_fitness'] >= 1.0) else 0.0
                         for res in replayed]

        scores.append(sum(trace_fitnesses) / len(trace_fitnesses))
        accept_scores.append(sum(trace_accepts) / len(trace_accepts))

        reg_fits = [f for f, flag in zip(trace_fitnesses, mutation_flags) if not flag]
        mut_fits = [f for f, flag in zip(trace_fitnesses, mutation_flags) if flag]
        reg_acc = [a for a, flag in zip(trace_accepts, mutation_flags) if not flag]
        mut_acc = [a for a, flag in zip(trace_accepts, mutation_flags) if flag]

        mutation_counts.append(len(mut_fits))
        regular_scores.append(np.mean(reg_fits) if reg_fits else 0.0)
        mutated_scores.append(np.mean(mut_fits) if mut_fits else 0.0)
        accept_regular.append(np.mean(reg_acc) if reg_acc else 0.0)
        accept_mutated.append(np.mean(mut_acc) if mut_acc else 0.0)

    def mean(v):
        return float(np.mean(v)) if v else None

    def std(v):
        return float(np.std(v)) if v else None

    return {
        "mean": mean(scores),
        "std": std(scores),
        "raw_scores": scores,
        "accept_mean": mean(accept_scores),
        "accept_std": std(accept_scores),
        "raw_accepts": accept_scores,
        "reg_mean": mean(regular_scores),
        "reg_std": std(regular_scores),
        "mut_mean": mean(mutated_scores),
        "mut_std": std(mutated_scores),
        "accept_reg_mean": mean(accept_regular),
        "accept_mut_mean": mean(accept_mutated),
        "mutation_counts": mutation_counts,
        # Probe accounting
        "scored_counts": scored_counts,
        "iterations_without_score": iterations - len(scores),
        "seen_dropped": seen_dropped,
        "rule_dropped": rule_dropped,
        "broken_rules": dict(broken),
        "duplicates_kept": 0,
        "truncated": truncated_total,
        "max_trace_length_used": cap_used,
    }


def evaluate_miner(event_log, miner_name, miner_fn, w=0.5, num_shadow_traces=1000,
                   iterations=5, seed=42, max_n=6, successor_weighting="log"):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    print(f"       Evaluating {miner_name} (v27, weighting={successor_weighting})...")
    t0 = time.time()

    net, im, fm = miner_fn(event_log)
    r = calculate_gen_shadow_stable(
        event_log, net, im, fm, num_shadow_traces, iterations,
        safe_threshold=5, max_n=max_n, successor_weighting=successor_weighting
    )

    runtime = time.time() - t0

    return {
        "miner": miner_name,
        "gen_struct": 0.0,
        "gen_shadow_mean": r["mean"],
        "gen_shadow_std": r["std"],
        "gen_shadow_raw_iterations": list(r["raw_scores"]),
        "gen_total": r["mean"],
        # Acceptance: fraction of perfectly replayed shadow traces.
        "gen_accept": r["accept_mean"],
        "gen_accept_std": r["accept_std"],
        # Openness profile (fitness and acceptance, regular vs mutated)
        "gen_shadow_regular": r["reg_mean"],
        "gen_shadow_regular_std": r["reg_std"],
        "gen_shadow_mutated": r["mut_mean"],
        "gen_shadow_mutated_std": r["mut_std"],
        "gen_accept_regular": r["accept_reg_mean"],
        "gen_accept_mutated": r["accept_mut_mean"],
        "mutated_traces_per_iteration": r["mutation_counts"],
        # Probe accounting
        "scored_traces_per_iteration": r["scored_counts"],
        "iterations_without_score": r["iterations_without_score"],
        "seen_dropped": r["seen_dropped"],
        "rule_dropped": r["rule_dropped"],
        "broken_rules": r["broken_rules"],
        "duplicates_kept": r["duplicates_kept"],
        "truncated_traces": r["truncated"],
        "max_trace_length_used": r["max_trace_length_used"],
        "successor_weighting": successor_weighting,
        "runtime_s": runtime
    }

# Register to the library
from . import register_algorithm
register_algorithm("v2.7")
