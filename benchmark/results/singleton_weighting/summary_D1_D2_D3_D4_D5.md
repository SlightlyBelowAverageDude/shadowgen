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
| L4 | random | 0.626 | 57.6 / 64.9 / 58.1 / 62.6 / 64.2 | 618 | none | 0.998 | 1.00 | 1.00 | 0.014 | 0.77 (0.78) | 0.045 |
| | | | | | singleton | 0.999 | 1.00 | 1.00 | 0.009 | 0.77 (0.78) | 0.033 |
| | | | | | singleton, 5 bins | 0.999 | 1.00 | 1.00 | 0.010 | 0.77 (0.78) | 0.035 |
| | | | | | singleton, 20 bins | 0.999 | 1.00 | 1.00 | 0.009 | 0.77 (0.78) | 0.031 |
| | | | | | oracle (unseen lengths) | 0.999 | 1.00 | 1.00 | 0.010 | 0.77 (0.78) | 0.033 |
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
| L4 | random | Alpha | 0.209 | +0.012 | +0.007 | +0.007 |
| L4 | random | Alpha+ | 0.628 | -0.045 | -0.033 | -0.033 |
| L4 | random | Heuristics | 0.878 | -0.004 | -0.003 | -0.003 |
| L4 | random | Heuristics_Strict | 0.938 | -0.008 | -0.001 | -0.001 |
| L4 | random | Inductive_Strict | 0.988 | +0.000 | +0.000 | +0.000 |
| L4 | random | Inductive_Infrequent | 0.983 | -0.018 | -0.014 | -0.014 |
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
| L3 | temporal | none | 0.991 | 0.026 | 0.123 |
| L3 | temporal | singleton | 0.999 | 0.010 | 0.035 |
| L3 | temporal | oracle | 0.999 | 0.011 | 0.035 |
| L3 | random | none | 1.000 | 0.010 | 0.027 |
| L3 | random | singleton | 1.000 | 0.007 | 0.023 |
| L3 | random | oracle | 1.000 | 0.007 | 0.023 |
| L4 | random | none | 0.871 | 0.010 | 0.057 |
| L4 | random | singleton | 0.929 | 0.007 | 0.036 |
| L4 | random | oracle | 0.930 | 0.007 | 0.036 |
| L5 | temporal | none | 0.659 | 0.176 | 0.789 |
| L5 | temporal | singleton | 0.721 | 0.158 | 0.776 |
| L5 | temporal | oracle | 0.662 | 0.175 | 0.776 |
| L5 | random | none | 0.999 | 0.072 | 0.225 |
| L5 | random | singleton | 0.998 | 0.040 | 0.129 |
| L5 | random | oracle | 0.998 | 0.039 | 0.130 |
