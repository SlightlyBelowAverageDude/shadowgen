# Strict reading on the synthetic known-system study

Protocol: seed 42; one 1,000-trace draw; N=6, tau=5, mle; v2.6 core; pm4py 2.7.22.2. 78 systems regenerated from the stored seeds (trees match the stored study on 78 of 78); training log and fresh sample resampled, so this is a replication under resampling, not a reproduction.

## Replication against the stored study (per log-model pair, |fresh - stored|)

| quantity | n | median | p90 | max |
|---|---|---|---|---|
| graded | 624 | 0.0035 | 0.0332 | 0.2206 |
| true_recall | 624 | 0.0000 | 0.0239 | 0.5530 |
| true_precision | 624 | 0.0000 | 0.0174 | 0.5657 |
| m2 | 624 | 0.0008 | 0.0104 | 0.1695 |

Graded reading, per-system Pearson with true recall over the six miners, discriminating systems (sd >= 0.05): fresh median 0.905 (n=62, positive 0.90); stored median 0.904 (n=61, positive 0.90).

## Both readings against true recall and true precision

Pooled r over all pairs; centred r after subtracting each system's mean; per-system medians over systems with at least 3 models. The partial correlation asks whether the score still tracks true precision once the reference recall is held fixed.

### discriminating systems, six discovered nets

| reading | reference | n pairs | pooled r | centred r | per-system median r | positive | per-system median rho | median MAE | partial r with precision given reference | per-system median r with precision |
|---|---|---|---|---|---|---|---|---|---|---|
| graded | true_recall | 372 | 0.530 | 0.576 | 0.905 | 0.90 | 0.824 | 0.071 | 0.333 (centred 0.392) | 0.690 (positive 0.85) |
| strict | true_recall_strict | 456 | 0.666 | 0.729 | 0.868 | 0.93 | 0.894 | 0.264 | 0.122 (centred 0.066) | 0.510 (positive 0.88) |
| strict | true_recall | 372 | 0.339 | 0.437 | 0.619 | 0.92 | 0.840 | 0.584 | 0.354 (centred 0.285) | 0.508 (positive 0.85) |

### all systems, six discovered nets

| reading | reference | n pairs | pooled r | centred r | per-system median r | positive | per-system median rho | median MAE | partial r with precision given reference | per-system median r with precision |
|---|---|---|---|---|---|---|---|---|---|---|
| graded | true_recall | 468 | 0.559 | 0.579 | 0.918 | 0.92 | 0.843 | 0.052 | 0.343 (centred 0.391) | 0.749 (positive 0.86) |
| strict | true_recall_strict | 468 | 0.676 | 0.729 | 0.868 | 0.93 | 0.894 | 0.256 | 0.126 (centred 0.066) | 0.510 (positive 0.88) |
| strict | true_recall | 468 | 0.354 | 0.420 | 0.647 | 0.93 | 0.840 | 0.572 | 0.357 (centred 0.297) | 0.510 (positive 0.88) |

### all systems, eight models including the poles

| reading | reference | n pairs | pooled r | centred r | per-system median r | positive | per-system median rho | median MAE | partial r with precision given reference | per-system median r with precision |
|---|---|---|---|---|---|---|---|---|---|---|
| graded | true_recall | 624 | 0.612 | 0.647 | 0.898 | 0.96 | 0.895 | 0.047 | 0.070 (centred 0.041) | 0.063 (positive 0.55) |
| strict | true_recall_strict | 624 | 0.741 | 0.779 | 0.874 | 0.99 | 0.875 | 0.208 | -0.190 (centred -0.277) | -0.206 (positive 0.28) |
| strict | true_recall | 624 | 0.459 | 0.506 | 0.676 | 0.97 | 0.855 | 0.515 | -0.081 (centred -0.175) | -0.206 (positive 0.28) |

## Per miner across systems

| miner | n | graded~recall | graded~precision | partial(graded, precision given recall) | strict~recall_strict | strict~precision | partial(strict, precision given recall_strict) | mean true recall | mean true recall strict | mean precision | mean graded | mean strict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Alpha | 78 | 0.508 | 0.352 | 0.214 | 0.627 | 0.417 | 0.110 | 0.787 | 0.253 | 0.464 | 0.736 | 0.118 |
| Alpha+ | 78 | 0.375 | 0.357 | 0.175 | 0.617 | 0.247 | 0.152 | 0.938 | 0.497 | 0.884 | 0.867 | 0.209 |
| Heuristics | 78 | 0.484 | -0.056 | 0.055 | 0.728 | 0.304 | 0.031 | 0.804 | 0.374 | 0.883 | 0.869 | 0.317 |
| Heuristics_Strict | 78 | 0.567 | 0.336 | 0.412 | 0.747 | 0.456 | 0.415 | 0.822 | 0.498 | 0.786 | 0.815 | 0.326 |
| Inductive_Strict | 78 | 0.022 | -0.006 | -0.020 | 0.036 | 0.091 | 0.095 | 1.000 | 1.000 | 0.957 | 0.943 | 0.629 |
| Inductive_Infrequent | 78 | 0.036 | 0.079 | 0.071 | 0.298 | 0.411 | 0.297 | 0.997 | 0.943 | 0.977 | 0.946 | 0.615 |
| Trace_Filtered | 78 | 0.408 | -0.033 | -0.030 | 0.453 | 0.025 | -0.008 | 0.769 | 0.182 | 1.000 | 0.740 | 0.030 |
| Flower | 78 | nan | nan | nan | nan | nan | nan | 1.000 | 1.000 | 0.405 | 1.000 | 1.000 |

## Poles

Flower: graded mean 1.0000 (min 1.0000), strict mean 1.0000 (min 1.0000), true recall 1.000, true precision 0.405.
Trace model: graded mean 0.740, strict mean 0.030, true recall 0.769, true recall strict 0.182, true precision 1.000.

Strict reading over the six miners: share of pairs at exactly 0: 0.38, at exactly 1: 0.17, n=468.
