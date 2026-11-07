# Rule filter on the synthetic known systems (78 systems; seed 42; 1,000 shadow traces; N=6, tau=5, mle; v2.6 generator; rules from the 300-trace training log; pm4py 2.7.22.2)

Trees match the stored study on 78 of 78; logs resampled. Model errors: 0.

## A. Filter quality (per system)

| quantity | n | mean | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|---|
| shadow traces in the system's language, unfiltered | 78 | 0.593 | 0.000 | 0.176 | 0.707 | 1.000 | 1.000 |
| same, after the filter (all rules) | 76 | 0.717 | 0.000 | 0.491 | 0.864 | 1.000 | 1.000 |
| shadow traces kept (all rules) | 78 | 0.756 | 0.000 | 0.695 | 0.845 | 0.958 | 1.000 |
| invalid shadow traces removed (all rules) | 55 | 0.563 | 0.000 | 0.297 | 0.638 | 0.823 | 1.000 |
| valid shadow traces removed (all rules) | 73 | 0.038 | 0.000 | 0.007 | 0.018 | 0.046 | 0.252 |
| fresh unseen system traces the filter would remove (all rules) | 74 | 0.090 | 0.000 | 0.014 | 0.035 | 0.082 | 1.000 |
| same, after the filter (count and mandatory) | 76 | 0.684 | 0.000 | 0.438 | 0.782 | 1.000 | 1.000 |
| shadow traces kept (count and mandatory) | 78 | 0.795 | 0.000 | 0.795 | 0.942 | 0.978 | 1.000 |
| invalid shadow traces removed (count and mandatory) | 55 | 0.363 | 0.000 | 0.072 | 0.234 | 0.694 | 1.000 |
| valid shadow traces removed (count and mandatory) | 73 | 0.035 | 0.000 | 0.005 | 0.018 | 0.041 | 0.252 |
| fresh unseen system traces the filter would remove (count and mandatory) | 74 | 0.082 | 0.000 | 0.007 | 0.023 | 0.070 | 1.000 |

Pooled over all 78000 shadow traces: valid 0.593; after the filter with all rules 0.749 (0.756 kept); with count and mandatory 0.714 (0.795 kept).
Systems with a valid share below 0.9: unfiltered 50, all rules 43, count and mandatory 47.

## B. Score accuracy against the acceptance of unseen system traces

Per system: mean absolute error over the models; then mean and median over systems. Pooled: all (system, model) pairs.

| models | reading | predictor | systems | mean MAE | median MAE | pooled pairs | pooled MAE | pooled signed | pooled Pearson |
|---|---|---|---|---|---|---|---|---|---|
| six miners | strict | unfiltered | 74 | 0.175 | 0.119 | 444 | 0.175 | -0.108 | 0.772 |
| six miners | strict | filter all | 72 | 0.123 | 0.062 | 432 | 0.123 | -0.054 | 0.854 |
| six miners | strict | filter cm | 72 | 0.134 | 0.076 | 432 | 0.134 | -0.068 | 0.844 |
| six miners | strict | fitness | 74 | 0.127 | 0.075 | 444 | 0.127 | +0.113 | 0.870 |
| six miners | graded | unfiltered | 74 | 0.053 | 0.024 | 444 | 0.053 | -0.021 | 0.801 |
| six miners | graded | filter all | 72 | 0.040 | 0.014 | 432 | 0.040 | -0.005 | 0.823 |
| six miners | graded | filter cm | 72 | 0.041 | 0.016 | 432 | 0.041 | -0.008 | 0.826 |
| six miners | graded | fitness | 74 | 0.071 | 0.030 | 444 | 0.071 | +0.010 | 0.545 |
| Inductive_Strict | strict | unfiltered | 74 | 0.350 | 0.265 | 74 | 0.350 | -0.350 | 0.063 |
| Inductive_Strict | strict | filter all | 72 | 0.204 | 0.057 | 72 | 0.204 | -0.203 | -0.155 |
| Inductive_Strict | strict | filter cm | 72 | 0.238 | 0.173 | 72 | 0.238 | -0.238 | -0.172 |
| Inductive_Strict | strict | fitness | 74 | 0.001 | 0.000 | 74 | 0.001 | +0.001 | nan |
| Inductive_Strict | graded | unfiltered | 74 | 0.049 | 0.013 | 74 | 0.049 | -0.049 | 0.053 |
| Inductive_Strict | graded | filter all | 72 | 0.024 | 0.002 | 72 | 0.024 | -0.024 | -0.095 |
| Inductive_Strict | graded | filter cm | 72 | 0.025 | 0.006 | 72 | 0.025 | -0.025 | -0.101 |
| Inductive_Strict | graded | fitness | 74 | 0.000 | 0.000 | 74 | 0.000 | +0.000 | nan |
| Inductive_Infrequent | strict | unfiltered | 74 | 0.301 | 0.228 | 74 | 0.301 | -0.295 | 0.349 |
| Inductive_Infrequent | strict | filter all | 72 | 0.205 | 0.112 | 72 | 0.205 | -0.173 | 0.255 |
| Inductive_Infrequent | strict | filter cm | 72 | 0.238 | 0.173 | 72 | 0.238 | -0.207 | 0.224 |
| Inductive_Infrequent | strict | fitness | 74 | 0.027 | 0.000 | 74 | 0.027 | +0.025 | 0.917 |
| Inductive_Infrequent | graded | unfiltered | 74 | 0.044 | 0.013 | 74 | 0.044 | -0.044 | 0.150 |
| Inductive_Infrequent | graded | filter all | 72 | 0.024 | 0.005 | 72 | 0.024 | -0.022 | -0.014 |
| Inductive_Infrequent | graded | filter cm | 72 | 0.025 | 0.008 | 72 | 0.025 | -0.024 | -0.019 |
| Inductive_Infrequent | graded | fitness | 74 | 0.001 | 0.000 | 74 | 0.001 | +0.000 | 0.885 |

## C. Poles (mean over systems): truth / unfiltered / filter all / filter cm / fitness

| model | strict | graded |
|---|---|---|
| Trace_Filtered | 0.000 / 0.043 / 0.045 / 0.045 / 0.209 | 0.760 / 0.740 / 0.742 / 0.741 / 0.775 |
| Flower | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |
