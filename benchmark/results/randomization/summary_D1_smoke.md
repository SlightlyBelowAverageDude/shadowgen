# Randomization test, D1 (Sepsis), 1050 cases, 1 repetitions

within-trace permutation of a share p of the cases; random 70/30 case split; models discovered on the training split; ShadowGen seed 42, one 1,000-trace draw, N=6, tau=5, mle, v2.6 core; truth = token replay of future cases with a variant absent from training; pm4py 2.7.22.2

## Log statistics per level (mean over repetitions)

| p | training variants | unseen share of the future | errors |
|---|---|---|---|
| 0.00 | 603 | 0.781 | 0 |
| 1.00 | 714 | 0.956 | 0 |

## A. Agreement with the truth over the six real miners (median over repetitions)

| metric | p | Pearson | Spearman | MAE | spread metric | spread truth |
|---|---|---|---|---|---|---|
| ShadowGen graded | 0.00 | 0.995 | 1.000 | 0.023 | 0.716 | 0.728 |
| ShadowGen graded | 1.00 | 0.925 | 0.714 | 0.111 | 0.666 | 0.866 |
| ShadowGen strict | 0.00 | 1.000 | 0.955 | 0.095 | 0.704 | 0.996 |
| ShadowGen strict | 1.00 | -0.424 | 0.058 | 0.358 | 0.289 | 0.993 |
| M2 | 0.00 | -0.441 | -0.429 | 0.186 | 0.087 | 0.728 |
| M2 | 1.00 | -0.375 | -0.086 | 0.232 | 0.140 | 0.866 |

## B. Per model and level (mean over repetitions)

### graded reading: truth / training / gap (training minus truth) / ShadowGen / M2

| model | p=0.00 | p=1.00 |
|---|---|---|
| Trace_Filtered | 0.597 / 0.629 / +0.033 / 0.577 / 0.040 | 0.453 / 0.453 / -0.000 / 0.410 / 0.083 |
| Alpha | 0.272 / 0.282 / +0.009 / 0.266 / 0.899 | 0.134 / 0.140 / +0.006 / 0.251 / 0.896 |
| Alpha+ | 0.823 / 0.802 / -0.021 / 0.747 / 0.906 | 0.624 / 0.624 / +0.000 / 0.437 / 0.898 |
| Heuristics | 0.919 / 0.920 / +0.001 / 0.914 / 0.818 | 0.910 / 0.903 / -0.008 / 0.917 / 0.762 |
| Heuristics_Strict | 0.932 / 0.929 / -0.003 / 0.922 / 0.883 | 0.817 / 0.819 / +0.002 / 0.839 / 0.802 |
| Inductive_Strict | 1.000 / 1.000 / +0.000 / 0.982 / 0.884 | 1.000 / 1.000 / +0.000 / 0.851 / 0.866 |
| Inductive_Infrequent | 0.990 / 0.978 / -0.012 / 0.969 / 0.851 | 0.964 / 0.954 / -0.010 / 0.780 / 0.902 |
| Flower | 1.000 / 1.000 / +0.000 / 1.000 / 0.899 | 1.000 / 1.000 / +0.000 / 1.000 / 0.896 |

### strict reading: truth / training / gap (training minus truth) / ShadowGen

| model | p=0.00 | p=1.00 |
|---|---|---|
| Trace_Filtered | 0.000 / 0.029 / +0.029 / 0.000 | 0.000 / 0.015 / +0.015 / 0.000 |
| Alpha | 0.000 / 0.000 / +0.000 / 0.000 | 0.000 / 0.000 / +0.000 / 0.036 |
| Alpha+ | 0.000 / 0.000 / +0.000 / 0.000 | 0.000 / 0.003 / +0.003 / 0.000 |
| Heuristics | 0.000 / 0.029 / +0.029 / 0.003 | 0.040 / 0.052 / +0.012 / 0.289 |
| Heuristics_Strict | 0.041 / 0.052 / +0.011 / 0.041 | 0.007 / 0.007 / +0.000 / 0.201 |
| Inductive_Strict | 0.996 / 1.000 / +0.004 / 0.704 | 0.993 / 1.000 / +0.007 / 0.034 |
| Inductive_Infrequent | 0.882 / 0.799 / -0.083 / 0.606 | 0.718 / 0.675 / -0.043 / 0.009 |
| Flower | 1.000 / 1.000 / +0.000 / 1.000 | 1.000 / 1.000 / +0.000 / 1.000 |

## C. Change from p = 0 to p = 1 (mean over repetitions)

| model | truth | ShadowGen | M2 | truth strict | ShadowGen strict |
|---|---|---|---|---|---|
| Trace_Filtered | -0.144 | -0.167 | +0.043 | +0.000 | +0.000 |
| Alpha | -0.138 | -0.015 | -0.003 | +0.000 | +0.036 |
| Alpha+ | -0.199 | -0.310 | -0.008 | +0.000 | +0.000 |
| Heuristics | -0.008 | +0.003 | -0.056 | +0.040 | +0.286 |
| Heuristics_Strict | -0.115 | -0.083 | -0.081 | -0.034 | +0.160 |
| Inductive_Strict | -0.000 | -0.131 | -0.018 | -0.003 | -0.670 |
| Inductive_Infrequent | -0.026 | -0.189 | +0.051 | -0.165 | -0.597 |
| Flower | +0.000 | +0.000 | -0.003 | +0.000 | +0.000 |

Correlation of the change over the six real miners: ShadowGen vs truth 0.407, M2 vs truth 0.058.
