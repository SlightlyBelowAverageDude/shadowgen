# Singleton length weighting of the shadow log (sensitivity analysis)

Reference: replay fitness of the test cases whose variant is absent from training, same nets as the score.

| log | split | singleton share of cases | mean length: cases / singletons / shadow / weighted / unseen | ESS | weighting | Pearson | Spearman | tau_b | MAE | spread (ref) | max dev |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L4 | random | 0.626 | 57.6 / 64.9 / 58.1 / 62.6 / 64.2 | 618 | none | 0.998 | 1.00 | 1.00 | 0.014 | 0.77 (0.78) | 0.045 |
| | | | | | singleton | 0.999 | 1.00 | 1.00 | 0.009 | 0.77 (0.78) | 0.033 |
| | | | | | singleton, 5 bins | 0.999 | 1.00 | 1.00 | 0.010 | 0.77 (0.78) | 0.035 |
| | | | | | singleton, 20 bins | 0.999 | 1.00 | 1.00 | 0.009 | 0.77 (0.78) | 0.031 |
| | | | | | oracle (unseen lengths) | 0.999 | 1.00 | 1.00 | 0.010 | 0.77 (0.78) | 0.033 |

## Per miner: score minus reference (graded)

| log | split | miner | reference | none | singleton | oracle |
|---|---|---|---|---|---|---|
| L4 | random | Alpha | 0.209 | +0.012 | +0.007 | +0.007 |
| L4 | random | Alpha+ | 0.628 | -0.045 | -0.033 | -0.033 |
| L4 | random | Heuristics | 0.878 | -0.004 | -0.003 | -0.003 |
| L4 | random | Heuristics_Strict | 0.938 | -0.008 | -0.001 | -0.001 |
| L4 | random | Inductive_Strict | 0.988 | +0.000 | +0.000 | +0.000 |
| L4 | random | Inductive_Infrequent | 0.983 | -0.018 | -0.014 | -0.014 |

## Strict reading against the perfect-replay share of the unseen cases

| log | split | weighting | Pearson | MAE | max dev |
|---|---|---|---|---|---|
| L4 | random | none | 0.871 | 0.010 | 0.057 |
| L4 | random | singleton | 0.929 | 0.007 | 0.036 |
| L4 | random | oracle | 0.930 | 0.007 | 0.036 |
