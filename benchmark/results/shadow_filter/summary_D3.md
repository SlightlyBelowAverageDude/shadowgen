# Rule filter on the shadow traces, D3 (BPI2017), 31509 cases, 1 repetitions

Protocol: benchmark/shadow_filter_test.py. Truth = stored acceptance of future cases with a variant absent from training. Errors: none.

## A. What the filter removes

| rep | mutated share | shadow kept, all rules | shadow kept, count and mandatory | real unseen removed, all rules | real unseen removed, count and mandatory |
|---|---|---|---|---|---|
| 0 | 0.026 | 0.956 | 0.959 | 0.002 | 0.001 |

## B. Agreement with the truth (median over repetitions)

| models | n | reading | predictor | Pearson | Spearman | MAE | mean signed error |
|---|---|---|---|---|---|---|---|
| six miners | 6 | strict | unfiltered | 1.000 | 1.000 | 0.010 | +0.002 |
| six miners | 6 | strict | filter all | 0.999 | 1.000 | 0.007 | +0.007 |
| six miners | 6 | strict | filter cm | 0.999 | 1.000 | 0.007 | +0.007 |
| six miners | 6 | strict | fitness | 0.951 | 1.000 | 0.073 | +0.073 |
| six miners | 6 | graded | unfiltered | 1.000 | 1.000 | 0.002 | -0.001 |
| six miners | 6 | graded | filter all | 1.000 | 1.000 | 0.003 | +0.000 |
| six miners | 6 | graded | filter cm | 1.000 | 1.000 | 0.003 | +0.000 |
| six miners | 6 | graded | fitness | 0.998 | 1.000 | 0.011 | +0.004 |

## C. Per model (mean over repetitions): truth / unfiltered / filter all / filter cm / fitness

| model | strict | graded |
|---|---|---|
| Trace_Filtered | 0.000 / 0.000 / 0.000 / 0.000 / 0.007 | 0.553 / 0.577 / 0.574 / 0.574 / 0.664 |
| Alpha | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.423 / 0.422 / 0.424 / 0.424 / 0.436 |
| Alpha+ | 0.043 / 0.053 / 0.055 / 0.055 / 0.180 | 0.859 / 0.861 / 0.864 / 0.863 / 0.882 |
| Heuristics | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.954 / 0.949 / 0.949 / 0.949 / 0.943 |
| Heuristics_Strict | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.956 / 0.952 / 0.953 / 0.953 / 0.945 |
| Inductive_Strict | 1.000 / 0.976 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |
| Inductive_Infrequent | 0.091 / 0.118 / 0.123 / 0.123 / 0.393 | 0.977 / 0.979 / 0.980 / 0.980 / 0.986 |
| Flower | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |

## D. Unfiltered score against the stored value

miner: largest difference strict 0.0000 (Trace_Filtered), graded 0.0157 (Trace_Filtered), 8 models.
