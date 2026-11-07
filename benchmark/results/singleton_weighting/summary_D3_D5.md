# Singleton length weighting of the shadow log (sensitivity analysis)

Reference: replay fitness of the test cases whose variant is absent from training, same nets as the score.

| log | split | singleton share of cases | mean length: cases / singletons / shadow / weighted / unseen | ESS | weighting | Pearson | Spearman | tau_b | MAE | spread (ref) | max dev |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L3 | temporal | 0.465 | 38.3 / 49.9 / 44.7 / 50.1 / 49.3 | 868 | none | 1.000 | 1.00 | 1.00 | 0.002 | 0.61 (0.61) | 0.003 |
| | | | | | singleton | 1.000 | 1.00 | 1.00 | 0.002 | 0.61 (0.61) | 0.004 |
| | | | | | singleton, 5 bins | 1.000 | 1.00 | 1.00 | 0.002 | 0.61 (0.61) | 0.004 |
| | | | | | singleton, 20 bins | 1.000 | 1.00 | 1.00 | 0.002 | 0.61 (0.61) | 0.004 |
| | | | | | oracle (unseen lengths) | 1.000 | 1.00 | 1.00 | 0.002 | 0.61 (0.61) | 0.004 |
| L3 | random | 0.464 | 38.1 / 49.7 / 45.4 / 49.6 / 49.8 | 868 | none | 1.000 | 1.00 | 1.00 | 0.002 | 0.58 (0.58) | 0.005 |
| | | | | | singleton | 1.000 | 1.00 | 1.00 | 0.002 | 0.58 (0.58) | 0.004 |
| | | | | | singleton, 5 bins | 1.000 | 1.00 | 1.00 | 0.002 | 0.58 (0.58) | 0.004 |
| | | | | | singleton, 20 bins | 1.000 | 1.00 | 1.00 | 0.002 | 0.58 (0.58) | 0.004 |
| | | | | | oracle (unseen lengths) | 1.000 | 1.00 | 1.00 | 0.002 | 0.58 (0.58) | 0.004 |
| L5 | temporal | 0.038 | 6.5 / 35.1 / 19.4 / 27.9 / 10.3 | 686 | none | 0.965 | 0.89 | 0.73 | 0.074 | 0.71 (0.51) | 0.294 |
| | | | | | singleton | 0.986 | 1.00 | 1.00 | 0.080 | 0.69 (0.51) | 0.245 |
| | | | | | singleton, 5 bins | 0.985 | 1.00 | 1.00 | 0.078 | 0.68 (0.51) | 0.249 |
| | | | | | singleton, 20 bins | 0.987 | 1.00 | 1.00 | 0.080 | 0.69 (0.51) | 0.242 |
| | | | | | oracle (unseen lengths) | 0.957 | 0.89 | 0.73 | 0.076 | 0.72 (0.51) | 0.309 |
| L5 | random | 0.039 | 6.4 / 32.8 / 18.8 / 26.3 / 32.1 | 712 | none | 0.987 | 0.94 | 0.87 | 0.038 | 0.70 (0.73) | 0.092 |
| | | | | | singleton | 1.000 | 1.00 | 1.00 | 0.008 | 0.70 (0.73) | 0.022 |
| | | | | | singleton, 5 bins | 0.999 | 1.00 | 1.00 | 0.012 | 0.69 (0.73) | 0.033 |
| | | | | | singleton, 20 bins | 1.000 | 1.00 | 1.00 | 0.006 | 0.71 (0.73) | 0.016 |
| | | | | | oracle (unseen lengths) | 1.000 | 1.00 | 1.00 | 0.007 | 0.70 (0.73) | 0.021 |

## Per miner: score minus reference (graded)

| log | split | miner | reference | none | singleton | oracle |
|---|---|---|---|---|---|---|
| L3 | temporal | Alpha | 0.392 | +0.002 | -0.004 | -0.004 |
| L3 | temporal | Alpha+ | 0.855 | -0.002 | -0.002 | -0.002 |
| L3 | temporal | Heuristics | 0.949 | -0.003 | +0.003 | +0.003 |
| L3 | temporal | Heuristics_Strict | 0.952 | -0.002 | +0.003 | +0.003 |
| L3 | temporal | Inductive_Strict | 1.000 | -0.000 | -0.000 | -0.000 |
| L3 | temporal | Inductive_Infrequent | 0.984 | +0.003 | +0.001 | +0.002 |
| L3 | random | Alpha | 0.423 | -0.001 | -0.004 | -0.004 |
| L3 | random | Alpha+ | 0.859 | +0.003 | +0.003 | +0.003 |
| L3 | random | Heuristics | 0.954 | -0.005 | +0.001 | +0.001 |
| L3 | random | Heuristics_Strict | 0.956 | -0.003 | +0.002 | +0.002 |
| L3 | random | Inductive_Strict | 1.000 | -0.000 | -0.000 | -0.000 |
| L3 | random | Inductive_Infrequent | 0.977 | +0.002 | +0.002 | +0.002 |
| L5 | temporal | Alpha | 0.487 | -0.096 | -0.175 | -0.075 |
| L5 | temporal | Alpha+ | 0.580 | -0.294 | -0.245 | -0.309 |
| L5 | temporal | Heuristics | 0.831 | +0.010 | +0.028 | -0.011 |
| L5 | temporal | Heuristics_Strict | 0.902 | -0.008 | +0.001 | -0.026 |
| L5 | temporal | Inductive_Strict | 1.000 | -0.005 | -0.002 | -0.005 |
| L5 | temporal | Inductive_Infrequent | 0.967 | +0.029 | +0.028 | +0.029 |
| L5 | random | Alpha | 0.274 | +0.092 | +0.022 | +0.021 |
| L5 | random | Alpha+ | 0.361 | -0.069 | -0.006 | -0.004 |
| L5 | random | Heuristics | 0.863 | -0.024 | -0.006 | -0.006 |
| L5 | random | Heuristics_Strict | 0.914 | -0.015 | -0.005 | -0.005 |
| L5 | random | Inductive_Strict | 1.000 | -0.005 | -0.002 | -0.002 |
| L5 | random | Inductive_Infrequent | 0.985 | -0.022 | -0.008 | -0.008 |

## Strict reading against the perfect-replay share of the unseen cases

| log | split | weighting | Pearson | MAE | max dev |
|---|---|---|---|---|---|
| L3 | temporal | none | 0.991 | 0.026 | 0.123 |
| L3 | temporal | singleton | 0.999 | 0.010 | 0.035 |
| L3 | temporal | oracle | 0.999 | 0.011 | 0.035 |
| L3 | random | none | 1.000 | 0.010 | 0.027 |
| L3 | random | singleton | 1.000 | 0.007 | 0.023 |
| L3 | random | oracle | 1.000 | 0.007 | 0.023 |
| L5 | temporal | none | 0.659 | 0.176 | 0.789 |
| L5 | temporal | singleton | 0.721 | 0.158 | 0.776 |
| L5 | temporal | oracle | 0.662 | 0.175 | 0.776 |
| L5 | random | none | 0.999 | 0.072 | 0.225 |
| L5 | random | singleton | 0.998 | 0.040 | 0.129 |
| L5 | random | oracle | 0.998 | 0.039 | 0.130 |
