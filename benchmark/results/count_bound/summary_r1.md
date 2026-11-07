# Count-bound rejection against R1

| log | shadow breaking | acceptance | length shadow / bounded | score | Pearson | Spearman | MAE | spread (R1) | max dev |
|---|---|---|---|---|---|---|---|---|---|
| L1 | 0.244 | 0.750 | 16.9 / 16.3 | stored | 0.996 | 1.00 | 0.023 | 0.71 (0.73) | 0.070 |
| | | | | fresh | 0.996 | 1.00 | 0.023 | 0.71 (0.73) | 0.070 |
| | | | | bounded | 0.999 | 1.00 | 0.009 | 0.72 (0.73) | 0.023 |
| | | | | strict fresh | 0.998 | 0.94 | 0.076 | 0.74 (1.00) | 0.252 |
| | | | | strict bounded | 0.998 | 1.00 | 0.023 | 0.98 (1.00) | 0.056 |
| L2 | 0.000 | 1.000 | 12.1 / 12.1 | stored | 0.994 | 1.00 | 0.019 | 0.74 (0.78) | 0.068 |
| | | | | fresh | 0.994 | 1.00 | 0.019 | 0.74 (0.78) | 0.068 |
| | | | | bounded | 0.994 | 1.00 | 0.019 | 0.74 (0.78) | 0.068 |
| | | | | strict fresh | 0.997 | 0.94 | 0.021 | 1.00 (1.00) | 0.075 |
| | | | | strict bounded | 0.997 | 0.94 | 0.021 | 1.00 (1.00) | 0.075 |
| L3 | 0.050 | 0.950 | 44.9 / 44.6 | stored | 0.999 | 0.94 | 0.006 | 0.61 (0.61) | 0.024 |
| | | | | fresh | 0.999 | 0.94 | 0.006 | 0.61 (0.61) | 0.024 |
| | | | | bounded | 0.999 | 0.94 | 0.006 | 0.61 (0.61) | 0.020 |
| | | | | strict fresh | 0.992 | 1.00 | 0.039 | 0.97 (1.00) | 0.115 |
| | | | | strict bounded | 0.992 | 1.00 | 0.033 | 1.00 (1.00) | 0.110 |
| L4 | 0.103 | 0.897 | 58.2 / 59.3 | stored | 0.999 | 1.00 | 0.016 | 0.76 (0.79) | 0.034 |
| | | | | fresh | 0.999 | 1.00 | 0.016 | 0.76 (0.79) | 0.034 |
| | | | | bounded | 0.999 | 1.00 | 0.017 | 0.76 (0.79) | 0.045 |
| | | | | strict fresh | -0.038 | 0.94 | 0.057 | 0.09 (0.30) | 0.298 |
| | | | | strict bounded | -0.040 | 0.94 | 0.058 | 0.10 (0.30) | 0.299 |
| L5 | 0.223 | 0.777 | 17.4 / 20.5 | stored | 0.986 | 0.94 | 0.043 | 0.67 (0.65) | 0.128 |
| | | | | fresh | 0.986 | 0.94 | 0.043 | 0.67 (0.65) | 0.128 |
| | | | | bounded | 0.999 | 1.00 | 0.031 | 0.71 (0.65) | 0.058 |
| | | | | strict fresh | 0.999 | 0.94 | 0.075 | 0.78 (1.00) | 0.223 |
| | | | | strict bounded | 0.999 | 1.00 | 0.017 | 1.00 (1.00) | 0.055 |

## Per miner (score minus R1)

| log | miner | R1 | fresh | bounded | net |
|---|---|---|---|---|---|
| L1 | Alpha | 0.275 | -0.002 | +0.000 | cached PNML |
| L1 | Alpha+ | 0.829 | -0.070 | -0.019 | cached PNML |
| L1 | Heuristics | 0.902 | -0.024 | -0.023 | cached PNML |
| L1 | Heuristics_Strict | 0.933 | -0.015 | -0.010 | cached PNML |
| L1 | Inductive_Strict | 1.000 | -0.016 | -0.000 | cached PNML |
| L1 | Inductive_Infrequent | 0.985 | -0.012 | +0.001 | cached PNML |
| L2 | Alpha | 0.215 | +0.042 | +0.042 | cached PNML |
| L2 | Alpha+ | 0.698 | -0.068 | -0.068 | in-memory discovery |
| L2 | Heuristics | 0.996 | -0.002 | -0.002 | cached PNML |
| L2 | Heuristics_Strict | 0.998 | -0.001 | -0.001 | cached PNML |
| L2 | Inductive_Strict | 1.000 | -0.000 | -0.000 | cached PNML |
| L2 | Inductive_Infrequent | 0.988 | +0.003 | +0.003 | cached PNML |
| L3 | Alpha | 0.385 | +0.004 | +0.006 | cached PNML |
| L3 | Alpha+ | 0.884 | -0.024 | -0.020 | cached PNML |
| L3 | Heuristics | 0.953 | -0.005 | -0.004 | cached PNML |
| L3 | Heuristics_Strict | 0.952 | -0.001 | -0.000 | cached PNML |
| L3 | Inductive_Strict | 1.000 | -0.000 | +0.000 | cached PNML |
| L3 | Inductive_Infrequent | 0.981 | -0.005 | -0.004 | cached PNML |
| L4 | Alpha | 0.196 | +0.025 | +0.023 | cached PNML |
| L4 | Alpha+ | 0.633 | +0.034 | +0.045 | cached PNML |
| L4 | Heuristics | 0.882 | -0.007 | -0.006 | cached PNML |
| L4 | Heuristics_Strict | 0.938 | -0.011 | -0.009 | cached PNML |
| L4 | Inductive_Strict | 0.985 | -0.009 | -0.009 | cached PNML |
| L4 | Inductive_Infrequent | 0.982 | -0.013 | -0.010 | cached PNML |
| L5 | Alpha | 0.345 | +0.023 | -0.058 | cached PNML |
| L5 | Alpha+ | 0.456 | -0.128 | -0.053 | cached PNML |
| L5 | Heuristics | 0.885 | -0.046 | -0.040 | cached PNML |
| L5 | Heuristics_Strict | 0.929 | -0.032 | -0.027 | cached PNML |
| L5 | Inductive_Strict | 1.000 | -0.004 | +0.000 | cached PNML |
| L5 | Inductive_Infrequent | 0.988 | -0.026 | -0.006 | cached PNML |
