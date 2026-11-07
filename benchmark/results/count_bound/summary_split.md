# Count-bound rejection of shadow traces (sensitivity analysis)

| log | split | shadow breaking | unseen cases breaking (over max / under min) | length shadow / bounded / unseen | score | Pearson | Spearman | MAE | spread (ref) | max dev |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 | temporal | 0.360 | 0.004 (0.000 / 0.004) | 17.7 / 16.3 / 16.1 | original | 0.993 | 1.00 | 0.025 | 0.75 (0.78) | 0.088 |
| | | | | | bounded | 1.000 | 1.00 | 0.006 | 0.77 (0.78) | 0.017 |
| | | | | | strict original | 1.000 | 0.94 | 0.115 | 0.64 (0.99) | 0.348 |
| | | | | | strict bounded | 0.999 | 1.00 | 0.010 | 1.00 (0.99) | 0.041 |
| L1 | random | 0.287 | 0.000 (0.000 / 0.000) | 16.6 / 15.9 / 16.2 | original | 0.995 | 1.00 | 0.023 | 0.72 (0.73) | 0.076 |
| | | | | | bounded | 1.000 | 1.00 | 0.005 | 0.73 (0.73) | 0.013 |
| | | | | | strict original | 1.000 | 1.00 | 0.095 | 0.70 (1.00) | 0.292 |
| | | | | | strict bounded | 1.000 | 1.00 | 0.011 | 0.98 (1.00) | 0.048 |
| L2 | temporal | 0.000 | 0.000 (0.000 / 0.000) | 14.0 / 14.0 / 15.5 | original | 0.994 | 1.00 | 0.022 | 0.77 (0.82) | 0.069 |
| | | | | | bounded | 0.994 | 1.00 | 0.022 | 0.77 (0.82) | 0.069 |
| | | | | | strict original | 0.997 | 0.94 | 0.027 | 0.99 (1.00) | 0.079 |
| | | | | | strict bounded | 0.997 | 0.94 | 0.027 | 0.99 (1.00) | 0.079 |
| L2 | random | 0.000 | 0.000 (0.000 / 0.000) | 12.1 / 12.1 / 19.6 | original | 0.962 | 1.00 | 0.052 | 0.74 (0.87) | 0.177 |
| | | | | | bounded | 0.962 | 1.00 | 0.052 | 0.74 (0.87) | 0.177 |
| | | | | | strict original | 0.993 | 1.00 | 0.043 | 0.99 (1.00) | 0.116 |
| | | | | | strict bounded | 0.993 | 1.00 | 0.043 | 0.99 (1.00) | 0.116 |
| L3 | temporal | 0.048 | 0.000 (0.000 / 0.000) | 44.7 / 44.6 / 49.3 | original | 1.000 | 1.00 | 0.002 | 0.61 (0.61) | 0.003 |
| | | | | | bounded | 1.000 | 1.00 | 0.003 | 0.60 (0.61) | 0.005 |
| | | | | | strict original | 0.991 | 1.00 | 0.026 | 0.96 (1.00) | 0.123 |
| | | | | | strict bounded | 0.990 | 1.00 | 0.023 | 1.00 (1.00) | 0.135 |
| L3 | random | 0.041 | 0.001 (0.001 / 0.000) | 45.4 / 45.1 / 49.8 | original | 1.000 | 1.00 | 0.002 | 0.58 (0.58) | 0.005 |
| | | | | | bounded | 1.000 | 1.00 | 0.002 | 0.58 (0.58) | 0.005 |
| | | | | | strict original | 1.000 | 1.00 | 0.010 | 0.98 (1.00) | 0.027 |
| | | | | | strict bounded | 1.000 | 1.00 | 0.007 | 1.00 (1.00) | 0.030 |
| L5 | temporal | 0.211 | 0.030 (0.030 / 0.000) | 19.4 / 21.5 / 10.3 | original | 0.965 | 0.89 | 0.074 | 0.71 (0.51) | 0.294 |
| | | | | | bounded | 0.988 | 1.00 | 0.073 | 0.67 (0.51) | 0.234 |
| | | | | | strict original | 0.659 | 0.89 | 0.176 | 0.96 (1.00) | 0.789 |
| | | | | | strict bounded | 0.755 | 1.00 | 0.143 | 1.00 (1.00) | 0.799 |
| L5 | random | 0.225 | 0.002 (0.002 / 0.000) | 18.8 / 21.3 / 32.1 | original | 0.987 | 0.94 | 0.038 | 0.70 (0.73) | 0.092 |
| | | | | | bounded | 0.999 | 1.00 | 0.009 | 0.71 (0.73) | 0.019 |
| | | | | | strict original | 0.999 | 0.94 | 0.072 | 0.78 (1.00) | 0.225 |
| | | | | | strict bounded | 1.000 | 1.00 | 0.004 | 1.00 (1.00) | 0.019 |

## Per miner, graded (score minus reference)

| log | split | miner | reference | original | bounded |
|---|---|---|---|---|---|
| L1 | temporal | Alpha | 0.221 | +0.008 | +0.006 |
| L1 | temporal | Alpha+ | 0.845 | -0.088 | -0.017 |
| L1 | temporal | Heuristics | 0.874 | +0.003 | +0.002 |
| L1 | temporal | Heuristics_Strict | 0.929 | -0.003 | +0.005 |
| L1 | temporal | Inductive_Strict | 1.000 | -0.024 | +0.000 |
| L1 | temporal | Inductive_Infrequent | 0.991 | -0.025 | -0.004 |
| L1 | random | Alpha | 0.272 | -0.006 | -0.006 |
| L1 | random | Alpha+ | 0.823 | -0.076 | -0.013 |
| L1 | random | Heuristics | 0.919 | -0.004 | -0.002 |
| L1 | random | Heuristics_Strict | 0.932 | -0.010 | -0.005 |
| L1 | random | Inductive_Strict | 1.000 | -0.018 | -0.000 |
| L1 | random | Inductive_Infrequent | 0.990 | -0.022 | -0.005 |
| L2 | temporal | Alpha | 0.181 | +0.045 | +0.045 |
| L2 | temporal | Alpha+ | 0.743 | -0.069 | -0.069 |
| L2 | temporal | Heuristics | 0.987 | +0.006 | +0.006 |
| L2 | temporal | Heuristics_Strict | 0.996 | +0.001 | +0.001 |
| L2 | temporal | Inductive_Strict | 1.000 | -0.000 | -0.000 |
| L2 | temporal | Inductive_Infrequent | 0.978 | +0.012 | +0.012 |
| L2 | random | Alpha | 0.129 | +0.126 | +0.126 |
| L2 | random | Alpha+ | 0.808 | -0.177 | -0.177 |
| L2 | random | Heuristics | 0.992 | +0.003 | +0.003 |
| L2 | random | Heuristics_Strict | 0.998 | +0.000 | +0.000 |
| L2 | random | Inductive_Strict | 1.000 | -0.000 | -0.000 |
| L2 | random | Inductive_Infrequent | 0.987 | +0.006 | +0.006 |
| L3 | temporal | Alpha | 0.392 | +0.002 | +0.005 |
| L3 | temporal | Alpha+ | 0.855 | -0.002 | +0.002 |
| L3 | temporal | Heuristics | 0.949 | -0.003 | -0.003 |
| L3 | temporal | Heuristics_Strict | 0.952 | -0.002 | -0.002 |
| L3 | temporal | Inductive_Strict | 1.000 | -0.000 | +0.000 |
| L3 | temporal | Inductive_Infrequent | 0.984 | +0.003 | +0.004 |
| L3 | random | Alpha | 0.423 | -0.001 | +0.001 |
| L3 | random | Alpha+ | 0.859 | +0.003 | +0.005 |
| L3 | random | Heuristics | 0.954 | -0.005 | -0.004 |
| L3 | random | Heuristics_Strict | 0.956 | -0.003 | -0.003 |
| L3 | random | Inductive_Strict | 1.000 | -0.000 | +0.000 |
| L3 | random | Inductive_Infrequent | 0.977 | +0.002 | +0.002 |
| L5 | temporal | Alpha | 0.487 | -0.096 | -0.157 |
| L5 | temporal | Alpha+ | 0.580 | -0.294 | -0.234 |
| L5 | temporal | Heuristics | 0.831 | +0.010 | +0.012 |
| L5 | temporal | Heuristics_Strict | 0.903 | -0.008 | -0.003 |
| L5 | temporal | Inductive_Strict | 1.000 | -0.005 | +0.000 |
| L5 | temporal | Inductive_Infrequent | 0.967 | +0.029 | +0.031 |
| L5 | random | Alpha | 0.274 | +0.092 | +0.013 |
| L5 | random | Alpha+ | 0.361 | -0.069 | -0.011 |
| L5 | random | Heuristics | 0.861 | -0.023 | -0.019 |
| L5 | random | Heuristics_Strict | 0.913 | -0.014 | -0.010 |
| L5 | random | Inductive_Strict | 1.000 | -0.005 | +0.000 |
| L5 | random | Inductive_Infrequent | 0.985 | -0.022 | -0.002 |
