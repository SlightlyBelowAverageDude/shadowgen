# Rule filter on the synthetic known systems (78 systems; seed 42; 1,000 shadow traces; N=6, tau=5, mle; v2.6 generator; rules from the 300-trace training log; pm4py 2.7.22.2)

Trees match the stored study on 78 of 78; logs resampled. Model errors: 0.

## A. Filter quality (per system)

| quantity | n | mean | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|---|
| shadow traces in the system's language, unfiltered | 78 | 0.600 | 0.000 | 0.225 | 0.671 | 1.000 | 1.000 |
| same, after the filter (all rules) | 76 | 0.720 | 0.000 | 0.459 | 0.864 | 1.000 | 1.000 |
| shadow traces kept (all rules) | 78 | 0.762 | 0.000 | 0.704 | 0.870 | 0.963 | 1.000 |
| invalid shadow traces removed (all rules) | 55 | 0.556 | 0.000 | 0.282 | 0.575 | 0.823 | 1.000 |
| valid shadow traces removed (all rules) | 73 | 0.041 | 0.000 | 0.008 | 0.020 | 0.048 | 0.373 |
| fresh unseen system traces the filter would remove (all rules) | 74 | 0.083 | 0.000 | 0.017 | 0.035 | 0.087 | 1.000 |
| same, after the filter (count and mandatory) | 76 | 0.693 | 0.000 | 0.429 | 0.803 | 1.000 | 1.000 |
| shadow traces kept (count and mandatory) | 78 | 0.795 | 0.000 | 0.801 | 0.942 | 0.976 | 1.000 |
| invalid shadow traces removed (count and mandatory) | 55 | 0.355 | 0.000 | 0.053 | 0.224 | 0.683 | 1.000 |
| valid shadow traces removed (count and mandatory) | 73 | 0.039 | 0.000 | 0.008 | 0.018 | 0.044 | 0.373 |
| fresh unseen system traces the filter would remove (count and mandatory) | 74 | 0.074 | 0.000 | 0.007 | 0.022 | 0.076 | 1.000 |
| same, after the filter (six rules and impl) | 74 | 0.817 | 0.000 | 0.674 | 1.000 | 1.000 | 1.000 |
| shadow traces kept (six rules and impl) | 78 | 0.662 | 0.000 | 0.379 | 0.799 | 0.937 | 1.000 |
| invalid shadow traces removed (six rules and impl) | 55 | 0.747 | 0.000 | 0.539 | 0.795 | 1.000 | 1.000 |
| valid shadow traces removed (six rules and impl) | 73 | 0.041 | 0.000 | 0.008 | 0.020 | 0.048 | 0.373 |
| fresh unseen system traces the filter would remove (six rules and impl) | 74 | 0.083 | 0.000 | 0.017 | 0.035 | 0.087 | 1.000 |
| same, after the filter (six rules, impl and balance) | 74 | 0.887 | 0.000 | 0.936 | 1.000 | 1.000 | 1.000 |
| shadow traces kept (six rules, impl and balance) | 78 | 0.607 | 0.000 | 0.293 | 0.670 | 0.927 | 1.000 |
| invalid shadow traces removed (six rules, impl and balance) | 55 | 0.910 | 0.466 | 0.842 | 0.996 | 1.000 | 1.000 |
| valid shadow traces removed (six rules, impl and balance) | 73 | 0.055 | 0.000 | 0.015 | 0.033 | 0.065 | 0.373 |
| fresh unseen system traces the filter would remove (six rules, impl and balance) | 74 | 0.099 | 0.000 | 0.029 | 0.057 | 0.096 | 1.000 |

Pooled over all 78000 shadow traces: valid 0.600; after the filter: all rules 0.753 (0.762 kept); count and mandatory 0.723 (0.795 kept); six rules and impl 0.867 (0.662 kept); six rules, impl and balance 0.931 (0.607 kept).
Systems with a valid share below 0.9: unfiltered 50; all rules 41 (no trace kept on 2); count and mandatory 46 (no trace kept on 2); six rules and impl 34 (no trace kept on 4); six rules, impl and balance 22 (no trace kept on 4).

## B. Score accuracy against the acceptance of unseen system traces

Per system: mean absolute error over the models; then mean and median over systems. Pooled: all (system, model) pairs.

| models | reading | predictor | systems | mean MAE | median MAE | pooled pairs | pooled MAE | pooled signed | pooled Pearson |
|---|---|---|---|---|---|---|---|---|---|
| six miners | strict | unfiltered | 74 | 0.172 | 0.124 | 444 | 0.172 | -0.105 | 0.776 |
| six miners | strict | filter all | 72 | 0.122 | 0.054 | 432 | 0.122 | -0.058 | 0.852 |
| six miners | strict | filter cm | 72 | 0.133 | 0.080 | 432 | 0.133 | -0.069 | 0.844 |
| six miners | strict | filter impl | 72 | 0.084 | 0.035 | 432 | 0.084 | -0.036 | 0.918 |
| six miners | strict | filter ext | 72 | 0.057 | 0.016 | 432 | 0.057 | -0.003 | 0.942 |
| six miners | strict | fitness | 74 | 0.126 | 0.076 | 444 | 0.126 | +0.111 | 0.870 |
| six miners | graded | unfiltered | 74 | 0.053 | 0.028 | 444 | 0.053 | -0.022 | 0.801 |
| six miners | graded | filter all | 72 | 0.040 | 0.014 | 432 | 0.040 | -0.007 | 0.825 |
| six miners | graded | filter cm | 72 | 0.041 | 0.018 | 432 | 0.041 | -0.009 | 0.825 |
| six miners | graded | filter impl | 72 | 0.027 | 0.013 | 432 | 0.027 | -0.000 | 0.903 |
| six miners | graded | filter ext | 72 | 0.024 | 0.007 | 432 | 0.024 | +0.003 | 0.905 |
| six miners | graded | fitness | 74 | 0.072 | 0.031 | 444 | 0.072 | +0.006 | 0.527 |
| Inductive_Strict | strict | unfiltered | 74 | 0.341 | 0.241 | 74 | 0.341 | -0.341 | 0.139 |
| Inductive_Strict | strict | filter all | 72 | 0.202 | 0.028 | 72 | 0.202 | -0.201 | -0.150 |
| Inductive_Strict | strict | filter cm | 72 | 0.230 | 0.101 | 72 | 0.230 | -0.229 | -0.169 |
| Inductive_Strict | strict | filter impl | 72 | 0.122 | 0.001 | 72 | 0.122 | -0.121 | -0.123 |
| Inductive_Strict | strict | filter ext | 72 | 0.065 | 0.000 | 72 | 0.065 | -0.063 | -0.080 |
| Inductive_Strict | strict | fitness | 74 | 0.001 | 0.000 | 74 | 0.001 | +0.001 | nan |
| Inductive_Strict | graded | unfiltered | 74 | 0.050 | 0.012 | 74 | 0.050 | -0.050 | 0.174 |
| Inductive_Strict | graded | filter all | 72 | 0.024 | 0.001 | 72 | 0.024 | -0.024 | -0.078 |
| Inductive_Strict | graded | filter cm | 72 | 0.026 | 0.003 | 72 | 0.026 | -0.025 | -0.083 |
| Inductive_Strict | graded | filter impl | 72 | 0.011 | 0.000 | 72 | 0.011 | -0.010 | -0.062 |
| Inductive_Strict | graded | filter ext | 72 | 0.008 | 0.000 | 72 | 0.008 | -0.008 | -0.044 |
| Inductive_Strict | graded | fitness | 74 | 0.000 | 0.000 | 74 | 0.000 | +0.000 | nan |
| Inductive_Infrequent | strict | unfiltered | 74 | 0.283 | 0.149 | 74 | 0.283 | -0.276 | 0.328 |
| Inductive_Infrequent | strict | filter all | 72 | 0.201 | 0.079 | 72 | 0.201 | -0.171 | 0.305 |
| Inductive_Infrequent | strict | filter cm | 72 | 0.229 | 0.112 | 72 | 0.229 | -0.201 | 0.283 |
| Inductive_Infrequent | strict | filter impl | 72 | 0.125 | 0.028 | 72 | 0.125 | -0.092 | 0.504 |
| Inductive_Infrequent | strict | filter ext | 72 | 0.083 | 0.000 | 72 | 0.083 | -0.026 | 0.472 |
| Inductive_Infrequent | strict | fitness | 74 | 0.026 | 0.000 | 74 | 0.026 | +0.026 | 0.919 |
| Inductive_Infrequent | graded | unfiltered | 74 | 0.043 | 0.012 | 74 | 0.043 | -0.043 | 0.135 |
| Inductive_Infrequent | graded | filter all | 72 | 0.024 | 0.003 | 72 | 0.024 | -0.023 | 0.017 |
| Inductive_Infrequent | graded | filter cm | 72 | 0.026 | 0.007 | 72 | 0.026 | -0.024 | 0.011 |
| Inductive_Infrequent | graded | filter impl | 72 | 0.011 | 0.001 | 72 | 0.011 | -0.009 | 0.200 |
| Inductive_Infrequent | graded | filter ext | 72 | 0.009 | 0.000 | 72 | 0.009 | -0.006 | 0.177 |
| Inductive_Infrequent | graded | fitness | 74 | 0.001 | 0.000 | 74 | 0.001 | +0.001 | 0.865 |

## B2. Six miners, every predictor on the same pairs (systems where the last filter keeps a trace)

| reading | predictor | pairs | pooled MAE | pooled signed |
|---|---|---|---|---|
| strict | unfiltered | 432 | 0.158 | -0.092 |
| strict | filter all | 432 | 0.122 | -0.058 |
| strict | filter cm | 432 | 0.133 | -0.069 |
| strict | filter impl | 432 | 0.084 | -0.036 |
| strict | filter ext | 432 | 0.057 | -0.003 |
| strict | fitness | 432 | 0.129 | +0.114 |
| graded | unfiltered | 432 | 0.049 | -0.018 |
| graded | filter all | 432 | 0.040 | -0.007 |
| graded | filter cm | 432 | 0.041 | -0.009 |
| graded | filter impl | 432 | 0.027 | -0.000 |
| graded | filter ext | 432 | 0.024 | +0.003 |
| graded | fitness | 432 | 0.074 | +0.006 |

## C. Poles (mean over systems): truth / unfiltered / filter all / filter cm / filter impl / filter ext / fitness

| model | strict | graded |
|---|---|---|
| Trace_Filtered | 0.000 / 0.037 / 0.040 / 0.040 / 0.041 / 0.041 / 0.202 | 0.759 / 0.741 / 0.747 / 0.746 / 0.753 / 0.756 / 0.773 |
| Flower | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |
