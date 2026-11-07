# ShadowGen readings on the synthetic known-system study (synth_unseen_check.json, reference: full)

Protocol: seed 42; one 1,000-trace draw; N=6, tau=5, mle; v2.6 core; pm4py 2.7.22.2. 78 systems regenerated from the stored seeds (trees match the stored study on 78 of 78); training log and fresh sample resampled, so this is a replication under resampling, not a reproduction.

## Replication against the stored study (per log-model pair, |fresh - stored|, full reference)

| quantity | n | median | p90 | max |
|---|---|---|---|---|
| graded | 624 | 0.0031 | 0.0317 | 0.5710 |
| true_recall | 624 | 0.0000 | 0.0196 | 0.6035 |
| true_precision | 624 | 0.0000 | 0.0185 | 0.7404 |
| m2 | 624 | 0.0010 | 0.0100 | 0.1693 |

Graded reading, per-system Pearson with full true recall over the six miners, discriminating systems (sd >= 0.05): fresh median 0.899 (n=61, positive 0.92); stored median 0.904 (n=61, positive 0.90).

## Both readings against the full reference and true precision

Pooled r over all pairs; centred r after subtracting each system's mean; per-system medians over systems with at least 3 models. The partial correlation asks whether the score still tracks true precision once the reference recall is held fixed.

### discriminating systems, six discovered nets

| reading | reference | n pairs | pooled r | centred r | per-system median r | positive | per-system median rho | median MAE | partial r with precision given reference | per-system median r with precision |
|---|---|---|---|---|---|---|---|---|---|---|
| graded | true_recall | 366 | 0.550 | 0.604 | 0.899 | 0.92 | 0.935 | 0.069 | 0.316 (centred 0.357) | 0.658 (positive 0.84) |
| strict | true_recall_strict | 456 | 0.660 | 0.716 | 0.891 | 0.93 | 0.894 | 0.244 | 0.101 (centred 0.044) | 0.489 (positive 0.85) |
| strict | true_recall | 366 | 0.348 | 0.448 | 0.602 | 0.93 | 0.840 | 0.597 | 0.308 (centred 0.252) | 0.469 (positive 0.82) |

### all systems, six discovered nets

| reading | reference | n pairs | pooled r | centred r | per-system median r | positive | per-system median rho | median MAE | partial r with precision given reference | per-system median r with precision |
|---|---|---|---|---|---|---|---|---|---|---|
| graded | true_recall | 468 | 0.580 | 0.607 | 0.920 | 0.93 | 0.938 | 0.052 | 0.325 (centred 0.357) | 0.698 (positive 0.85) |
| strict | true_recall_strict | 468 | 0.670 | 0.716 | 0.891 | 0.93 | 0.894 | 0.244 | 0.106 (centred 0.044) | 0.489 (positive 0.85) |
| strict | true_recall | 468 | 0.363 | 0.427 | 0.663 | 0.95 | 0.840 | 0.572 | 0.327 (centred 0.269) | 0.489 (positive 0.85) |

### all systems, eight models including the poles

| reading | reference | n pairs | pooled r | centred r | per-system median r | positive | per-system median rho | median MAE | partial r with precision given reference | per-system median r with precision |
|---|---|---|---|---|---|---|---|---|---|---|
| graded | true_recall | 624 | 0.632 | 0.670 | 0.912 | 0.97 | 0.927 | 0.045 | 0.049 (centred 0.018) | 0.046 (positive 0.51) |
| strict | true_recall_strict | 624 | 0.738 | 0.771 | 0.886 | 0.99 | 0.884 | 0.201 | -0.204 (centred -0.296) | -0.216 (positive 0.32) |
| strict | true_recall | 624 | 0.468 | 0.513 | 0.678 | 0.99 | 0.858 | 0.512 | -0.104 (centred -0.197) | -0.216 (positive 0.32) |

## Per miner across systems

| miner | n | graded~ref | graded~precision | partial(graded, precision given ref) | strict~ref_strict | strict~precision | partial(strict, precision given ref_strict) | mean ref | mean ref strict | mean precision | mean graded | mean strict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Alpha | 78 | 0.596 | 0.342 | 0.225 | 0.663 | 0.407 | 0.105 | 0.789 | 0.253 | 0.488 | 0.746 | 0.130 |
| Alpha+ | 78 | 0.365 | 0.329 | 0.147 | 0.600 | 0.233 | 0.184 | 0.937 | 0.474 | 0.893 | 0.868 | 0.200 |
| Heuristics | 78 | 0.541 | -0.065 | 0.045 | 0.706 | 0.276 | -0.018 | 0.808 | 0.366 | 0.881 | 0.868 | 0.319 |
| Heuristics_Strict | 78 | 0.566 | 0.359 | 0.425 | 0.767 | 0.383 | 0.291 | 0.832 | 0.507 | 0.777 | 0.821 | 0.338 |
| Inductive_Strict | 78 | -0.004 | -0.011 | -0.010 | -0.019 | 0.062 | 0.091 | 1.000 | 1.000 | 0.956 | 0.942 | 0.625 |
| Inductive_Infrequent | 78 | 0.097 | 0.084 | 0.045 | 0.265 | 0.356 | 0.279 | 0.997 | 0.951 | 0.982 | 0.945 | 0.613 |
| Trace_Filtered | 78 | 0.416 | -0.119 | -0.094 | 0.500 | 0.033 | -0.008 | 0.769 | 0.197 | 1.000 | 0.738 | 0.044 |
| Flower | 78 | nan | nan | nan | nan | nan | nan | 1.000 | 1.000 | 0.405 | 1.000 | 1.000 |

## Poles

Flower (n=78): graded mean 1.0000 (min 1.0000), strict mean 1.0000 (min 1.0000), reference 1.000, reference strict 1.000, true precision 0.405.
Trace model (n=78): graded mean 0.738, strict mean 0.044, reference 0.769, reference strict 0.197, true precision 1.000.

Strict reading over the six miners: share of pairs at exactly 0: 0.37, at exactly 1: 0.18, n=468.
