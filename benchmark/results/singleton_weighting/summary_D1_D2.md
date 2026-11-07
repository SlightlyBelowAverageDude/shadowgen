# Singleton length weighting of the shadow log (sensitivity analysis)

Reference: replay fitness of the test cases whose variant is absent from training, same nets as the score.

| log | split | singleton share of cases | mean length: cases / singletons / shadow / weighted / unseen | ESS | weighting | Pearson | Spearman | tau_b | MAE | spread (ref) | max dev |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | temporal | 0.778 | 14.7 / 16.8 / 17.7 / 16.0 / 16.1 | 933 | none | 0.993 | 1.00 | 1.00 | 0.025 | 0.75 (0.78) | 0.088 |
| | | | | | singleton | 0.993 | 1.00 | 1.00 | 0.026 | 0.74 (0.78) | 0.087 |
| | | | | | singleton, 5 bins | 0.993 | 1.00 | 1.00 | 0.027 | 0.74 (0.78) | 0.089 |
| | | | | | singleton, 20 bins | 0.994 | 1.00 | 1.00 | 0.026 | 0.74 (0.78) | 0.087 |
| | | | | | oracle (unseen lengths) | 0.994 | 1.00 | 1.00 | 0.025 | 0.74 (0.78) | 0.083 |
| L1 | random | 0.759 | 14.6 / 16.8 / 16.6 / 16.1 / 16.2 | 950 | none | 0.995 | 1.00 | 1.00 | 0.023 | 0.72 (0.73) | 0.076 |
| | | | | | singleton | 0.996 | 1.00 | 1.00 | 0.021 | 0.71 (0.73) | 0.071 |
| | | | | | singleton, 5 bins | 0.996 | 1.00 | 1.00 | 0.021 | 0.71 (0.73) | 0.070 |
| | | | | | singleton, 20 bins | 0.996 | 1.00 | 1.00 | 0.021 | 0.72 (0.73) | 0.071 |
| | | | | | oracle (unseen lengths) | 0.996 | 1.00 | 1.00 | 0.022 | 0.71 (0.73) | 0.070 |
| L2 | temporal | 0.208 | 9.8 / 21.5 / 14.0 / 20.8 / 15.5 | 584 | none | 0.994 | 1.00 | 1.00 | 0.022 | 0.77 (0.82) | 0.069 |
| | | | | | singleton | 0.996 | 1.00 | 1.00 | 0.021 | 0.87 (0.82) | 0.061 |
| | | | | | singleton, 5 bins | 0.998 | 1.00 | 1.00 | 0.017 | 0.86 (0.82) | 0.046 |
| | | | | | singleton, 20 bins | 0.995 | 1.00 | 1.00 | 0.024 | 0.87 (0.82) | 0.073 |
| | | | | | oracle (unseen lengths) | 1.000 | 1.00 | 1.00 | 0.004 | 0.82 (0.82) | 0.011 |
| L2 | random | 0.172 | 8.7 / 21.0 / 12.1 / 20.0 / 19.6 | 496 | none | 0.962 | 1.00 | 1.00 | 0.052 | 0.74 (0.87) | 0.177 |
| | | | | | singleton | 1.000 | 1.00 | 1.00 | 0.003 | 0.86 (0.87) | 0.008 |
| | | | | | singleton, 5 bins | 0.999 | 1.00 | 1.00 | 0.008 | 0.85 (0.87) | 0.025 |
| | | | | | singleton, 20 bins | 1.000 | 1.00 | 1.00 | 0.002 | 0.87 (0.87) | 0.004 |
| | | | | | oracle (unseen lengths) | 1.000 | 1.00 | 1.00 | 0.004 | 0.86 (0.87) | 0.009 |

## Per miner: score minus reference (graded)

| log | split | miner | reference | none | singleton | oracle |
|---|---|---|---|---|---|---|
| L1 | temporal | Alpha | 0.221 | +0.008 | +0.015 | +0.015 |
| L1 | temporal | Alpha+ | 0.845 | -0.088 | -0.087 | -0.083 |
| L1 | temporal | Heuristics | 0.874 | +0.003 | -0.003 | -0.005 |
| L1 | temporal | Heuristics_Strict | 0.929 | -0.003 | -0.006 | -0.007 |
| L1 | temporal | Inductive_Strict | 1.000 | -0.024 | -0.023 | -0.020 |
| L1 | temporal | Inductive_Infrequent | 0.991 | -0.025 | -0.025 | -0.022 |
| L1 | random | Alpha | 0.272 | -0.006 | -0.002 | +0.002 |
| L1 | random | Alpha+ | 0.823 | -0.076 | -0.071 | -0.070 |
| L1 | random | Heuristics | 0.919 | -0.004 | -0.005 | -0.008 |
| L1 | random | Heuristics_Strict | 0.932 | -0.010 | -0.010 | -0.012 |
| L1 | random | Inductive_Strict | 1.000 | -0.018 | -0.018 | -0.017 |
| L1 | random | Inductive_Infrequent | 0.990 | -0.022 | -0.021 | -0.020 |
| L2 | temporal | Alpha | 0.181 | +0.045 | -0.046 | -0.005 |
| L2 | temporal | Alpha+ | 0.743 | -0.069 | +0.061 | -0.000 |
| L2 | temporal | Heuristics | 0.987 | +0.006 | +0.006 | +0.006 |
| L2 | temporal | Heuristics_Strict | 0.996 | +0.001 | +0.002 | +0.002 |
| L2 | temporal | Inductive_Strict | 1.000 | -0.000 | -0.000 | -0.000 |
| L2 | temporal | Inductive_Infrequent | 0.978 | +0.012 | +0.011 | +0.011 |
| L2 | random | Alpha | 0.129 | +0.126 | +0.008 | +0.009 |
| L2 | random | Alpha+ | 0.808 | -0.177 | -0.008 | -0.009 |
| L2 | random | Heuristics | 0.992 | +0.003 | +0.002 | +0.002 |
| L2 | random | Heuristics_Strict | 0.998 | +0.000 | +0.000 | +0.000 |
| L2 | random | Inductive_Strict | 1.000 | -0.000 | -0.000 | -0.000 |
| L2 | random | Inductive_Infrequent | 0.987 | +0.006 | +0.003 | +0.002 |

## Strict reading against the perfect-replay share of the unseen cases

| log | split | weighting | Pearson | MAE | max dev |
|---|---|---|---|---|---|
| L1 | temporal | none | 1.000 | 0.115 | 0.348 |
| L1 | temporal | singleton | 1.000 | 0.104 | 0.314 |
| L1 | temporal | oracle | 1.000 | 0.099 | 0.297 |
| L1 | random | none | 1.000 | 0.095 | 0.292 |
| L1 | random | singleton | 1.000 | 0.092 | 0.284 |
| L1 | random | oracle | 1.000 | 0.088 | 0.272 |
| L2 | temporal | none | 0.997 | 0.027 | 0.079 |
| L2 | temporal | singleton | 1.000 | 0.008 | 0.017 |
| L2 | temporal | oracle | 0.999 | 0.016 | 0.047 |
| L2 | random | none | 0.993 | 0.043 | 0.116 |
| L2 | random | singleton | 1.000 | 0.007 | 0.013 |
| L2 | random | oracle | 1.000 | 0.008 | 0.017 |
