# Temporal hold-out: all test cases against unseen test cases only

| log | test cases | unseen cases | unseen share | unseen variants |
|---|---|---|---|---|
| L1 | 315 | 239 | 0.759 | 233 |
| L2 | 2267 | 165 | 0.073 | 158 |
| L3 | 9453 | 4372 | 0.462 | 4203 |
| L4 | 13143 | 8408 | 0.640 | 6902 |
| L5 | 75521 | 15618 | 0.207 | 3151 |

## Reproduction of the stored run (|fresh - stored| per model, six miners and poles)

| log | shadowgen max | holdout_fit max | holdout_fit_strict max | m2 max | models above 0.001 |
|---|---|---|---|---|---|
| L1 | 0.0223 | 0.0121 | 0.0349 | 0.0042 | Trace_Filtered.shadowgen 0.0223; Trace_Filtered.holdout_fit 0.0121; Trace_Filtered.holdout_fit_strict 0.0349; Trace_Filtered.m2 0.0042 |
| L2 | 0.0291 | 0.0071 | 0.0053 | 0.0063 | Trace_Filtered.shadowgen 0.0291; Trace_Filtered.holdout_fit 0.0071; Trace_Filtered.holdout_fit_strict 0.0053; Trace_Filtered.m2 0.0063 |
| L3 | 0.0216 | 0.0242 | 0.0057 | 0.0138 | Trace_Filtered.shadowgen 0.0216; Trace_Filtered.holdout_fit 0.0242; Trace_Filtered.holdout_fit_strict 0.0057; Heuristics_Strict.m2 0.0138 |
| L4 | 0.0022 | 0.0581 | 0.0000 | 0.0163 | Trace_Filtered.shadowgen 0.0022; Heuristics.shadowgen 0.0016; Trace_Filtered.holdout_fit 0.0581; Heuristics.holdout_fit 0.0020; Heuristics_Strict.holdout_fit 0.0025; Trace_Filtered.m2 0.0163; Heuristics.m2 0.0011 |
| L5 | 0.0033 | 0.0609 | 0.0325 | 0.0090 | Trace_Filtered.shadowgen 0.0033; Trace_Filtered.holdout_fit 0.0609; Trace_Filtered.holdout_fit_strict 0.0325; Trace_Filtered.m2 0.0090; Heuristics.m2 0.0043 |

## Four criteria over the six miners

| log | metric | reference | Pearson | Spearman | Spearman (ties) | tau_b | MAE | spread metric | spread reference |
|---|---|---|---|---|---|---|---|---|---|
| L1 | ShadowGen graded | holdout_fit | 0.998 | 1.00 | 1.00 | 1.00 | 0.018 | 0.75 | 0.76 |
| L1 | ShadowGen graded | unseen_fit | 0.993 | 1.00 | 1.00 | 1.00 | 0.025 | 0.75 | 0.78 |
| L1 | ShadowGen strict | holdout_fit_strict | 0.999 | 0.94 | 0.99 | 0.97 | 0.115 | 0.64 | 0.99 |
| L1 | ShadowGen strict | unseen_fit_strict | 1.000 | 0.94 | 0.94 | 0.89 | 0.115 | 0.64 | 0.99 |
| L1 | M2 | holdout_fit | -0.142 | 0.09 | 0.09 | 0.07 | 0.175 | 0.09 | 0.76 |
| L1 | M2 | unseen_fit | -0.124 | 0.09 | 0.09 | 0.07 | 0.173 | 0.09 | 0.78 |
| L2 | ShadowGen graded | holdout_fit | 0.959 | 1.00 | 1.00 | 1.00 | 0.050 | 0.77 | 0.63 |
| L2 | ShadowGen graded | unseen_fit | 0.994 | 1.00 | 1.00 | 1.00 | 0.022 | 0.77 | 0.82 |
| L2 | ShadowGen strict | holdout_fit_strict | 0.992 | 1.00 | 0.99 | 0.97 | 0.062 | 0.99 | 1.00 |
| L2 | ShadowGen strict | unseen_fit_strict | 0.997 | 0.94 | 0.94 | 0.87 | 0.027 | 0.99 | 1.00 |
| L2 | M2 | holdout_fit | 0.260 | -0.03 | -0.03 | -0.07 | 0.213 | 0.19 | 0.63 |
| L2 | M2 | unseen_fit | 0.119 | -0.03 | -0.03 | -0.07 | 0.207 | 0.19 | 0.82 |
| L3 | ShadowGen graded | holdout_fit | 1.000 | 1.00 | 1.00 | 1.00 | 0.006 | 0.61 | 0.59 |
| L3 | ShadowGen graded | unseen_fit | 1.000 | 1.00 | 1.00 | 1.00 | 0.002 | 0.61 | 0.61 |
| L3 | ShadowGen strict | holdout_fit_strict | 0.984 | 1.00 | 1.00 | 1.00 | 0.037 | 0.96 | 1.00 |
| L3 | ShadowGen strict | unseen_fit_strict | 0.991 | 1.00 | 1.00 | 1.00 | 0.026 | 0.96 | 1.00 |
| L3 | M2 | holdout_fit | -0.699 | -0.60 | -0.64 | -0.55 | 0.134 | 0.05 | 0.59 |
| L3 | M2 | unseen_fit | -0.708 | -0.60 | -0.64 | -0.55 | 0.139 | 0.05 | 0.61 |
| L4 | ShadowGen graded | holdout_fit | 0.964 | 1.00 | 1.00 | 1.00 | 0.050 | 0.76 | 0.74 |
| L4 | ShadowGen graded | unseen_fit | 0.966 | 1.00 | 1.00 | 1.00 | 0.049 | 0.76 | 0.74 |
| L4 | ShadowGen strict | holdout_fit_strict | 0.999 | 1.00 | 0.77 | 0.75 | 0.007 | 1.00 | 1.00 |
| L4 | ShadowGen strict | unseen_fit_strict | 0.999 | 1.00 | 0.77 | 0.75 | 0.007 | 1.00 | 1.00 |
| L4 | M2 | holdout_fit | -0.574 | -0.43 | -0.43 | -0.20 | 0.267 | 0.10 | 0.74 |
| L4 | M2 | unseen_fit | -0.573 | -0.43 | -0.43 | -0.20 | 0.266 | 0.10 | 0.74 |
| L5 | ShadowGen graded | holdout_fit | 0.983 | 0.89 | 0.89 | 0.73 | 0.060 | 0.71 | 0.53 |
| L5 | ShadowGen graded | unseen_fit | 0.965 | 0.89 | 0.89 | 0.73 | 0.073 | 0.71 | 0.51 |
| L5 | ShadowGen strict | holdout_fit_strict | 0.807 | 0.89 | 0.93 | 0.83 | 0.146 | 0.96 | 1.00 |
| L5 | ShadowGen strict | unseen_fit_strict | 0.659 | 0.89 | 0.93 | 0.83 | 0.176 | 0.96 | 1.00 |
| L5 | M2 | holdout_fit | -0.256 | 0.14 | 0.14 | 0.20 | 0.190 | 0.15 | 0.53 |
| L5 | M2 | unseen_fit | -0.221 | 0.14 | 0.14 | 0.20 | 0.171 | 0.15 | 0.51 |

## Per model: score against both references (graded and strict)

| log | model | graded | all | unseen | graded - unseen | strict | all strict | unseen strict | strict - unseen strict |
|---|---|---|---|---|---|---|---|---|---|
| L1 | Alpha | 0.228 | 0.245 | 0.221 | 0.008 | 0.001 | 0.000 | 0.000 | 0.001 |
| L1 | Alpha+ | 0.756 | 0.801 | 0.845 | -0.088 | 0.000 | 0.000 | 0.000 | 0.000 |
| L1 | Heuristics | 0.877 | 0.875 | 0.874 | 0.003 | 0.002 | 0.044 | 0.000 | 0.002 |
| L1 | Heuristics_Strict | 0.926 | 0.931 | 0.929 | -0.003 | 0.045 | 0.083 | 0.050 | -0.005 |
| L1 | Inductive_Strict | 0.976 | 1.000 | 1.000 | -0.024 | 0.639 | 0.990 | 0.987 | -0.348 |
| L1 | Inductive_Infrequent | 0.966 | 0.979 | 0.991 | -0.025 | 0.551 | 0.810 | 0.883 | -0.332 |
| L1 | Trace_Filtered | 0.585 | 0.622 | 0.609 | -0.024 | 0.000 | 0.010 | 0.000 | 0.000 |
| L1 | Flower | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| L2 | Alpha | 0.226 | 0.369 | 0.181 | 0.045 | 0.002 | 0.000 | 0.006 | -0.004 |
| L2 | Alpha+ | 0.674 | 0.531 | 0.743 | -0.069 | 0.000 | 0.000 | 0.000 | 0.000 |
| L2 | Heuristics | 0.993 | 0.998 | 0.987 | 0.006 | 0.811 | 0.965 | 0.752 | 0.059 |
| L2 | Heuristics_Strict | 0.998 | 1.000 | 0.996 | 0.001 | 0.935 | 0.992 | 0.921 | 0.014 |
| L2 | Inductive_Strict | 1.000 | 1.000 | 1.000 | -0.000 | 0.992 | 1.000 | 1.000 | -0.008 |
| L2 | Inductive_Infrequent | 0.990 | 0.997 | 0.978 | 0.012 | 0.812 | 0.965 | 0.733 | 0.079 |
| L2 | Trace_Filtered | 0.658 | 0.689 | 0.691 | -0.033 | 0.000 | 0.006 | 0.000 | 0.000 |
| L2 | Flower | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| L3 | Alpha | 0.394 | 0.410 | 0.392 | 0.002 | 0.000 | 0.000 | 0.000 | 0.000 |
| L3 | Alpha+ | 0.853 | 0.860 | 0.855 | -0.002 | 0.000 | 0.000 | 0.000 | 0.000 |
| L3 | Heuristics | 0.945 | 0.941 | 0.949 | -0.003 | 0.000 | 0.000 | 0.000 | 0.000 |
| L3 | Heuristics_Strict | 0.950 | 0.943 | 0.952 | -0.002 | 0.000 | 0.000 | 0.000 | 0.000 |
| L3 | Inductive_Strict | 1.000 | 1.000 | 1.000 | -0.000 | 0.965 | 1.000 | 1.000 | -0.035 |
| L3 | Inductive_Infrequent | 0.987 | 0.990 | 0.984 | 0.003 | 0.247 | 0.433 | 0.124 | 0.123 |
| L3 | Trace_Filtered | 0.697 | 0.750 | 0.707 | -0.009 | 0.000 | 0.008 | 0.000 | 0.000 |
| L3 | Flower | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| L4 | Alpha | 0.237 | 0.256 | 0.255 | -0.018 | 0.000 | 0.000 | 0.000 | 0.000 |
| L4 | Alpha+ | 0.501 | 0.261 | 0.265 | 0.235 | 0.000 | 0.000 | 0.000 | 0.000 |
| L4 | Heuristics | 0.880 | 0.874 | 0.873 | 0.007 | 0.000 | 0.000 | 0.000 | 0.000 |
| L4 | Heuristics_Strict | 0.939 | 0.963 | 0.961 | -0.022 | 0.000 | 0.000 | 0.000 | 0.000 |
| L4 | Inductive_Strict | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 0.999 | 0.999 | 0.001 |
| L4 | Inductive_Infrequent | 0.966 | 0.980 | 0.978 | -0.012 | 0.043 | 0.000 | 0.000 | 0.043 |
| L4 | Trace_Filtered | 0.612 | 0.707 | 0.651 | -0.039 | 0.000 | 0.000 | 0.000 | 0.000 |
| L4 | Flower | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| L5 | Alpha | 0.390 | 0.468 | 0.487 | -0.096 | 0.001 | 0.000 | 0.000 | 0.001 |
| L5 | Alpha+ | 0.286 | 0.518 | 0.580 | -0.294 | 0.000 | 0.000 | 0.000 | 0.000 |
| L5 | Heuristics | 0.839 | 0.836 | 0.830 | 0.009 | 0.004 | 0.056 | 0.019 | -0.015 |
| L5 | Heuristics_Strict | 0.896 | 0.918 | 0.903 | -0.007 | 0.020 | 0.069 | 0.060 | -0.040 |
| L5 | Inductive_Strict | 0.995 | 1.000 | 1.000 | -0.005 | 0.791 | 1.000 | 1.000 | -0.209 |
| L5 | Inductive_Infrequent | 0.996 | 0.975 | 0.967 | 0.029 | 0.957 | 0.390 | 0.168 | 0.789 |
| L5 | Trace_Filtered | 0.521 | 0.655 | 0.566 | -0.045 | 0.000 | 0.113 | 0.000 | -0.000 |
| L5 | Flower | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |

## Ranges over the logs

- shadowgen~holdout_fit: Pearson 0.959 to 1.000; Spearman 0.886 to 1.000 (ties 0.886 to 1.000); MAE 0.006 to 0.060
- shadowgen~unseen_fit: Pearson 0.965 to 1.000; Spearman 0.886 to 1.000 (ties 0.886 to 1.000); MAE 0.002 to 0.073
- shadowgen_strict~holdout_fit_strict: Pearson 0.807 to 0.999; Spearman 0.886 to 1.000 (ties 0.775 to 1.000); MAE 0.007 to 0.146
- shadowgen_strict~unseen_fit_strict: Pearson 0.659 to 1.000; Spearman 0.886 to 1.000 (ties 0.775 to 1.000); MAE 0.007 to 0.176
- m2~holdout_fit: Pearson -0.699 to 0.260; Spearman -0.600 to 0.143 (ties -0.638 to 0.143); MAE 0.134 to 0.267
- m2~unseen_fit: Pearson -0.708 to 0.119; Spearman -0.600 to 0.143 (ties -0.638 to 0.143); MAE 0.139 to 0.266
