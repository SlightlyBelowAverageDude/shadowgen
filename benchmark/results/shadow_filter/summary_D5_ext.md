# Rule filter on the shadow traces, D5 (BPI2019), 251734 cases, 2 repetitions

Protocol: benchmark/shadow_filter_test.py. Truth = stored acceptance of future cases with a variant absent from training. Errors: none.

## A. What the filter removes (all = six rules, cm = count and mandatory, impl = six rules and a implies b, ext = impl and balance)

| rep | mutated share | shadow kept, all | shadow kept, cm | shadow kept, impl | shadow kept, ext | real unseen removed, all | real unseen removed, cm | real unseen removed, impl | real unseen removed, ext |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.232 | 0.749 | 0.775 | 0.724 | 0.720 | 0.016 | 0.002 | 0.016 | 0.018 |
| 1 | 0.239 | 0.759 | 0.784 | 0.734 | 0.729 | 0.014 | 0.002 | 0.014 | 0.017 |

## B. Agreement with the truth (median over repetitions)

| models | n | reading | predictor | Pearson | Spearman | MAE | mean signed error |
|---|---|---|---|---|---|---|---|
| six miners | 6 | strict | unfiltered | 0.996 | 0.963 | 0.076 | -0.052 |
| six miners | 6 | strict | filter all | 1.000 | 1.000 | 0.003 | -0.003 |
| six miners | 6 | strict | filter cm | 1.000 | 1.000 | 0.003 | -0.003 |
| six miners | 6 | strict | filter impl | 1.000 | 1.000 | 0.003 | +0.001 |
| six miners | 6 | strict | filter ext | 1.000 | 1.000 | 0.003 | +0.002 |
| six miners | 6 | strict | fitness | 0.987 | 0.977 | 0.045 | +0.045 |
| six miners | 6 | graded | unfiltered | 0.987 | 0.943 | 0.036 | -0.005 |
| six miners | 6 | graded | filter all | 1.000 | 1.000 | 0.008 | -0.003 |
| six miners | 6 | graded | filter cm | 1.000 | 1.000 | 0.008 | -0.003 |
| six miners | 6 | graded | filter impl | 1.000 | 1.000 | 0.008 | -0.002 |
| six miners | 6 | graded | filter ext | 1.000 | 1.000 | 0.008 | -0.002 |
| six miners | 6 | graded | fitness | 0.997 | 1.000 | 0.021 | +0.014 |

## C. Per model (mean over repetitions): truth / unfiltered / filter all / filter cm / filter impl / filter ext / fitness

| model | strict | graded |
|---|---|---|
| Trace_Filtered | 0.007 / 0.004 / 0.005 / 0.005 / 0.005 / 0.005 / 0.115 | 0.480 / 0.541 / 0.538 / 0.536 / 0.535 / 0.535 / 0.681 |
| Alpha | 0.000 / 0.005 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.275 / 0.367 / 0.290 / 0.289 / 0.291 / 0.291 / 0.343 |
| Alpha+ | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.369 / 0.301 / 0.360 / 0.364 / 0.362 / 0.361 / 0.372 |
| Heuristics | 0.001 / 0.007 / 0.001 / 0.001 / 0.001 / 0.001 / 0.022 | 0.873 / 0.852 / 0.857 / 0.857 / 0.858 / 0.859 / 0.879 |
| Heuristics_Strict | 0.009 / 0.071 / 0.005 / 0.004 / 0.005 / 0.005 / 0.047 | 0.922 / 0.914 / 0.914 / 0.915 / 0.917 / 0.917 / 0.923 |
| Inductive_Strict | 1.000 / 0.780 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 0.995 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |
| Inductive_Infrequent | 0.680 / 0.517 / 0.667 / 0.663 / 0.690 / 0.692 / 0.892 | 0.985 / 0.964 / 0.983 / 0.984 / 0.986 / 0.986 / 0.993 |
| Flower | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |

## D. Unfiltered score against the stored value

miner: largest difference strict 0.0150 (Trace_Filtered), graded 0.0195 (Trace_Filtered), 16 models.
