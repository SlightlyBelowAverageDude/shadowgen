# ShadowGen axiom check (van der Aalst 2018 propositions)

Scores: ShadowGen M1g (HybridGen v2.6, N=6, tau=5, mle, theta=1000), K=5 draws, mean ± population sd over draws.
Readings: graded = mean token-replay trace fitness of the shadow log; accept = fraction of shadow traces replayed perfectly.
d is oriented so that the proposition requires d >= 0 (or d = 0 for equalities). sd_d is the sd of per-draw differences
when both scores use the same draws (paired), and sqrt(sd1^2 + sd2^2) when the logs differ (unpaired).
Verdict: holds (d in the required direction by more than 2 sd_d, or d = 0), violated (wrong direction by more than 2 sd_d),
inconclusive (|d| <= 2 sd_d, either direction).

## D1 Sepsis

Log: 1050 traces, 846 variants, alphabet 16, mean length 14.5, max 185. Shadow cap 370, mutation share per draw [0.505, 0.572, 0.544, 0.546, 0.541].

### Sanity: plain score vs stored M1g (tolerance 0.03, Trace_Filtered 0.05 for the replay tie-break drift; worst |diff| excluding Trace_Filtered 0.0001; passed)

| model | graded (this run) | stored mean | diff | accept (this run) | stored accept | diff | within tol. | time s |
|---|---|---|---|---|---|---|---|---|
| Trace_Filtered | 0.5877 ± 0.0033 | 0.5687 | +0.0190 | 0.0000 ± 0.0000 | 0.0000 | +0.0000 | yes (0.05) | 24.5 |
| Alpha | 0.2724 ± 0.0039 | 0.2724 | +0.0000 | 0.0002 ± 0.0004 | 0.0002 | +0.0000 | yes (0.03) | 2.8 |
| Alpha+ | 0.7591 ± 0.0053 | 0.7591 | +0.0000 | 0.0000 ± 0.0000 | 0.0000 | +0.0000 | yes (0.03) | 3.1 |
| Heuristics | 0.8787 ± 0.0017 | 0.8787 | -0.0001 | 0.0010 ± 0.0013 | 0.0010 | +0.0000 | yes (0.03) | 7.1 |
| Heuristics_Strict | 0.9174 ± 0.0015 | 0.9174 | +0.0000 | 0.0078 ± 0.0034 | 0.0078 | +0.0000 | yes (0.03) | 6.5 |
| Inductive_Strict | 0.9838 ± 0.0020 | 0.9838 | +0.0000 | 0.7444 ± 0.0220 | 0.7444 | +0.0000 | yes (0.03) | 6.0 |
| Inductive_Infrequent | 0.9723 ± 0.0019 | 0.9723 | +0.0000 | 0.6436 ± 0.0225 | 0.6436 | +0.0000 | yes (0.03) | 4.6 |
| Flower | 1.0000 ± 0.0000 | 1.0000 | +0.0000 | 1.0000 ± 0.0000 | 1.0000 | +0.0000 | yes (0.03) | 2.6 |

### T1 GenPro8: Flower scores 1

| reading | score | sd | d = score - 1 | verdict |
|---|---|---|---|---|
| graded | 1.0000 | 0.0000 | +0.0000 | holds |
| accept | 1.0000 | 0.0000 | +0.0000 | holds |

### T2 GenPro1: language superset cannot lower generalization (gen(m2) >= gen(m1), same draws)

Inclusion check Trace_Filtered in Inductive_Strict: 1.0 of 50 variants fit; pair included.

| m1 (subset) | m2 (superset) | graded m1 | graded m2 | d | sd_d | verdict | accept m1 | accept m2 | d | sd_d | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Trace_Filtered | Flower | 0.5877 ± 0.0033 | 1.0000 ± 0.0000 | +0.4123 | 0.0033 | holds | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | +1.0000 | 0.0000 | holds |
| Alpha | Flower | 0.2724 ± 0.0039 | 1.0000 ± 0.0000 | +0.7276 | 0.0039 | holds | 0.0002 ± 0.0004 | 1.0000 ± 0.0000 | +0.9998 | 0.0004 | holds |
| Alpha+ | Flower | 0.7591 ± 0.0053 | 1.0000 ± 0.0000 | +0.2409 | 0.0053 | holds | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | +1.0000 | 0.0000 | holds |
| Heuristics | Flower | 0.8787 ± 0.0017 | 1.0000 ± 0.0000 | +0.1213 | 0.0017 | holds | 0.0010 ± 0.0013 | 1.0000 ± 0.0000 | +0.9990 | 0.0013 | holds |
| Heuristics_Strict | Flower | 0.9174 ± 0.0015 | 1.0000 ± 0.0000 | +0.0826 | 0.0015 | holds | 0.0078 ± 0.0034 | 1.0000 ± 0.0000 | +0.9922 | 0.0034 | holds |
| Inductive_Strict | Flower | 0.9838 ± 0.0020 | 1.0000 ± 0.0000 | +0.0162 | 0.0020 | holds | 0.7444 ± 0.0220 | 1.0000 ± 0.0000 | +0.2556 | 0.0220 | holds |
| Inductive_Infrequent | Flower | 0.9723 ± 0.0019 | 1.0000 ± 0.0000 | +0.0277 | 0.0019 | holds | 0.6436 ± 0.0225 | 1.0000 ± 0.0000 | +0.3564 | 0.0225 | holds |
| Trace_Filtered | Inductive_Strict | 0.5877 ± 0.0033 | 0.9838 ± 0.0020 | +0.3961 | 0.0021 | holds | 0.0000 ± 0.0000 | 0.7444 ± 0.0220 | +0.7444 | 0.0220 | holds |

### T3 BehPro: language-equivalent nets score the same (same draws)

| pair | net A | net B | equivalence check (shadow acceptance identical) | accept A | accept B | graded A | graded B | d | sd_d | verdict (graded) |
|---|---|---|---|---|---|---|---|---|---|---|
| (a) | Trace_Filtered 424p/472t | trie 138p/186t (14 silent) | FAILED: 2 of 5000 traces differ | 0.0000 ± 0.0000 | 0.0004 ± 0.0008 | 0.5877 ± 0.0033 | 0.7497 ± 0.0028 | +0.1620 | 0.0015 | not a BehPro result (equivalence check failed); raw verdict violated |
| (b) | Inductive_Strict 39p/50t (34 silent) | reduced 39p/50t (34 silent) | passed: 0 of 5000 traces differ; log acceptance diffs 0 | 0.7444 ± 0.0220 | 0.7444 ± 0.0220 | 0.9838 ± 0.0020 | 0.9838 ± 0.0020 | +0.0000 | 0.0000 | holds |

T3(a) diagnostics: the shipped trace net replays 0.02 of its own 50 variants perfectly, the trie 1.00 (pm4py token replay picks the first enabled transition with the matching label in set order, i.e. by object id). Scores of the shipped net on the same draws for 3 copies with shuffled object-creation order, each in a fresh process: [0.5919, 0.575, 0.5799] (spread 0.0170); trie: [0.7493, 0.7449, 0.7491] (spread 0.0045). Labels absent from the trace net (ignored by token replay): ['Admission IC', 'Release C', 'Release D', 'Release E']; 1428 shadow traces contain one.
- differing trace: draw 3, index 226, length 10, accepted by shipped=False, trie=True, variant prefixes of length [3, 8, 9], contains absent label: True; sequence ['ER Registration', 'ER Triage', 'ER Sepsis Triage', 'Leucocytes', 'LacticAcid', 'CRP', 'IV Liquid', 'IV Antibiotics', 'Admission NC', 'Release C']
- differing trace: draw 3, index 475, length 10, accepted by shipped=False, trie=True, variant prefixes of length [3, 8, 9], contains absent label: True; sequence ['ER Registration', 'ER Triage', 'ER Sepsis Triage', 'Leucocytes', 'LacticAcid', 'CRP', 'IV Liquid', 'IV Antibiotics', 'Admission NC', 'Release C']
T3(b): apply_simple_reduction left Inductive_Strict unchanged (39p/50t), so pair (b) compares a deep copy with the original.

### T4 GenPro4-7: duplication l^2 (2100 traces; mutation share per draw [0.0, 0.0, 0.0, 0.0, 0.0] vs base [0.505, 0.572, 0.544, 0.546, 0.541])

| model | fit share of l | class | prop. | required | graded l | graded l^k | d | sd_d | verdict | accept l | accept l^k | d | sd_d | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trace_Filtered | 0.002 | majority non-fit | GenPro7 | gen(l^k) <= gen(l) | 0.5877 ± 0.0033 | 0.5806 ± 0.0047 | +0.0072 | 0.0057 | inconclusive (within 2 sd) | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Alpha | 0.000 | none fit | GenPro5 | gen(l^k) <= gen(l) | 0.2724 ± 0.0039 | 0.2702 ± 0.0016 | +0.0022 | 0.0043 | inconclusive (within 2 sd) | 0.0002 ± 0.0004 | 0.0012 ± 0.0007 | -0.0010 | 0.0008 | inconclusive (within 2 sd) |
| Alpha+ | 0.000 | none fit | GenPro5 | gen(l^k) <= gen(l) | 0.7591 ± 0.0053 | 0.7832 ± 0.0044 | -0.0241 | 0.0068 | violated | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Heuristics | 0.033 | majority non-fit | GenPro7 | gen(l^k) <= gen(l) | 0.8787 ± 0.0017 | 0.8898 ± 0.0019 | -0.0111 | 0.0025 | violated | 0.0010 ± 0.0013 | 0.0030 ± 0.0021 | -0.0020 | 0.0024 | inconclusive (within 2 sd) |
| Heuristics_Strict | 0.035 | majority non-fit | GenPro7 | gen(l^k) <= gen(l) | 0.9174 ± 0.0015 | 0.9250 ± 0.0016 | -0.0076 | 0.0022 | violated | 0.0078 ± 0.0034 | 0.0072 ± 0.0031 | +0.0006 | 0.0046 | inconclusive (within 2 sd) |
| Inductive_Strict | 1.000 | all fit | GenPro4 | gen(l^k) >= gen(l) | 0.9838 ± 0.0020 | 0.9855 ± 0.0006 | +0.0017 | 0.0021 | inconclusive (within 2 sd) | 0.7444 ± 0.0220 | 0.8412 ± 0.0040 | +0.0968 | 0.0223 | holds |
| Inductive_Infrequent | 0.804 | majority fit | GenPro6 | gen(l^k) >= gen(l) | 0.9723 ± 0.0019 | 0.9772 ± 0.0019 | +0.0049 | 0.0027 | inconclusive (within 2 sd) | 0.6436 ± 0.0225 | 0.7498 ± 0.0138 | +0.1062 | 0.0264 | holds |
| Flower | 1.000 | all fit | GenPro4 | gen(l^k) >= gen(l) | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | holds | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |

### T4 GenPro4-7: duplication l^5 (5250 traces; mutation share per draw [0.0, 0.0, 0.0, 0.0, 0.0] vs base [0.505, 0.572, 0.544, 0.546, 0.541])

| model | fit share of l | class | prop. | required | graded l | graded l^k | d | sd_d | verdict | accept l | accept l^k | d | sd_d | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trace_Filtered | 0.002 | majority non-fit | GenPro7 | gen(l^k) <= gen(l) | 0.5877 ± 0.0033 | 0.5757 ± 0.0045 | +0.0120 | 0.0056 | holds | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Alpha | 0.000 | none fit | GenPro5 | gen(l^k) <= gen(l) | 0.2724 ± 0.0039 | 0.2673 ± 0.0047 | +0.0051 | 0.0061 | inconclusive (within 2 sd) | 0.0002 ± 0.0004 | 0.0004 ± 0.0008 | -0.0002 | 0.0009 | inconclusive (within 2 sd) |
| Alpha+ | 0.000 | none fit | GenPro5 | gen(l^k) <= gen(l) | 0.7591 ± 0.0053 | 0.8011 ± 0.0034 | -0.0420 | 0.0063 | violated | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Heuristics | 0.033 | majority non-fit | GenPro7 | gen(l^k) <= gen(l) | 0.8787 ± 0.0017 | 0.8956 ± 0.0011 | -0.0170 | 0.0020 | violated | 0.0010 ± 0.0013 | 0.0020 ± 0.0018 | -0.0010 | 0.0022 | inconclusive (within 2 sd) |
| Heuristics_Strict | 0.035 | majority non-fit | GenPro7 | gen(l^k) <= gen(l) | 0.9174 ± 0.0015 | 0.9303 ± 0.0017 | -0.0130 | 0.0023 | violated | 0.0078 ± 0.0034 | 0.0068 ± 0.0039 | +0.0010 | 0.0051 | inconclusive (within 2 sd) |
| Inductive_Strict | 1.000 | all fit | GenPro4 | gen(l^k) >= gen(l) | 0.9838 ± 0.0020 | 0.9856 ± 0.0020 | +0.0017 | 0.0028 | inconclusive (within 2 sd) | 0.7444 ± 0.0220 | 0.8702 ± 0.0093 | +0.1258 | 0.0238 | holds |
| Inductive_Infrequent | 0.804 | majority fit | GenPro6 | gen(l^k) >= gen(l) | 0.9723 ± 0.0019 | 0.9812 ± 0.0030 | +0.0088 | 0.0036 | holds | 0.6436 ± 0.0225 | 0.7920 ± 0.0135 | +0.1484 | 0.0262 | holds |
| Flower | 1.000 | all fit | GenPro4 | gen(l^k) >= gen(l) | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | holds | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |

### T5 GenPro2 (l + fitting, gen >= gen(l)) and GenPro3 (l + non-fitting, gen <= gen(l)); extension size 105 (10% of |l|), random length 14, alphabet 16

| model | ext | traces kept | in log | graded l | graded l+ext | d | sd_d | verdict | accept l | accept l+ext | d | sd_d | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trace_Filtered | fit | 48 | 1.00 | 0.5877 ± 0.0033 | 0.5866 ± 0.0037 | -0.0011 | 0.0050 | inconclusive (within 2 sd) | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Trace_Filtered | nonfit | 105 | - | 0.5877 ± 0.0033 | 0.5493 ± 0.0037 | +0.0384 | 0.0050 | holds | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Alpha | fit | 102 | 0.00 | 0.2724 ± 0.0039 | 0.2770 ± 0.0033 | +0.0046 | 0.0051 | inconclusive (within 2 sd) | 0.0002 ± 0.0004 | 0.0000 ± 0.0000 | -0.0002 | 0.0004 | inconclusive (within 2 sd) |
| Alpha | nonfit | 105 | - | 0.2724 ± 0.0039 | 0.2919 ± 0.0011 | -0.0196 | 0.0041 | violated | 0.0002 ± 0.0004 | 0.0004 ± 0.0005 | -0.0002 | 0.0006 | inconclusive (within 2 sd) |
| Alpha+ | fit | 0 | - | - | skipped: no fitting play-out traces (2100 generated) | | | | | | | | |
| Alpha+ | nonfit | 105 | - | 0.7591 ± 0.0053 | 0.6585 ± 0.0051 | +0.1006 | 0.0073 | holds | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Heuristics | fit | 105 | 0.04 | 0.8787 ± 0.0017 | 0.8784 ± 0.0010 | -0.0003 | 0.0020 | inconclusive (within 2 sd) | 0.0010 ± 0.0013 | 0.0010 ± 0.0013 | +0.0000 | 0.0018 | holds |
| Heuristics | nonfit | 105 | - | 0.8787 ± 0.0017 | 0.8350 ± 0.0031 | +0.0436 | 0.0035 | holds | 0.0010 ± 0.0013 | 0.0042 ± 0.0017 | -0.0032 | 0.0021 | inconclusive (within 2 sd) |
| Heuristics_Strict | fit | 105 | 0.04 | 0.9174 ± 0.0015 | 0.9173 ± 0.0006 | -0.0001 | 0.0016 | inconclusive (within 2 sd) | 0.0078 ± 0.0034 | 0.0146 ± 0.0044 | +0.0068 | 0.0055 | inconclusive (within 2 sd) |
| Heuristics_Strict | nonfit | 105 | - | 0.9174 ± 0.0015 | 0.8763 ± 0.0034 | +0.0411 | 0.0037 | holds | 0.0078 ± 0.0034 | 0.0116 ± 0.0017 | -0.0038 | 0.0038 | inconclusive (within 2 sd) |
| Inductive_Strict | fit | 105 | 0.00 | 0.9838 ± 0.0020 | 0.9627 ± 0.0023 | -0.0211 | 0.0030 | violated | 0.7444 ± 0.0220 | 0.5858 ± 0.0184 | -0.1586 | 0.0286 | violated |
| Inductive_Strict | nonfit | 105 | - | 0.9838 ± 0.0020 | 0.9457 ± 0.0029 | +0.0382 | 0.0035 | holds | 0.7444 ± 0.0220 | 0.4948 ± 0.0170 | +0.2496 | 0.0278 | holds |
| Inductive_Infrequent | fit | 105 | 0.00 | 0.9723 ± 0.0019 | 0.9599 ± 0.0029 | -0.0124 | 0.0034 | violated | 0.6436 ± 0.0225 | 0.5640 ± 0.0182 | -0.0796 | 0.0290 | violated |
| Inductive_Infrequent | nonfit | 105 | - | 0.9723 ± 0.0019 | 0.9295 ± 0.0022 | +0.0429 | 0.0029 | holds | 0.6436 ± 0.0225 | 0.4414 ± 0.0138 | +0.2022 | 0.0264 | holds |

Timings: sanity 58 s, T1 0 s, T2 0 s, T3 128 s, T4 124 s, T5 185 s, total 496 s.

## D2 BPI2013_Incidents

Log: 7554 traces, 1511 variants, alphabet 4, mean length 8.7, max 123. Shadow cap 246, mutation share per draw [0.013, 0.012, 0.016, 0.017, 0.016].

Notes:
- Alpha+: rediscovered (run_m1_family.MINERS) instead of benchmark/models/D2/Alpha+.pnml (cached size {'places': 6, 'transitions': 6, 'silent': 2, 'arcs': 10}, duplicate place names in cached net: {"({'artificial_start'}, {'artificial_end'})": 2}).

### Sanity: plain score vs stored M1g (tolerance 0.03, Trace_Filtered 0.05 for the replay tie-break drift; worst |diff| excluding Trace_Filtered 0.0000; passed)

| model | graded (this run) | stored mean | diff | accept (this run) | stored accept | diff | within tol. | time s |
|---|---|---|---|---|---|---|---|---|
| Trace_Filtered | 0.6404 ± 0.0051 | 0.6000 | +0.0404 | 0.0000 ± 0.0000 | 0.0000 | +0.0000 | yes (0.05) | 14.5 |
| Alpha | 0.2572 ± 0.0050 | 0.2572 | +0.0000 | 0.0014 ± 0.0012 | 0.0014 | +0.0000 | yes (0.03) | 1.3 |
| Alpha+ | 0.6301 ± 0.0078 | 0.6301 | +0.0000 | 0.0000 ± 0.0000 | 0.0000 | +0.0000 | yes (0.03) | 1.1 |
| Heuristics | 0.9935 ± 0.0003 | 0.9935 | +0.0000 | 0.8360 ± 0.0068 | 0.8360 | +0.0000 | yes (0.03) | 2.1 |
| Heuristics_Strict | 0.9978 ± 0.0003 | 0.9978 | -0.0000 | 0.9458 ± 0.0074 | 0.9458 | +0.0000 | yes (0.03) | 2.1 |
| Inductive_Strict | 1.0000 ± 0.0000 | 1.0000 | +0.0000 | 0.9984 ± 0.0008 | 0.9984 | +0.0000 | yes (0.03) | 2.6 |
| Inductive_Infrequent | 0.9907 ± 0.0007 | 0.9907 | +0.0000 | 0.8378 ± 0.0088 | 0.8378 | +0.0000 | yes (0.03) | 2.2 |
| Flower | 1.0000 ± 0.0000 | 1.0000 | +0.0000 | 1.0000 ± 0.0000 | 1.0000 | +0.0000 | yes (0.03) | 0.9 |

### T1 GenPro8: Flower scores 1

| reading | score | sd | d = score - 1 | verdict |
|---|---|---|---|---|
| graded | 1.0000 | 0.0000 | +0.0000 | holds |
| accept | 1.0000 | 0.0000 | +0.0000 | holds |

### T2 GenPro1: language superset cannot lower generalization (gen(m2) >= gen(m1), same draws)

Inclusion check Trace_Filtered in Inductive_Strict: 1.0 of 50 variants fit; pair included.

| m1 (subset) | m2 (superset) | graded m1 | graded m2 | d | sd_d | verdict | accept m1 | accept m2 | d | sd_d | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Trace_Filtered | Flower | 0.6404 ± 0.0051 | 1.0000 ± 0.0000 | +0.3596 | 0.0051 | holds | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | +1.0000 | 0.0000 | holds |
| Alpha | Flower | 0.2572 ± 0.0050 | 1.0000 ± 0.0000 | +0.7428 | 0.0050 | holds | 0.0014 ± 0.0012 | 1.0000 ± 0.0000 | +0.9986 | 0.0012 | holds |
| Alpha+ | Flower | 0.6301 ± 0.0078 | 1.0000 ± 0.0000 | +0.3699 | 0.0078 | holds | 0.0000 ± 0.0000 | 1.0000 ± 0.0000 | +1.0000 | 0.0000 | holds |
| Heuristics | Flower | 0.9935 ± 0.0003 | 1.0000 ± 0.0000 | +0.0065 | 0.0003 | holds | 0.8360 ± 0.0068 | 1.0000 ± 0.0000 | +0.1640 | 0.0068 | holds |
| Heuristics_Strict | Flower | 0.9978 ± 0.0003 | 1.0000 ± 0.0000 | +0.0022 | 0.0003 | holds | 0.9458 ± 0.0074 | 1.0000 ± 0.0000 | +0.0542 | 0.0074 | holds |
| Inductive_Strict | Flower | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | inconclusive (within 2 sd) | 0.9984 ± 0.0008 | 1.0000 ± 0.0000 | +0.0016 | 0.0008 | holds |
| Inductive_Infrequent | Flower | 0.9907 ± 0.0007 | 1.0000 ± 0.0000 | +0.0093 | 0.0007 | holds | 0.8378 ± 0.0088 | 1.0000 ± 0.0000 | +0.1622 | 0.0088 | holds |
| Trace_Filtered | Inductive_Strict | 0.6404 ± 0.0051 | 1.0000 ± 0.0000 | +0.3596 | 0.0051 | holds | 0.0000 ± 0.0000 | 0.9984 ± 0.0008 | +0.9984 | 0.0008 | holds |

### T3 BehPro: language-equivalent nets score the same (same draws)

| pair | net A | net B | equivalence check (shadow acceptance identical) | accept A | accept B | graded A | graded B | d | sd_d | verdict (graded) |
|---|---|---|---|---|---|---|---|---|---|---|
| (a) | Trace_Filtered 361p/409t | trie 115p/163t (3 silent) | passed: 0 of 5000 traces differ | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.6404 ± 0.0051 | 0.7855 ± 0.0028 | +0.1451 | 0.0043 | violated |
| (b) | Inductive_Strict 17p/23t (19 silent) | reduced 17p/23t (19 silent) | passed: 0 of 5000 traces differ; log acceptance diffs 0 | 0.9984 ± 0.0008 | 0.9984 ± 0.0008 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |

T3(a) diagnostics: the shipped trace net replays 0.04 of its own 50 variants perfectly, the trie 1.00 (pm4py token replay picks the first enabled transition with the matching label in set order, i.e. by object id). Scores of the shipped net on the same draws for 3 copies with shuffled object-creation order, each in a fresh process: [0.6515, 0.635, 0.6138] (spread 0.0377); trie: [0.7794, 0.795, 0.7884] (spread 0.0156). Labels absent from the trace net (ignored by token replay): ['Unmatched']; 45 shadow traces contain one.
T3(b): apply_simple_reduction left Inductive_Strict unchanged (17p/23t), so pair (b) compares a deep copy with the original.

### T4 GenPro4-7: duplication l^2 (15108 traces; mutation share per draw [0.0, 0.0, 0.0, 0.0, 0.0] vs base [0.013, 0.012, 0.016, 0.017, 0.016])

| model | fit share of l | class | prop. | required | graded l | graded l^k | d | sd_d | verdict | accept l | accept l^k | d | sd_d | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trace_Filtered | 0.006 | majority non-fit | GenPro7 | gen(l^k) <= gen(l) | 0.6404 ± 0.0051 | 0.6397 ± 0.0033 | +0.0007 | 0.0061 | inconclusive (within 2 sd) | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Alpha | 0.000 | majority non-fit | GenPro7 | gen(l^k) <= gen(l) | 0.2572 ± 0.0050 | 0.2579 ± 0.0040 | -0.0007 | 0.0064 | inconclusive (within 2 sd) | 0.0014 ± 0.0012 | 0.0014 ± 0.0012 | +0.0000 | 0.0017 | holds |
| Alpha+ | 0.000 | none fit | GenPro5 | gen(l^k) <= gen(l) | 0.6301 ± 0.0078 | 0.6280 ± 0.0062 | +0.0021 | 0.0100 | inconclusive (within 2 sd) | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Heuristics | 0.928 | majority fit | GenPro6 | gen(l^k) >= gen(l) | 0.9935 ± 0.0003 | 0.9937 ± 0.0004 | +0.0002 | 0.0005 | inconclusive (within 2 sd) | 0.8360 ± 0.0068 | 0.8394 ± 0.0085 | +0.0034 | 0.0109 | inconclusive (within 2 sd) |
| Heuristics_Strict | 0.981 | majority fit | GenPro6 | gen(l^k) >= gen(l) | 0.9978 ± 0.0003 | 0.9980 ± 0.0004 | +0.0002 | 0.0005 | inconclusive (within 2 sd) | 0.9458 ± 0.0074 | 0.9492 ± 0.0111 | +0.0034 | 0.0134 | inconclusive (within 2 sd) |
| Inductive_Strict | 1.000 | all fit | GenPro4 | gen(l^k) >= gen(l) | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | inconclusive (within 2 sd) | 0.9984 ± 0.0008 | 1.0000 ± 0.0000 | +0.0016 | 0.0008 | holds |
| Inductive_Infrequent | 0.931 | majority fit | GenPro6 | gen(l^k) >= gen(l) | 0.9907 ± 0.0007 | 0.9909 ± 0.0008 | +0.0002 | 0.0011 | inconclusive (within 2 sd) | 0.8378 ± 0.0088 | 0.8396 ± 0.0092 | +0.0018 | 0.0127 | inconclusive (within 2 sd) |
| Flower | 1.000 | all fit | GenPro4 | gen(l^k) >= gen(l) | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | holds | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |

### T4 GenPro4-7: duplication l^5 (37770 traces; mutation share per draw [0.0, 0.0, 0.0, 0.0, 0.0] vs base [0.013, 0.012, 0.016, 0.017, 0.016])

| model | fit share of l | class | prop. | required | graded l | graded l^k | d | sd_d | verdict | accept l | accept l^k | d | sd_d | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trace_Filtered | 0.006 | majority non-fit | GenPro7 | gen(l^k) <= gen(l) | 0.6404 ± 0.0051 | 0.6392 ± 0.0041 | +0.0012 | 0.0065 | inconclusive (within 2 sd) | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Alpha | 0.000 | majority non-fit | GenPro7 | gen(l^k) <= gen(l) | 0.2572 ± 0.0050 | 0.2580 ± 0.0049 | -0.0009 | 0.0070 | inconclusive (within 2 sd) | 0.0014 ± 0.0012 | 0.0014 ± 0.0012 | +0.0000 | 0.0017 | holds |
| Alpha+ | 0.000 | none fit | GenPro5 | gen(l^k) <= gen(l) | 0.6301 ± 0.0078 | 0.6279 ± 0.0075 | +0.0022 | 0.0109 | inconclusive (within 2 sd) | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Heuristics | 0.928 | majority fit | GenPro6 | gen(l^k) >= gen(l) | 0.9935 ± 0.0003 | 0.9939 ± 0.0003 | +0.0004 | 0.0004 | inconclusive (within 2 sd) | 0.8360 ± 0.0068 | 0.8410 ± 0.0089 | +0.0050 | 0.0112 | inconclusive (within 2 sd) |
| Heuristics_Strict | 0.981 | majority fit | GenPro6 | gen(l^k) >= gen(l) | 0.9978 ± 0.0003 | 0.9981 ± 0.0004 | +0.0003 | 0.0005 | inconclusive (within 2 sd) | 0.9458 ± 0.0074 | 0.9502 ± 0.0097 | +0.0044 | 0.0123 | inconclusive (within 2 sd) |
| Inductive_Strict | 1.000 | all fit | GenPro4 | gen(l^k) >= gen(l) | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | inconclusive (within 2 sd) | 0.9984 ± 0.0008 | 1.0000 ± 0.0000 | +0.0016 | 0.0008 | holds |
| Inductive_Infrequent | 0.931 | majority fit | GenPro6 | gen(l^k) >= gen(l) | 0.9907 ± 0.0007 | 0.9909 ± 0.0007 | +0.0002 | 0.0010 | inconclusive (within 2 sd) | 0.8378 ± 0.0088 | 0.8402 ± 0.0099 | +0.0024 | 0.0132 | inconclusive (within 2 sd) |
| Flower | 1.000 | all fit | GenPro4 | gen(l^k) >= gen(l) | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | holds | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |

### T5 GenPro2 (l + fitting, gen >= gen(l)) and GenPro3 (l + non-fitting, gen <= gen(l)); extension size 755 (10% of |l|), random length 9, alphabet 4

| model | ext | traces kept | in log | graded l | graded l+ext | d | sd_d | verdict | accept l | accept l+ext | d | sd_d | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trace_Filtered | fit | 622 | 1.00 | 0.6404 ± 0.0051 | 0.6379 ± 0.0038 | -0.0025 | 0.0063 | inconclusive (within 2 sd) | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Trace_Filtered | nonfit | 755 | - | 0.6404 ± 0.0051 | 0.6111 ± 0.0059 | +0.0292 | 0.0078 | holds | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | +0.0000 | 0.0000 | holds |
| Alpha | fit | 755 | 0.16 | 0.2572 ± 0.0050 | 0.2522 ± 0.0098 | -0.0050 | 0.0110 | inconclusive (within 2 sd) | 0.0014 ± 0.0012 | 0.0070 ± 0.0037 | +0.0056 | 0.0039 | inconclusive (within 2 sd) |
| Alpha | nonfit | 755 | - | 0.2572 ± 0.0050 | 0.3107 ± 0.0043 | -0.0535 | 0.0066 | violated | 0.0014 ± 0.0012 | 0.0400 ± 0.0023 | -0.0386 | 0.0026 | violated |
| Alpha+ | fit | 755 | 0.00 | 0.6301 ± 0.0078 | 0.6184 ± 0.0075 | -0.0118 | 0.0109 | inconclusive (within 2 sd) | 0.0000 ± 0.0000 | 0.0332 ± 0.0037 | +0.0332 | 0.0037 | holds |
| Alpha+ | nonfit | 755 | - | 0.6301 ± 0.0078 | 0.6310 ± 0.0043 | -0.0009 | 0.0089 | inconclusive (within 2 sd) | 0.0000 ± 0.0000 | 0.0136 ± 0.0044 | -0.0136 | 0.0044 | violated |
| Heuristics | fit | 755 | 0.20 | 0.9935 ± 0.0003 | 0.9910 ± 0.0003 | -0.0026 | 0.0004 | violated | 0.8360 ± 0.0068 | 0.7740 ± 0.0066 | -0.0620 | 0.0095 | violated |
| Heuristics | nonfit | 755 | - | 0.9935 ± 0.0003 | 0.9611 ± 0.0030 | +0.0324 | 0.0030 | holds | 0.8360 ± 0.0068 | 0.7336 ± 0.0075 | +0.1024 | 0.0101 | holds |
| Heuristics_Strict | fit | 755 | 0.19 | 0.9978 ± 0.0003 | 0.9973 ± 0.0005 | -0.0005 | 0.0006 | inconclusive (within 2 sd) | 0.9458 ± 0.0074 | 0.9326 ± 0.0084 | -0.0132 | 0.0112 | inconclusive (within 2 sd) |
| Heuristics_Strict | nonfit | 755 | - | 0.9978 ± 0.0003 | 0.9785 ± 0.0047 | +0.0193 | 0.0047 | holds | 0.9458 ± 0.0074 | 0.8242 ± 0.0232 | +0.1216 | 0.0244 | holds |
| Inductive_Strict | fit | 755 | 0.30 | 1.0000 ± 0.0000 | 0.9999 ± 0.0000 | -0.0000 | 0.0001 | inconclusive (within 2 sd) | 0.9984 ± 0.0008 | 0.9968 ± 0.0016 | -0.0016 | 0.0018 | inconclusive (within 2 sd) |
| Inductive_Strict | nonfit | 755 | - | 1.0000 ± 0.0000 | 0.9916 ± 0.0005 | +0.0083 | 0.0005 | holds | 0.9984 ± 0.0008 | 0.8954 ± 0.0085 | +0.1030 | 0.0086 | holds |
| Inductive_Infrequent | fit | 755 | 0.54 | 0.9907 ± 0.0007 | 0.9860 ± 0.0003 | -0.0047 | 0.0008 | violated | 0.8378 ± 0.0088 | 0.7578 ± 0.0086 | -0.0800 | 0.0123 | violated |
| Inductive_Infrequent | nonfit | 755 | - | 0.9907 ± 0.0007 | 0.9542 ± 0.0054 | +0.0365 | 0.0054 | holds | 0.8378 ± 0.0088 | 0.6888 ± 0.0219 | +0.1490 | 0.0236 | holds |

Timings: sanity 28 s, T1 0 s, T2 0 s, T3 78 s, T4 68 s, T5 132 s, total 308 s.
