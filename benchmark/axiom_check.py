"""
axiom_check.py: ShadowGen (M1g, HybridGen v2.6 MLE) against the
generalization propositions of van der Aalst (2018, "Relating process
models and event logs: 21 conformance propositions").

Tests
  sanity  plain ShadowGen score (graded + acceptance, K=5) for all cached
          models, compared with the stored M1g means in results/configs/
  T1      GenPro8   model accepting everything (Flower) scores 1
  T2      GenPro1   language superset cannot lower generalization
  T3      BehPro    language-equivalent nets with different structure
                    must score the same (trie vs trace net; reduced vs
                    original Inductive_Strict)
  T4      GenPro4-7 log duplication l^k, k in {2, 5}
  T5      GenPro2-3 log extension with fitting / non-fitting traces

Usage (from the repo root, PYTHONHASHSEED=0 set before the interpreter starts):
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/axiom_check.py --dataset D1
  PYTHONHASHSEED=0 env/Scripts/python.exe benchmark/axiom_check.py --dataset D2 \
      --rediscover Alpha+ --force

Outputs (never touches results/configs/):
  benchmark/results/axiom_check/axiom_check_<key>.json
  benchmark/results/axiom_check/summary.md   (rebuilt from all JSON files)

Every score uses the benchmark protocol: random.seed(42), np.random.seed(42),
then K=5 consecutive generate_shadow_log draws (theta=1000, N=6, tau=5,
weighting mle), token replay of each draw, mean over draws, population std.
The draws depend only on the log, so every model is scored on the same
draws of a given log (as in the benchmark, where every cell restarts from
seed 42). Replay runs in one worker process with a wall-clock budget; the
worker keeps every net it has seen, so all scores of a net within a run
use the same Python objects (pm4py token replay breaks ties between
equally labelled enabled transitions by set iteration order, i.e. by
object id, so the trace net's score depends on the process that scores it).
"""
import os
import sys
import json
import time
import copy
import random
import argparse
import platform
import traceback
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FuturesTimeout

import multiprocessing as mp
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "benchmark"))

import pm4py  # noqa: E402
from pm4py.objects.log.obj import EventLog, Trace, Event  # noqa: E402
from pm4py.objects.petri_net.obj import PetriNet, Marking  # noqa: E402
from pm4py.objects.petri_net.utils import petri_utils, reduction  # noqa: E402
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay  # noqa: E402

from datasets import DATASETS  # noqa: E402
from run_m1_family import MINERS  # noqa: E402
from HybridGen.algorithm import load_algorithm  # noqa: E402

# ── Benchmark protocol constants (run_m1_family.py, METHODS["M1g"]) ─────────
SEED = 42
THETA = 1000          # shadow traces per draw
K_DRAWS = 5           # draws (iterations)
MAX_N = 6             # context bound N
TAU = 5               # support threshold
WEIGHTING = "mle"
ALGO_VERSION = "v26"
GEN_KW = dict(num_traces=THETA, safe_threshold=TAU, max_n=MAX_N,
              successor_weighting=WEIGHTING)

PLAYOUT_SEED = 1042   # T5 fitting extension (pm4py basic play-out)
RANDOM_SEED = 2042    # T5 non-fitting extension (uniform random sequences)
DRIFT_RUNS = 3        # fresh processes for the trace-net tie-break drift

MODEL_NAMES = ["Trace_Filtered", "Alpha", "Alpha+", "Heuristics",
               "Heuristics_Strict", "Inductive_Strict", "Inductive_Infrequent",
               "Flower"]
REAL_MODELS = [m for m in MODEL_NAMES if m != "Flower"]

SANITY_TOL = 0.03
TRACE_TOL = 0.05      # Trace_Filtered only: pm4py token replay tie-break drift (see T3(a) drift measurement)
OUT_DIR_DEFAULT = os.path.join(ROOT, "benchmark", "results", "axiom_check")
CONFIG_DIR = os.path.join(ROOT, "benchmark", "results", "configs")
MODEL_DIR = os.path.join(ROOT, "benchmark", "models")

ACT = "concept:name"


# ── Basic helpers ───────────────────────────────────────────────────────────
def seqs_of(log):
    return [tuple(e[ACT] for e in t) for t in log]


def log_from_seqs(seqs, prefix="t"):
    log = EventLog()
    for i, s in enumerate(seqs):
        tr = Trace(attributes={ACT: f"{prefix}_{i}"})
        for a in s:
            tr.append(Event({ACT: a}))
        log.append(tr)
    return log


def log_stats(log):
    seqs = seqs_of(log)
    lens = [len(s) for s in seqs]
    return {
        "n_traces": len(seqs),
        "n_variants": len(set(seqs)),
        "alphabet_size": len(set(a for s in seqs for a in s)),
        "mean_len": float(np.mean(lens)),
        "max_len": int(max(lens)),
    }


def load_log(key):
    path = os.path.join(ROOT, DATASETS[key]["log_path"])
    log = pm4py.read_xes(path)
    return pm4py.convert_to_event_log(log)


def net_size(net):
    silent = sum(1 for t in net.transitions if t.label is None)
    return {"places": len(net.places), "transitions": len(net.transitions),
            "silent": silent, "arcs": len(net.arcs)}


def duplicate_place_names(net):
    c = Counter(str(p.name) for p in net.places)
    return {n: k for n, k in c.items() if k > 1}


def load_models(key, log, rediscover=()):
    """Cached PNML models; names in `rediscover` are discovered in memory instead."""
    models, info = {}, {}
    for mn in MODEL_NAMES:
        path = os.path.join(MODEL_DIR, key, f"{mn}.pnml")
        cached = pm4py.read_pnml(path)
        dup = duplicate_place_names(cached[0])
        rec = {"source": "cache", "path": os.path.relpath(path, ROOT).replace("\\", "/"),
               "size": net_size(cached[0]), "duplicate_place_names": dup}
        if mn in rediscover:
            random.seed(SEED)
            np.random.seed(SEED)
            fresh = MINERS[mn](log)
            rec.update({"source": "rediscovered (run_m1_family.MINERS)",
                        "size": net_size(fresh[0]),
                        "duplicate_place_names": duplicate_place_names(fresh[0]),
                        "cached_size": net_size(cached[0])})
            models[mn] = fresh
        else:
            models[mn] = cached
        info[mn] = rec
    return models, info


def load_stored_m1g(dname):
    stored = {}
    for mn in MODEL_NAMES:
        p = os.path.join(CONFIG_DIR, f"{dname}__{mn}__M1g.json")
        if os.path.exists(p):
            with open(p) as f:
                d = json.load(f)
            r = d["results"]
            stored[mn] = {"mean": r["mean"], "std": r["std"],
                          "gen_accept": r.get("gen_accept"),
                          "gen_accept_std": r.get("gen_accept_std"),
                          "parameters": d.get("parameters"),
                          "timestamp": d.get("timestamp")}
    return stored


# ── Shadow log draws (generator side, main process) ─────────────────────────
_ALGO = None


def algo():
    global _ALGO
    if _ALGO is None:
        _ALGO = load_algorithm(ALGO_VERSION)
    return _ALGO


def draw_shadow_logs(log, k=K_DRAWS, seed=SEED):
    """K draws with the benchmark seeding; returns a dict with plain sequences."""
    random.seed(seed)
    np.random.seed(seed)
    t0 = time.time()
    draws, flags, dups, truncs, cap = [], [], 0, 0, None
    for _ in range(k):
        sl, mf, dk, tr, cap = algo().generate_shadow_log(log, **GEN_KW)
        draws.append(seqs_of(sl))
        flags.append(list(mf))
        dups += dk
        truncs += tr
    return {
        "draws": draws, "flags": flags, "k": k, "seed": seed,
        "duplicates_kept": dups, "truncated": truncs, "max_trace_length_used": cap,
        "mutation_share_per_draw": [float(np.mean(f)) for f in flags],
        "gen_time_s": time.time() - t0,
    }


# ── Replay worker (child process) ───────────────────────────────────────────
_MODELS = {}   # worker-global: key -> (net, im, fm), same objects for the whole run


def _replay_seqs(seqs, net, im, fm):
    log = log_from_seqs(seqs, "r")
    params = {token_replay.Variants.TOKEN_REPLAY.value.Parameters.SHOW_PROGRESS_BAR: False}
    replayed = token_replay.apply(log, net, im, fm, parameters=params)
    fit = [float(r["trace_fitness"]) for r in replayed]
    acc = [bool(r.get("trace_is_fit", r["trace_fitness"] >= 1.0)) for r in replayed]
    return fit, acc


def _worker(draws, key, model):
    if model is not None:
        _MODELS[key] = model
    net, im, fm = _MODELS[key]
    return [_replay_seqs(seqs, net, im, fm) for seqs in draws]


class Scorer:
    """Runs token replay in one worker process with a wall-clock budget."""

    def __init__(self, timeout_s):
        self.timeout = timeout_s
        self.ctx = mp.get_context("spawn")
        self.ex = None
        self.sent = set()
        self.restarts = 0
        self._start()

    def _start(self):
        self.ex = ProcessPoolExecutor(max_workers=1, mp_context=self.ctx)
        self.sent = set()

    def restart(self):
        """Fresh worker process (new object ids, hence new replay tie-breaks)."""
        try:
            for p in list(self.ex._processes.values()):
                p.terminate()
        except Exception:
            pass
        try:
            self.ex.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass
        self.restarts += 1
        self._start()

    def close(self):
        try:
            self.ex.shutdown(wait=True)
        except Exception:
            pass

    def replay(self, draws, key, model, label=""):
        """draws: list of sequence lists. Returns (per_draw[(fit, acc)], runtime, timeout?)."""
        t0 = time.time()
        payload = None if key in self.sent else model
        fut = self.ex.submit(_worker, draws, key, payload)
        try:
            res = fut.result(timeout=self.timeout)
            self.sent.add(key)
            return res, time.time() - t0, False
        except FuturesTimeout:
            print(f"      TIMEOUT ({self.timeout}s) on {label}", flush=True)
            self.restart()
            return None, time.time() - t0, True

    def score(self, shadow, key, model, label=""):
        """Benchmark score of a model on the shadow draws (both readings)."""
        res, rt, to = self.replay(shadow["draws"], key, model, label)
        if to:
            return {"timeout": True, "runtime_s": rt, "mean": None, "std": None,
                    "accept_mean": None, "accept_std": None, "raw": None,
                    "raw_accept": None, "k": shadow["k"], "model_key": key}
        graded = [float(np.mean(f)) for f, _ in res]
        accept = [float(np.mean(a)) for _, a in res]
        mut = []
        for (f, a), flags in zip(res, shadow["flags"]):
            m = [x for x, fl in zip(f, flags) if fl]
            mut.append(float(np.mean(m)) if m else None)
        return {
            "timeout": False, "runtime_s": rt, "k": shadow["k"], "model_key": key,
            "mean": float(np.mean(graded)), "std": float(np.std(graded)),
            "accept_mean": float(np.mean(accept)), "accept_std": float(np.std(accept)),
            "raw": graded, "raw_accept": accept,
            "mutated_fitness_per_draw": mut,
            "_per_trace": res,   # stripped before JSON
        }

    def fit_share(self, seqs, key, model, label=""):
        """Share of sequences replayed perfectly (trace_is_fit) + the fit vector."""
        res, rt, to = self.replay([seqs], key, model, label)
        if to:
            return None, None, rt
        fit, acc = res[0]
        return float(np.mean(acc)), acc, rt


# ── Verdicts ────────────────────────────────────────────────────────────────
def verdict_ge(d, sd):
    """Proposition requires d >= 0 (d = score that must be larger minus the other)."""
    if d == 0:
        return "holds"
    if abs(d) <= 2 * sd:
        return "inconclusive (within 2 sd)"
    return "holds" if d > 0 else "violated"


def verdict_eq(d, sd):
    if d == 0:
        return "holds"
    if abs(d) <= 2 * sd:
        return "inconclusive (within 2 sd)"
    return "violated"


def paired_sd(raw_a, raw_b):
    return float(np.std(np.array(raw_a) - np.array(raw_b)))


def unpaired_sd(sd_a, sd_b):
    return float(np.sqrt(sd_a ** 2 + sd_b ** 2))


def strip(score):
    return {k: v for k, v in score.items() if not k.startswith("_")}


def compare(sa, sb, relation, paired):
    """Compare score dicts; d = sa - sb. relation '>=' means sa >= sb required."""
    out = {}
    for reading, key, raw, sdk in (("graded", "mean", "raw", "std"),
                                   ("accept", "accept_mean", "raw_accept", "accept_std")):
        if sa.get("timeout") or sb.get("timeout"):
            out[reading] = {"d": None, "sd": None, "verdict": "timeout"}
            continue
        d = sa[key] - sb[key]
        sd = paired_sd(sa[raw], sb[raw]) if paired else unpaired_sd(sa[sdk], sb[sdk])
        v = verdict_ge(d, sd) if relation == ">=" else verdict_eq(d, sd)
        out[reading] = {"d": d, "sd": sd, "verdict": v}
    return out


# ── Net constructions for T3 ────────────────────────────────────────────────
def trace_net_variants(net, im, fm):
    """Paths of the shipped trace net (source place -> ... -> sink place)."""
    s = list(im.keys())[0]
    e = list(fm.keys())[0]
    variants = []
    for arc in s.out_arcs:
        tr = arc.target
        seq = []
        while True:
            seq.append(tr.label)
            outs = list(tr.out_arcs)
            if len(outs) != 1:
                raise ValueError("trace net: transition with != 1 outgoing arc")
            p = outs[0].target
            if p is e:
                break
            outs_p = list(p.out_arcs)
            if len(outs_p) != 1:
                raise ValueError("trace net: place with != 1 outgoing arc")
            tr = outs_p[0].target
        variants.append(tuple(seq))
    return variants


def top_k_variants(log, k=50):
    vc = {}
    for t in log:
        key = tuple(x[ACT] for x in t)
        vc[key] = vc.get(key, 0) + 1
    return sorted(vc, key=vc.get, reverse=True)[:k], vc


class _TrieNode:
    __slots__ = ("children", "end")

    def __init__(self):
        self.children = {}
        self.end = False


def build_trie_net(variants):
    """Prefix-merged net whose language is exactly the given variants."""
    root = _TrieNode()
    for v in variants:
        node = root
        for a in v:
            node = node.children.setdefault(a, _TrieNode())
        node.end = True
    net = PetriNet("Trace_Trie")
    src, sink = PetriNet.Place("src"), PetriNet.Place("sink")
    net.places.update([src, sink])
    counter = {"t": 0, "p": 0, "tau": 0, "ends": 0}

    def build(place, node):
        for act, child in node.children.items():
            tr = PetriNet.Transition(f"t_{counter['t']}", act)
            counter["t"] += 1
            net.transitions.add(tr)
            petri_utils.add_arc_from_to(place, tr, net)
            if child.children:
                p = PetriNet.Place(f"p_{counter['p']}")
                counter["p"] += 1
                net.places.add(p)
                petri_utils.add_arc_from_to(tr, p, net)
                if child.end:
                    tau = PetriNet.Transition(f"tau_{counter['tau']}", None)
                    counter["tau"] += 1
                    net.transitions.add(tau)
                    petri_utils.add_arc_from_to(p, tau, net)
                    petri_utils.add_arc_from_to(tau, sink, net)
                    counter["ends"] += 1
                build(p, child)
            else:
                petri_utils.add_arc_from_to(tr, sink, net)
                counter["ends"] += 1

    build(src, root)
    return net, Marking({src: 1}), Marking({sink: 1}), counter


def reduced_copy(model):
    net, im, fm = copy.deepcopy(model)
    reduction.apply_simple_reduction(net)
    ok = all(p in net.places for p in im) and all(p in net.places for p in fm)
    return (net, im, fm), ok


# ── Tests ───────────────────────────────────────────────────────────────────
def run_sanity(scorer, shadow, models, stored):
    print("\n[sanity] plain ShadowGen scores vs stored M1g", flush=True)
    base, rows, worst = {}, [], 0.0
    for mn in MODEL_NAMES:
        s = scorer.score(shadow, mn, models[mn], f"sanity/{mn}")
        base[mn] = s
        st = stored.get(mn)
        row = {"model": mn, "mean": s["mean"], "std": s["std"],
               "accept_mean": s["accept_mean"], "accept_std": s["accept_std"],
               "runtime_s": s["runtime_s"], "timeout": s["timeout"],
               "stored_mean": st["mean"] if st else None,
               "stored_std": st["std"] if st else None,
               "stored_accept": st["gen_accept"] if st else None}
        tol = TRACE_TOL if mn == "Trace_Filtered" else SANITY_TOL
        row["tolerance"] = tol
        if st and not s["timeout"]:
            row["diff_mean"] = s["mean"] - st["mean"]
            row["diff_accept"] = (s["accept_mean"] - st["gen_accept"]
                                  if st["gen_accept"] is not None else None)
            row["within_tolerance"] = max(abs(row["diff_mean"]), abs(row["diff_accept"] or 0.0)) <= tol
            if mn != "Trace_Filtered":
                worst = max(worst, abs(row["diff_mean"]), abs(row["diff_accept"] or 0.0))
        rows.append(row)
        print(f"  {mn:22s} graded {s['mean']:.4f}+-{s['std']:.4f}  accept {s['accept_mean']:.4f}+-{s['accept_std']:.4f}"
              f"  stored {row['stored_mean']}/{row['stored_accept']}  diff {row.get('diff_mean')}"
              f"  ({s['runtime_s']:.1f}s)", flush=True)
    passed = all(r.get("within_tolerance", True) for r in rows)
    return base, {"rows": rows, "worst_abs_diff_excluding_trace": worst, "tolerance": SANITY_TOL,
                  "trace_tolerance": TRACE_TOL, "passed": passed}


def run_t1(base):
    s = base["Flower"]
    out = {}
    for reading, key, sdk in (("graded", "mean", "std"), ("accept", "accept_mean", "accept_std")):
        d = s[key] - 1.0
        out[reading] = {"score": s[key], "sd": s[sdk], "d": d, "verdict": verdict_eq(d, s[sdk])}
    return {"model": "Flower", "readings": out}


def run_t2(scorer, base, models):
    print("\n[T2] GenPro1 language superset", flush=True)
    pairs = []
    for mn in REAL_MODELS:
        c = compare(base["Flower"], base[mn], ">=", paired=True)
        pairs.append({"m1": mn, "m2": "Flower", "inclusion": "every model <= Flower (by construction)",
                      "gen_m1": strip(base[mn]), "gen_m2": strip(base["Flower"]), "cmp": c})
    tf_vars = trace_net_variants(*models["Trace_Filtered"])
    share, acc, rt = scorer.fit_share(tf_vars, "Inductive_Strict", models["Inductive_Strict"], "T2/variants-on-IndS")
    unfit = [i for i, a in enumerate(acc) if not a] if acc is not None else None
    check = {"n_variants": len(tf_vars), "fit_share_on_Inductive_Strict": share,
             "unfit_variant_indices": unfit,
             "unfit_variants": [list(tf_vars[i]) for i in unfit] if unfit else [],
             "runtime_s": rt}
    if acc is not None and all(acc):
        c = compare(base["Inductive_Strict"], base["Trace_Filtered"], ">=", paired=True)
        pairs.append({"m1": "Trace_Filtered", "m2": "Inductive_Strict",
                      "inclusion": "all 50 trace-net variants replay perfectly on Inductive_Strict",
                      "gen_m1": strip(base["Trace_Filtered"]), "gen_m2": strip(base["Inductive_Strict"]),
                      "cmp": c})
        print("  Trace_Filtered <= Inductive_Strict: inclusion verified (50/50 variants fit)", flush=True)
    else:
        print(f"  Trace_Filtered <= Inductive_Strict: SKIPPED, unfit variants {unfit}", flush=True)
    for p in pairs:
        print(f"  {p['m1']:22s} -> {p['m2']:18s} graded d={p['cmp']['graded']['d']:+.4f} sd={p['cmp']['graded']['sd']:.4f} {p['cmp']['graded']['verdict']}"
              f" | accept d={p['cmp']['accept']['d']:+.4f} sd={p['cmp']['accept']['sd']:.4f} {p['cmp']['accept']['verdict']}", flush=True)
    return {"pairs": pairs, "inclusion_check_TF_in_IndS": check}


def _acc_identity(sa, sb):
    """Per-trace acceptance identity on shared draws; lists the differing traces."""
    if sa.get("timeout") or sb.get("timeout"):
        return None
    diffs, n, where = 0, 0, []
    for di, ((fa, aa), (fb, ab)) in enumerate(zip(sa["_per_trace"], sb["_per_trace"])):
        for ti, (x, y) in enumerate(zip(aa, ab)):
            if x != y:
                diffs += 1
                where.append({"draw": di, "trace": ti, "accepted_by_A": x, "accepted_by_B": y})
        n += len(aa)
    return {"n_traces": n, "n_acceptance_differences": diffs, "identical": diffs == 0,
            "differences": where[:20]}


def shuffled_copy(model, rng):
    """Structurally identical net whose places, transitions and arcs are created
    in a random order (different object ids, hence different set iteration order)."""
    net, im, fm = model
    new = PetriNet(net.name)
    pmap, tmap = {}, {}
    places = list(net.places); rng.shuffle(places)
    trans = list(net.transitions); rng.shuffle(trans)
    arcs = list(net.arcs); rng.shuffle(arcs)
    for p in places:
        q = PetriNet.Place(p.name); new.places.add(q); pmap[p] = q
    for t in trans:
        u = PetriNet.Transition(t.name, t.label); new.transitions.add(u); tmap[t] = u
    for a in arcs:
        src = pmap.get(a.source) or tmap.get(a.source)
        dst = pmap.get(a.target) or tmap.get(a.target)
        petri_utils.add_arc_from_to(src, dst, new, weight=a.weight)
    return new, Marking({pmap[p]: c for p, c in im.items()}), Marking({pmap[p]: c for p, c in fm.items()})


def _drift(timeout, shadow, key, model, runs):
    """Score shuffled copies of the same net on the same draws, each in a fresh process."""
    rng = random.Random(7)
    means, accepts = [], []
    for r in range(runs):
        copy_model = shuffled_copy(model, rng)
        sc = Scorer(timeout)
        try:
            s = sc.score(shadow, f"{key}#drift{r}", copy_model, f"drift/{key}/{r}")
        finally:
            sc.close()
        means.append(s["mean"])
        accepts.append(s["accept_mean"])
    return {"runs": runs, "method": "shuffled object-creation order, fresh process per run",
            "graded_means": means, "graded_spread": float(max(means) - min(means)),
            "accept_means": accepts}


def run_t3(scorer, base, shadow, models, log, timeout):
    print("\n[T3] BehPro language-equivalent nets", flush=True)
    out = {}
    # (a) shipped trace net vs trie
    tf = models["Trace_Filtered"]
    tf_vars = trace_net_variants(*tf)
    top50, vc = top_k_variants(log, 50)
    trie_net, trie_im, trie_fm, counter = build_trie_net(tf_vars)
    trie = (trie_net, trie_im, trie_fm)
    v_on_tf = scorer.fit_share(tf_vars, "Trace_Filtered", tf, "T3a/variants-on-TF")
    v_on_trie = scorer.fit_share(tf_vars, "Trace_Trie", trie, "T3a/variants-on-trie")
    s_trie = scorer.score(shadow, "Trace_Trie", trie, "T3a/trie")
    ident = _acc_identity(base["Trace_Filtered"], s_trie)
    c = compare(s_trie, base["Trace_Filtered"], "==", paired=True)
    # diagnostics: labels absent from the trace net are ignored by token replay
    net_labels = set(t.label for t in trie_net.transitions if t.label is not None)
    log_labels = set(a for s in seqs_of(log) for a in s)
    absent = sorted(log_labels - net_labels)
    n_absent = sum(1 for d in shadow["draws"] for s in d if any(a in absent for a in s))
    diff_detail = []
    if ident:
        vs = set(tf_vars)
        for w in ident["differences"]:
            s = shadow["draws"][w["draw"]][w["trace"]]
            pref = [len(v) for v in vs if len(v) < len(s) and s[:len(v)] == v]
            diff_detail.append({"draw": w["draw"], "trace_index": w["trace"],
                                "accepted_by_A": w["accepted_by_A"], "accepted_by_B": w["accepted_by_B"],
                                "len": len(s), "in_variants": s in vs,
                                "variant_prefix_lengths": sorted(pref),
                                "has_label_absent_from_net": any(a in absent for a in s),
                                "sequence": list(s)})
    equiv_ok = bool(ident and ident["identical"])
    print(f"  (a) trie {net_size(trie_net)} vs shipped {net_size(tf[0])}; "
          f"variants fit shipped={v_on_tf[0]} trie={v_on_trie[0]}; shadow acceptance identical={ident and ident['identical']}", flush=True)
    print(f"      graded trie {s_trie['mean']:.4f} vs shipped {base['Trace_Filtered']['mean']:.4f} d={c['graded']['d']:+.4f} sd={c['graded']['sd']:.4f} {c['graded']['verdict']}", flush=True)
    print(f"      drift measurement ({DRIFT_RUNS} fresh processes) ...", flush=True)
    drift_tf = _drift(timeout, shadow, "Trace_Filtered", tf, DRIFT_RUNS)
    drift_trie = _drift(timeout, shadow, "Trace_Trie", trie, DRIFT_RUNS)
    print(f"      shipped graded means {['%.4f' % m for m in drift_tf['graded_means']]} spread {drift_tf['graded_spread']:.4f}; "
          f"trie {['%.4f' % m for m in drift_trie['graded_means']]} spread {drift_trie['graded_spread']:.4f}", flush=True)
    out["a_trace_vs_trie"] = {
        "variants_in_shipped_net": len(tf_vars),
        "shipped_variants_equal_top50_of_log": set(tf_vars) == set(top50),
        "trie_size": {**net_size(trie_net), "end_paths": counter["ends"]},
        "shipped_size": net_size(tf[0]),
        "variants_fit_on_shipped": v_on_tf[0], "variants_fit_on_trie": v_on_trie[0],
        "labels_absent_from_trace_net": absent,
        "shadow_traces_with_absent_label": n_absent,
        "acceptance_identity_on_shadow": {**ident, "differences": diff_detail} if ident else None,
        "equivalence_check_passed": equiv_ok,
        "gen_shipped": strip(base["Trace_Filtered"]), "gen_trie": strip(s_trie),
        "cmp_trie_minus_shipped": c,
        "tie_break_drift": {"shipped": drift_tf, "trie": drift_trie},
    }
    # (b) Inductive_Strict vs reduced copy
    red, mk_ok = reduced_copy(models["Inductive_Strict"])
    log_seqs = seqs_of(log)
    sh_o, acc_o, _ = scorer.fit_share(log_seqs, "Inductive_Strict", models["Inductive_Strict"], "T3b/log-on-IndS")
    sh_r, acc_r, _ = scorer.fit_share(log_seqs, "Inductive_Strict_reduced", red, "T3b/log-on-reduced")
    log_ident = (sum(1 for x, y in zip(acc_o, acc_r) if x != y) if acc_o and acc_r else None)
    s_red = scorer.score(shadow, "Inductive_Strict_reduced", red, "T3b/reduced")
    ident_b = _acc_identity(base["Inductive_Strict"], s_red)
    cb = compare(s_red, base["Inductive_Strict"], "==", paired=True)
    equiv_b = bool(ident_b and ident_b["identical"])
    out["b_inductive_vs_reduced"] = {
        "original_size": net_size(models["Inductive_Strict"][0]), "reduced_size": net_size(red[0]),
        "reduction_changed_net": net_size(models["Inductive_Strict"][0]) != net_size(red[0]),
        "markings_preserved": mk_ok,
        "log_fit_share_original": sh_o, "log_fit_share_reduced": sh_r,
        "log_acceptance_differences": log_ident,
        "acceptance_identity_on_shadow": ident_b,
        "equivalence_check_passed": equiv_b,
        "gen_original": strip(base["Inductive_Strict"]), "gen_reduced": strip(s_red),
        "cmp_reduced_minus_original": cb,
    }
    print(f"  (b) reduced {net_size(red[0])} vs original {net_size(models['Inductive_Strict'][0])}; "
          f"log acceptance diffs={log_ident}; shadow acceptance identical={ident_b and ident_b['identical']}", flush=True)
    print(f"      graded reduced {s_red['mean']:.4f} vs original {base['Inductive_Strict']['mean']:.4f} d={cb['graded']['d']:+.4f} sd={cb['graded']['sd']:.4f} {cb['graded']['verdict']}", flush=True)
    return out


def classify(fit_share):
    if fit_share == 1.0:
        return "all fit", "GenPro4", ">="
    if fit_share == 0.0:
        return "none fit", "GenPro5", "<="
    if fit_share > 0.5:
        return "majority fit", "GenPro6", ">="
    if fit_share < 0.5:
        return "majority non-fit", "GenPro7", "<="
    return "tie (50%)", None, None


def run_t4(scorer, base, shadow, models, log):
    print("\n[T4] GenPro4-7 log duplication", flush=True)
    log_seqs = seqs_of(log)
    shares = {}
    for mn in MODEL_NAMES:
        sh, _, _ = scorer.fit_share(log_seqs, mn, models[mn], f"T4/fit-share/{mn}")
        shares[mn] = sh
    out = {"fit_share_of_log": shares, "base_mutation_share_per_draw": shadow["mutation_share_per_draw"],
           "k": {}}
    for k in (2, 5):
        dup = EventLog()
        for t in log:
            for _ in range(k):
                dup.append(copy.deepcopy(t))
        sh_k = draw_shadow_logs(dup)
        print(f"  k={k}: {len(dup)} traces; mutation share per draw {['%.3f' % m for m in sh_k['mutation_share_per_draw']]}"
              f" (base {['%.3f' % m for m in shadow['mutation_share_per_draw']]}); dup_kept={sh_k['duplicates_kept']} trunc={sh_k['truncated']}", flush=True)
        cells = []
        for mn in MODEL_NAMES:
            s = scorer.score(sh_k, mn, models[mn], f"T4/k{k}/{mn}")
            cls, prop, rel = classify(shares[mn])
            cell = {"model": mn, "fit_share": shares[mn], "class": cls, "proposition": prop,
                    "relation": f"gen(l^k) {rel} gen(l)" if rel else None,
                    "gen_lk": strip(s), "gen_l": strip(base[mn])}
            if rel == ">=":
                cell["cmp"] = compare(s, base[mn], ">=", paired=False)
            elif rel == "<=":
                cell["cmp"] = compare(base[mn], s, ">=", paired=False)
            else:
                cell["cmp"] = None
            cells.append(cell)
            cg = cell["cmp"]["graded"] if cell["cmp"] else None
            ca = cell["cmp"]["accept"] if cell["cmp"] else None
            print(f"    {mn:22s} fit_share={shares[mn]:.3f} {cls:16s} {prop or '-':8s} "
                  f"graded {base[mn]['mean']:.4f}->{s['mean']:.4f} {cg['verdict'] if cg else '-'} | "
                  f"accept {base[mn]['accept_mean']:.4f}->{s['accept_mean']:.4f} {ca['verdict'] if ca else '-'}", flush=True)
        out["k"][str(k)] = {"n_traces": len(dup), "shadow": {kk: v for kk, v in sh_k.items() if kk not in ("draws", "flags")},
                            "cells": cells}
    return out


def playout_fitting(scorer, key, model, n_target, max_len, seed, label, max_batches=4):
    """Play-out traces that replay perfectly; oversample in batches and filter."""
    random.seed(seed)
    net, im, fm = model
    n_gen = max(5 * n_target, 50)
    kept, generated, n_fit, batches = [], 0, 0, 0
    while len(kept) < n_target and batches < max_batches:
        batches += 1
        po = pm4py.play_out(net, im, fm, parameters={"noTraces": n_gen, "maxTraceLength": max_len})
        seqs = [s for s in seqs_of(po) if len(s) > 0]
        generated += len(seqs)
        if not seqs:
            continue
        share, acc, _ = scorer.fit_share(seqs, key, model, label)
        fit = [s for s, a in zip(seqs, acc) if a]
        n_fit += len(fit)
        kept.extend(fit)
    kept = kept[:n_target]
    return kept, {"generated": generated, "fit": n_fit, "kept": len(kept), "batches": batches,
                  "mean_len_kept": float(np.mean([len(s) for s in kept])) if kept else None}


def random_nonfitting(scorer, key, model, n_target, alphabet, length, seed, label):
    rng = random.Random(seed)
    kept, attempts, generated = [], 0, 0
    while len(kept) < n_target and attempts < 50:
        attempts += 1
        batch = [tuple(rng.choice(alphabet) for _ in range(length)) for _ in range(n_target)]
        generated += len(batch)
        share, acc, _ = scorer.fit_share(batch, key, model, label)
        kept.extend(s for s, a in zip(batch, acc) if not a)
    kept = kept[:n_target]
    return kept, {"generated": generated, "kept": len(kept), "length": length, "batches": attempts}


def run_t5(scorer, base, shadow, models, log):
    print("\n[T5] GenPro2-3 log extension", flush=True)
    log_seqs = seqs_of(log)
    log_set = set(log_seqs)
    n_ext = max(1, int(round(0.1 * len(log_seqs))))
    alphabet = sorted(set(a for s in log_seqs for a in s))
    mean_len = int(round(float(np.mean([len(s) for s in log_seqs]))))
    cap = shadow["max_trace_length_used"]
    out = {"n_extension": n_ext, "alphabet_size": len(alphabet), "random_length": mean_len,
           "playout_seed": PLAYOUT_SEED, "random_seed": RANDOM_SEED, "cells": []}
    for mn in REAL_MODELS:
        cell = {"model": mn}
        fit_seqs, info_f = playout_fitting(scorer, mn, models[mn], n_ext, cap, PLAYOUT_SEED, f"T5/playout/{mn}")
        if fit_seqs:
            vs, _, _ = scorer.fit_share(fit_seqs, mn, models[mn], f"T5/verify-fit/{mn}")
            info_f["verified_fit_share"] = vs
            info_f["share_already_in_log"] = float(np.mean([s in log_set for s in fit_seqs]))
            info_f["distinct_sequences"] = len(set(fit_seqs))
            ext = log_from_seqs(log_seqs + fit_seqs, "lf")
            sh = draw_shadow_logs(ext)
            s = scorer.score(sh, mn, models[mn], f"T5/fit/{mn}")
            cell["fit"] = {"info": info_f, "shadow": {k: v for k, v in sh.items() if k not in ("draws", "flags")},
                           "gen_ext": strip(s), "gen_l": strip(base[mn]),
                           "cmp": compare(s, base[mn], ">=", paired=False)}
        else:
            cell["fit"] = {"info": info_f, "skipped": "no fitting play-out traces"}
        nf_seqs, info_n = random_nonfitting(scorer, mn, models[mn], n_ext, alphabet, mean_len, RANDOM_SEED, f"T5/random/{mn}")
        if nf_seqs:
            vs, _, _ = scorer.fit_share(nf_seqs, mn, models[mn], f"T5/verify-nonfit/{mn}")
            info_n["verified_fit_share"] = vs
            ext = log_from_seqs(log_seqs + nf_seqs, "ln")
            sh = draw_shadow_logs(ext)
            s = scorer.score(sh, mn, models[mn], f"T5/nonfit/{mn}")
            cell["nonfit"] = {"info": info_n, "shadow": {k: v for k, v in sh.items() if k not in ("draws", "flags")},
                              "gen_ext": strip(s), "gen_l": strip(base[mn]),
                              "cmp": compare(base[mn], s, ">=", paired=False)}
        else:
            cell["nonfit"] = {"info": info_n, "skipped": "no non-fitting random traces"}
        out["cells"].append(cell)
        fcmp = cell["fit"].get("cmp")
        ncmp = cell["nonfit"].get("cmp")
        print(f"  {mn:22s} fit: {info_f} -> " +
              (f"graded {base[mn]['mean']:.4f}->{cell['fit']['gen_ext']['mean']:.4f} {fcmp['graded']['verdict']}; accept {base[mn]['accept_mean']:.4f}->{cell['fit']['gen_ext']['accept_mean']:.4f} {fcmp['accept']['verdict']}" if fcmp else "skipped"), flush=True)
        print(f"  {'':22s} nonfit: {info_n} -> " +
              (f"graded {base[mn]['mean']:.4f}->{cell['nonfit']['gen_ext']['mean']:.4f} {ncmp['graded']['verdict']}; accept {base[mn]['accept_mean']:.4f}->{cell['nonfit']['gen_ext']['accept_mean']:.4f} {ncmp['accept']['verdict']}" if ncmp else "skipped"), flush=True)
    return out


# ── Summary (markdown) ──────────────────────────────────────────────────────
def _ms(s, reading):
    if s is None or s.get("timeout"):
        return "timeout"
    if reading == "graded":
        return f"{s['mean']:.4f} ± {s['std']:.4f}"
    return f"{s['accept_mean']:.4f} ± {s['accept_std']:.4f}"


def _cmp_cols(c, reading):
    if not c:
        return "-", "-", "n/a"
    if c[reading]["d"] is None:
        return "-", "-", c[reading]["verdict"]
    return f"{c[reading]['d']:+.4f}", f"{c[reading]['sd']:.4f}", c[reading]["verdict"]


def write_summary(out_dir):
    files = sorted(f for f in os.listdir(out_dir) if f.startswith("axiom_check_") and f.endswith(".json"))
    L = ["# ShadowGen axiom check (van der Aalst 2018 propositions)", "",
         "Scores: ShadowGen M1g (HybridGen v2.6, N=6, tau=5, mle, theta=1000), K=5 draws, mean ± population sd over draws.",
         "Readings: graded = mean token-replay trace fitness of the shadow log; accept = fraction of shadow traces replayed perfectly.",
         "d is oriented so that the proposition requires d >= 0 (or d = 0 for equalities). sd_d is the sd of per-draw differences",
         "when both scores use the same draws (paired), and sqrt(sd1^2 + sd2^2) when the logs differ (unpaired).",
         "Verdict: holds (d in the required direction by more than 2 sd_d, or d = 0), violated (wrong direction by more than 2 sd_d),",
         "inconclusive (|d| <= 2 sd_d, either direction).", ""]
    for fn in files:
        with open(os.path.join(out_dir, fn)) as f:
            R = json.load(f)
        key, dname = R["dataset_key"], R["dataset"]
        L += [f"## {key} {dname}", "",
              f"Log: {R['log']['n_traces']} traces, {R['log']['n_variants']} variants, alphabet {R['log']['alphabet_size']}, "
              f"mean length {R['log']['mean_len']:.1f}, max {R['log']['max_len']}. "
              f"Shadow cap {R['shadow_base']['max_trace_length_used']}, mutation share per draw "
              f"{[round(m, 3) for m in R['shadow_base']['mutation_share_per_draw']]}.", ""]
        notes = R.get("notes", [])
        if notes:
            L += ["Notes:"] + [f"- {n}" for n in notes] + [""]
        if R.get("error"):
            L += ["ERROR during run (see JSON):", "```", R["error"].strip().splitlines()[-1], "```", ""]
        S = R.get("sanity")
        if S:
            L += [f"### Sanity: plain score vs stored M1g (tolerance {S['tolerance']}, Trace_Filtered {S.get('trace_tolerance', S['tolerance'])} "
                  f"for the replay tie-break drift; worst |diff| excluding Trace_Filtered {S.get('worst_abs_diff_excluding_trace', S.get('worst_abs_diff', 0)):.4f}; "
                  f"{'passed' if S['passed'] else 'FAILED'}{', run continued with --force' if R.get('sanity_forced') else ''})", "",
                  "| model | graded (this run) | stored mean | diff | accept (this run) | stored accept | diff | within tol. | time s |",
                  "|---|---|---|---|---|---|---|---|---|"]
            for r in S["rows"]:
                L.append(f"| {r['model']} | {r['mean']:.4f} ± {r['std']:.4f} | {r['stored_mean']:.4f} | {r.get('diff_mean', 0):+.4f} | "
                         f"{r['accept_mean']:.4f} ± {r['accept_std']:.4f} | {r['stored_accept']:.4f} | {r.get('diff_accept', 0):+.4f} | "
                         f"{'yes' if r.get('within_tolerance', True) else 'NO'} ({r.get('tolerance', S['tolerance'])}) | {r['runtime_s']:.1f} |")
            L.append("")
        T = R.get("T1")
        if T:
            L += ["### T1 GenPro8: Flower scores 1", "", "| reading | score | sd | d = score - 1 | verdict |", "|---|---|---|---|---|"]
            for rd in ("graded", "accept"):
                x = T["readings"][rd]
                L.append(f"| {rd} | {x['score']:.4f} | {x['sd']:.4f} | {x['d']:+.4f} | {x['verdict']} |")
            L.append("")
        T = R.get("T2")
        if T:
            chk = T["inclusion_check_TF_in_IndS"]
            L += ["### T2 GenPro1: language superset cannot lower generalization (gen(m2) >= gen(m1), same draws)", "",
                  f"Inclusion check Trace_Filtered in Inductive_Strict: {chk['fit_share_on_Inductive_Strict']} of {chk['n_variants']} variants fit"
                  + (f"; unfit variants {chk['unfit_variant_indices']} (pair skipped)" if chk['unfit_variant_indices'] else "; pair included") + ".", "",
                  "| m1 (subset) | m2 (superset) | graded m1 | graded m2 | d | sd_d | verdict | accept m1 | accept m2 | d | sd_d | verdict |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for p in T["pairs"]:
                g = _cmp_cols(p["cmp"], "graded"); a = _cmp_cols(p["cmp"], "accept")
                L.append(f"| {p['m1']} | {p['m2']} | {_ms(p['gen_m1'], 'graded')} | {_ms(p['gen_m2'], 'graded')} | {g[0]} | {g[1]} | {g[2]} | "
                         f"{_ms(p['gen_m1'], 'accept')} | {_ms(p['gen_m2'], 'accept')} | {a[0]} | {a[1]} | {a[2]} |")
            L.append("")
        T = R.get("T3")
        if T:
            L += ["### T3 BehPro: language-equivalent nets score the same (same draws)", "",
                  "| pair | net A | net B | equivalence check (shadow acceptance identical) | accept A | accept B | graded A | graded B | d | sd_d | verdict (graded) |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
            a = T["a_trace_vs_trie"]
            ida = a["acceptance_identity_on_shadow"]
            chk = (f"{'passed' if a['equivalence_check_passed'] else 'FAILED'}: "
                   f"{ida['n_acceptance_differences'] if ida else '-'} of {ida['n_traces'] if ida else '-'} traces differ")
            g = _cmp_cols(a["cmp_trie_minus_shipped"], "graded")
            L.append(f"| (a) | Trace_Filtered {a['shipped_size']['places']}p/{a['shipped_size']['transitions']}t | "
                     f"trie {a['trie_size']['places']}p/{a['trie_size']['transitions']}t ({a['trie_size']['silent']} silent) | {chk} | "
                     f"{_ms(a['gen_shipped'], 'accept')} | {_ms(a['gen_trie'], 'accept')} | {_ms(a['gen_shipped'], 'graded')} | {_ms(a['gen_trie'], 'graded')} | "
                     f"{g[0]} | {g[1]} | {g[2] if a['equivalence_check_passed'] else 'not a BehPro result (equivalence check failed); raw verdict ' + g[2]} |")
            b = T["b_inductive_vs_reduced"]
            idb = b["acceptance_identity_on_shadow"]
            chk = (f"{'passed' if b['equivalence_check_passed'] else 'FAILED'}: "
                   f"{idb['n_acceptance_differences'] if idb else '-'} of {idb['n_traces'] if idb else '-'} traces differ; "
                   f"log acceptance diffs {b['log_acceptance_differences']}")
            g = _cmp_cols(b["cmp_reduced_minus_original"], "graded")
            L.append(f"| (b) | Inductive_Strict {b['original_size']['places']}p/{b['original_size']['transitions']}t ({b['original_size']['silent']} silent) | "
                     f"reduced {b['reduced_size']['places']}p/{b['reduced_size']['transitions']}t ({b['reduced_size']['silent']} silent) | {chk} | "
                     f"{_ms(b['gen_original'], 'accept')} | {_ms(b['gen_reduced'], 'accept')} | {_ms(b['gen_original'], 'graded')} | {_ms(b['gen_reduced'], 'graded')} | "
                     f"{g[0]} | {g[1]} | {g[2] if b['equivalence_check_passed'] else 'not a BehPro result (equivalence check failed); raw verdict ' + g[2]} |")
            L.append("")
            dr = a.get("tie_break_drift")
            L += [f"T3(a) diagnostics: the shipped trace net replays {a['variants_fit_on_shipped']:.2f} of its own 50 variants perfectly, the trie {a['variants_fit_on_trie']:.2f} "
                  f"(pm4py token replay picks the first enabled transition with the matching label in set order, i.e. by object id). "
                  + (f"Scores of the shipped net on the same draws for {dr['shipped']['runs']} copies with shuffled object-creation order, each in a fresh process: "
                     f"{[round(m, 4) for m in dr['shipped']['graded_means']]} (spread {dr['shipped']['graded_spread']:.4f}); "
                     f"trie: {[round(m, 4) for m in dr['trie']['graded_means']]} (spread {dr['trie']['graded_spread']:.4f}). " if dr else "")
                  + f"Labels absent from the trace net (ignored by token replay): {a['labels_absent_from_trace_net']}; "
                  f"{a['shadow_traces_with_absent_label']} shadow traces contain one."]
            if ida and ida["differences"]:
                for w in ida["differences"][:5]:
                    L.append(f"- differing trace: draw {w['draw']}, index {w.get('trace_index', '?')}, length {w['len']}, accepted by shipped={w['accepted_by_A']}, trie={w['accepted_by_B']}, "
                             f"variant prefixes of length {w['variant_prefix_lengths']}, contains absent label: {w['has_label_absent_from_net']}; "
                             f"sequence {w.get('sequence', w.get('trace'))}")
            if not b["reduction_changed_net"]:
                L.append(f"T3(b): apply_simple_reduction left Inductive_Strict unchanged ({b['original_size']['places']}p/{b['original_size']['transitions']}t), so pair (b) compares a deep copy with the original.")
            L.append("")
        T = R.get("T4")
        if T:
            for k, blk in T["k"].items():
                L += [f"### T4 GenPro4-7: duplication l^{k} ({blk['n_traces']} traces; mutation share per draw "
                      f"{[round(m, 3) for m in blk['shadow']['mutation_share_per_draw']]} vs base "
                      f"{[round(m, 3) for m in T['base_mutation_share_per_draw']]})", "",
                      "| model | fit share of l | class | prop. | required | graded l | graded l^k | d | sd_d | verdict | accept l | accept l^k | d | sd_d | verdict |",
                      "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
                for c in blk["cells"]:
                    g = _cmp_cols(c["cmp"], "graded"); a = _cmp_cols(c["cmp"], "accept")
                    L.append(f"| {c['model']} | {c['fit_share']:.3f} | {c['class']} | {c['proposition'] or '-'} | {c['relation'] or '-'} | "
                             f"{_ms(c['gen_l'], 'graded')} | {_ms(c['gen_lk'], 'graded')} | {g[0]} | {g[1]} | {g[2]} | "
                             f"{_ms(c['gen_l'], 'accept')} | {_ms(c['gen_lk'], 'accept')} | {a[0]} | {a[1]} | {a[2]} |")
                L.append("")
        T = R.get("T5")
        if T:
            L += [f"### T5 GenPro2 (l + fitting, gen >= gen(l)) and GenPro3 (l + non-fitting, gen <= gen(l)); extension size {T['n_extension']} "
                  f"(10% of |l|), random length {T['random_length']}, alphabet {T['alphabet_size']}", "",
                  "| model | ext | traces kept | in log | graded l | graded l+ext | d | sd_d | verdict | accept l | accept l+ext | d | sd_d | verdict |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for c in T["cells"]:
                for ext in ("fit", "nonfit"):
                    e = c[ext]
                    info = e["info"]
                    if e.get("skipped"):
                        L.append(f"| {c['model']} | {ext} | {info.get('kept', 0)} | - | - | skipped: {e['skipped']} ({info.get('generated', 0)} generated) | | | | | | | | |")
                        continue
                    g = _cmp_cols(e["cmp"], "graded"); a = _cmp_cols(e["cmp"], "accept")
                    inlog = f"{info['share_already_in_log']:.2f}" if "share_already_in_log" in info else "-"
                    L.append(f"| {c['model']} | {ext} | {info['kept']} | {inlog} | {_ms(e['gen_l'], 'graded')} | {_ms(e['gen_ext'], 'graded')} | {g[0]} | {g[1]} | {g[2]} | "
                             f"{_ms(e['gen_l'], 'accept')} | {_ms(e['gen_ext'], 'accept')} | {a[0]} | {a[1]} | {a[2]} |")
            L.append("")
        tm = R.get("timings", {})
        L += [f"Timings: {', '.join(f'{k} {v:.0f} s' for k, v in tm.items())}.", ""]
    with open(os.path.join(out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, choices=["D1", "D2"])
    ap.add_argument("--out", default=OUT_DIR_DEFAULT)
    ap.add_argument("--tests", nargs="+", default=["sanity", "T1", "T2", "T3", "T4", "T5"])
    ap.add_argument("--timeout", type=int, default=600, help="wall-clock budget per score (s)")
    ap.add_argument("--force", action="store_true", help="continue past a failed sanity check")
    ap.add_argument("--rediscover", nargs="*", default=[], choices=MODEL_NAMES,
                    help="discover these models in memory (run_m1_family.MINERS) instead of the PNML cache")
    ap.add_argument("--summary-only", action="store_true", help="rebuild summary.md from the JSON files and exit")
    args = ap.parse_args()

    if args.summary_only:
        write_summary(args.out)
        print(f"rebuilt {os.path.join(args.out, 'summary.md')}")
        return 0

    if os.environ.get("PYTHONHASHSEED") != "0":
        print("WARNING: PYTHONHASHSEED is not 0 in this interpreter; set/dict iteration order may differ from the benchmark.")

    key = args.dataset
    dname = DATASETS[key]["name"]
    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, f"axiom_check_{key}.json")

    t_all = time.time()
    print(f"=== axiom_check {key} {dname} ===", flush=True)
    log = load_log(key)
    models, model_info = load_models(key, log, rediscover=args.rediscover)
    stored = load_stored_m1g(dname)
    stats = log_stats(log)
    print(f"log: {stats}", flush=True)
    notes = []
    for mn in MODEL_NAMES:
        mi = model_info[mn]
        print(f"  {mn:22s} {mi['size']} {mi['source']}"
              + (f" DUPLICATE PLACE NAMES {mi['duplicate_place_names']}" if mi["duplicate_place_names"] else ""), flush=True)
        if mi["source"] != "cache":
            notes.append(f"{mn}: {mi['source']} instead of {mi['path']} (cached size {mi['cached_size']}, "
                         f"duplicate place names in cached net: {duplicate_place_names(pm4py.read_pnml(os.path.join(ROOT, mi['path']))[0])}).")
        elif mi["duplicate_place_names"]:
            notes.append(f"{mn}: cached net has duplicate place names {mi['duplicate_place_names']} (PNML ids collide on round trip).")

    R = {"dataset_key": key, "dataset": dname, "log": stats,
         "parameters": {"algorithm_version": "v2.6", "method": "M1g", "max_n": MAX_N, "safe_threshold": TAU,
                        "successor_weighting": WEIGHTING, "num_shadow_traces": THETA, "iterations": K_DRAWS,
                        "seed": SEED, "timeout_s": args.timeout, "sanity_tolerance": SANITY_TOL,
                        "playout_seed": PLAYOUT_SEED, "random_seed": RANDOM_SEED, "drift_runs": DRIFT_RUNS},
         "command": " ".join(sys.argv),
         "environment": {"python": sys.version.split()[0], "pm4py": pm4py.__version__,
                         "platform": platform.platform(), "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED")},
         "models": model_info, "stored_m1g": stored, "notes": notes, "timings": {}}

    scorer = Scorer(args.timeout)
    base = {}
    try:
        t0 = time.time()
        shadow = draw_shadow_logs(log)
        R["shadow_base"] = {k: v for k, v in shadow.items() if k not in ("draws", "flags")}
        print(f"base draws: cap {shadow['max_trace_length_used']}, mutation share {['%.3f' % m for m in shadow['mutation_share_per_draw']]}, "
              f"dup_kept {shadow['duplicates_kept']}, trunc {shadow['truncated']} ({shadow['gen_time_s']:.1f}s)", flush=True)

        base, san = run_sanity(scorer, shadow, models, stored)
        R["sanity"] = san
        R["timings"]["sanity"] = time.time() - t0
        print(f"  sanity worst |diff| excluding Trace_Filtered = {san['worst_abs_diff_excluding_trace']:.4f} "
              f"({'passed' if san['passed'] else 'FAILED'})", flush=True)
        if not san["passed"]:
            R["sanity_forced"] = bool(args.force)
            if not args.force:
                with open(out_path, "w") as f:
                    json.dump(R, f, indent=2)
                print("Sanity check failed; stopping (use --force to continue).")
                return 2
            bad = [f"{r['model']} ({r.get('diff_mean', 0):+.4f})" for r in san["rows"] if not r.get("within_tolerance", True)]
            notes.append(f"Sanity check failed for {', '.join(bad)}; run continued with --force.")

        if "T1" in args.tests:
            t0 = time.time(); R["T1"] = run_t1(base); R["timings"]["T1"] = time.time() - t0
            print(f"\n[T1] Flower graded {R['T1']['readings']['graded']['verdict']}, accept {R['T1']['readings']['accept']['verdict']}", flush=True)
        if "T2" in args.tests:
            t0 = time.time(); R["T2"] = run_t2(scorer, base, models); R["timings"]["T2"] = time.time() - t0
        if "T3" in args.tests:
            t0 = time.time(); R["T3"] = run_t3(scorer, base, shadow, models, log, args.timeout); R["timings"]["T3"] = time.time() - t0
        if "T4" in args.tests:
            t0 = time.time(); R["T4"] = run_t4(scorer, base, shadow, models, log); R["timings"]["T4"] = time.time() - t0
        if "T5" in args.tests:
            t0 = time.time(); R["T5"] = run_t5(scorer, base, shadow, models, log); R["timings"]["T5"] = time.time() - t0
    except Exception:
        R["error"] = traceback.format_exc()
        print(R["error"])
    finally:
        scorer.close()

    R["worker_restarts"] = scorer.restarts
    R["timings"]["total"] = time.time() - t_all
    R["base_scores"] = {mn: strip(s) for mn, s in base.items()}
    with open(out_path, "w") as f:
        json.dump(R, f, indent=2)
    write_summary(args.out)
    print(f"\nwrote {out_path} and summary.md ({R['timings']['total']:.0f}s total)")
    return 1 if "error" in R else 0


if __name__ == "__main__":
    sys.exit(main())
