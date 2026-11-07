# ShadowGen readings on the synthetic known-system study (synth_unseen_check.json, reference: unseen)

Protocol: seed 42; one 1,000-trace draw; N=6, tau=5, mle; v2.6 core; pm4py 2.7.22.2. 78 systems regenerated from the stored seeds (trees match the stored study on 78 of 78); training log and fresh sample resampled, so this is a replication under resampling, not a reproduction.

Unseen share of the fresh sample: median 0.15, min 0.00, max 0.82; systems with an empty unseen part: 4.

## Replication against the stored study (per log-model pair, |fresh - stored|, full reference)

| quantity | n | median | p90 | max |
|---|---|---|---|---|
| graded | 624 | 0.0031 | 0.0317 | 0.5710 |
| true_recall | 624 | 0.0000 | 0.0196 | 0.6035 |
| true_precision | 624 | 0.0000 | 0.0185 | 0.7404 |
| m2 | 624 | 0.0010 | 0.0100 | 0.1693 |

Graded reading, per-system Pearson with full true recall over the six miners, discriminating systems (sd >= 0.05): fresh median 0.899 (n=61, positive 0.92); stored median 0.904 (n=61, positive 0.90).

## Both readings against the unseen reference and true precision

Pooled r over all pairs; centred r after subtracting each system's mean; per-system medians over systems with at least 3 models. The partial correlation asks whether the score still tracks true precision once the reference recall is held fixed.

### discriminating systems, six discovered nets

| reading | reference | n pairs | pooled r | centred r | per-system median r | positive | per-system median rho | median MAE | partial r with precision given reference | per-system median r with precision |
|---|---|---|---|---|---|---|---|---|---|---|
| graded | true_recall_unseen | 414 | 0.754 | 0.781 | 0.997 | 0.94 | 0.955 | 0.030 | 0.062 (centred 0.022) | 0.711 (positive 0.88) |
| strict | true_recall_strict_unseen | 432 | 0.742 | 0.804 | 0.998 | 0.96 | 1.000 | 0.122 | 0.089 (centred -0.046) | 0.493 (positive 0.86) |
| strict | true_recall_unseen | 414 | 0.395 | 0.514 | 0.709 | 0.94 | 0.840 | 0.582 | 0.253 (centred 0.092) | 0.489 (positive 0.86) |

### all systems, six discovered nets

| reading | reference | n pairs | pooled r | centred r | per-system median r | positive | per-system median rho | median MAE | partial r with precision given reference | per-system median r with precision |
|---|---|---|---|---|---|---|---|---|---|---|
| graded | true_recall_unseen | 444 | 0.761 | 0.782 | 0.998 | 0.94 | 0.970 | 0.026 | 0.072 (centred 0.024) | 0.714 (positive 0.89) |
| strict | true_recall_strict_unseen | 444 | 0.751 | 0.804 | 0.998 | 0.96 | 1.000 | 0.121 | 0.093 (centred -0.046) | 0.493 (positive 0.86) |
| strict | true_recall_unseen | 444 | 0.413 | 0.504 | 0.709 | 0.94 | 0.843 | 0.569 | 0.261 (centred 0.097) | 0.493 (positive 0.86) |

### all systems, eight models including the poles

| reading | reference | n pairs | pooled r | centred r | per-system median r | positive | per-system median rho | median MAE | partial r with precision given reference | per-system median r with precision |
|---|---|---|---|---|---|---|---|---|---|---|
| graded | true_recall_unseen | 592 | 0.802 | 0.819 | 0.992 | 0.99 | 0.975 | 0.021 | -0.131 (centred -0.191) | 0.088 (positive 0.54) |
| strict | true_recall_strict_unseen | 592 | 0.813 | 0.845 | 0.956 | 1.00 | 0.975 | 0.092 | -0.185 (centred -0.322) | -0.213 (positive 0.32) |
| strict | true_recall_unseen | 592 | 0.520 | 0.566 | 0.690 | 0.99 | 0.867 | 0.521 | -0.193 (centred -0.313) | -0.213 (positive 0.32) |

## Per miner across systems

| miner | n | graded~ref | graded~precision | partial(graded, precision given ref) | strict~ref_strict | strict~precision | partial(strict, precision given ref_strict) | mean ref | mean ref strict | mean precision | mean graded | mean strict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Alpha | 74 | 0.506 | 0.295 | 0.287 | 0.584 | 0.391 | 0.305 | 0.678 | 0.027 | 0.474 | 0.738 | 0.117 |
| Alpha+ | 74 | 0.683 | 0.359 | -0.043 | 0.711 | 0.240 | 0.107 | 0.915 | 0.260 | 0.887 | 0.869 | 0.198 |
| Heuristics | 74 | 0.611 | -0.054 | -0.104 | 0.900 | 0.295 | -0.093 | 0.908 | 0.281 | 0.886 | 0.876 | 0.326 |
| Heuristics_Strict | 74 | 0.868 | 0.410 | 0.152 | 0.864 | 0.477 | 0.237 | 0.834 | 0.398 | 0.782 | 0.820 | 0.341 |
| Inductive_Strict | 74 | 0.025 | 0.027 | 0.019 | -0.005 | 0.091 | 0.104 | 1.000 | 0.999 | 0.954 | 0.949 | 0.646 |
| Inductive_Infrequent | 74 | 0.127 | 0.148 | 0.108 | 0.329 | 0.409 | 0.325 | 0.996 | 0.924 | 0.981 | 0.952 | 0.633 |
| Trace_Filtered | 74 | 0.856 | -0.132 | -0.060 | nan | 0.036 | nan | 0.757 | 0.000 | 1.000 | 0.739 | 0.033 |
| Flower | 74 | nan | nan | nan | nan | nan | nan | 1.000 | 1.000 | 0.404 | 1.000 | 1.000 |

## Poles

Flower (n=74): graded mean 1.0000 (min 1.0000), strict mean 1.0000 (min 1.0000), reference 1.000, reference strict 1.000, true precision 0.404.
Trace model (n=74): graded mean 0.739, strict mean 0.033, reference 0.757, reference strict 0.000, true precision 1.000.

Strict reading over the six miners: share of pairs at exactly 0: 0.37, at exactly 1: 0.18, n=468.
