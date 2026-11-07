# Rule filter on the shadow traces, D2 (BPI2013_Incidents), 7554 cases, 3 repetitions

Protocol: benchmark/shadow_filter_test.py. Truth = stored acceptance of future cases with a variant absent from training. Errors: none.

## A. What the filter removes

| rep | mutated share | shadow kept, all rules | shadow kept, count and mandatory | real unseen removed, all rules | real unseen removed, count and mandatory |
|---|---|---|---|---|---|
| 0 | 0.017 | 0.992 | 1.000 | 0.000 | 0.000 |
| 1 | 0.027 | 0.990 | 0.999 | 0.008 | 0.008 |
| 2 | 0.022 | 0.992 | 0.999 | 0.019 | 0.019 |

## B. Agreement with the truth (median over repetitions)

| models | n | reading | predictor | Pearson | Spearman | MAE | mean signed error |
|---|---|---|---|---|---|---|---|
| six miners | 6 | strict | unfiltered | 0.993 | 0.986 | 0.043 | +0.041 |
| six miners | 6 | strict | filter all | 0.993 | 0.985 | 0.044 | +0.044 |
| six miners | 6 | strict | filter cm | 0.993 | 0.986 | 0.043 | +0.041 |
| six miners | 6 | strict | fitness | 0.986 | 0.928 | 0.073 | +0.072 |
| six miners | 6 | graded | unfiltered | 0.962 | 1.000 | 0.052 | -0.007 |
| six miners | 6 | graded | filter all | 0.961 | 1.000 | 0.053 | -0.007 |
| six miners | 6 | graded | filter cm | 0.962 | 1.000 | 0.052 | -0.007 |
| six miners | 6 | graded | fitness | 0.937 | 1.000 | 0.068 | -0.003 |
| ladder (Trie, IM) | 12 | strict | unfiltered | 0.989 | 0.962 | 0.031 | +0.030 |
| ladder (Trie, IM) | 12 | strict | filter all | 0.989 | 0.988 | 0.032 | +0.032 |
| ladder (Trie, IM) | 12 | strict | filter cm | 0.989 | 0.962 | 0.031 | +0.030 |
| ladder (Trie, IM) | 12 | strict | fitness | 0.706 | 0.661 | 0.438 | +0.438 |
| ladder (Trie, IM) | 12 | graded | unfiltered | 0.959 | 0.947 | 0.029 | -0.021 |
| ladder (Trie, IM) | 12 | graded | filter all | 0.959 | 0.947 | 0.029 | -0.021 |
| ladder (Trie, IM) | 12 | graded | filter cm | 0.959 | 0.947 | 0.029 | -0.021 |
| ladder (Trie, IM) | 12 | graded | fitness | 0.819 | 0.704 | 0.074 | +0.074 |
| six miners and ladder | 18 | strict | unfiltered | 0.990 | 0.980 | 0.035 | +0.032 |
| six miners and ladder | 18 | strict | filter all | 0.990 | 0.986 | 0.035 | +0.034 |
| six miners and ladder | 18 | strict | filter cm | 0.990 | 0.980 | 0.035 | +0.032 |
| six miners and ladder | 18 | strict | fitness | 0.618 | 0.764 | 0.317 | +0.316 |
| six miners and ladder | 18 | graded | unfiltered | 0.953 | 0.965 | 0.037 | -0.016 |
| six miners and ladder | 18 | graded | filter all | 0.952 | 0.965 | 0.038 | -0.016 |
| six miners and ladder | 18 | graded | filter cm | 0.953 | 0.965 | 0.037 | -0.016 |
| six miners and ladder | 18 | graded | fitness | 0.877 | 0.828 | 0.072 | +0.049 |

## C. Per model (mean over repetitions): truth / unfiltered / filter all / filter cm / fitness

| model | strict | graded |
|---|---|---|
| Trace_Filtered | 0.000 / 0.000 / 0.000 / 0.000 / 0.010 | 0.692 / 0.633 / 0.633 / 0.633 / 0.712 |
| Alpha | 0.001 / 0.002 / 0.002 / 0.002 / 0.000 | 0.129 / 0.256 / 0.257 / 0.256 / 0.308 |
| Alpha+ | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.809 / 0.632 / 0.630 / 0.632 / 0.596 |
| Heuristics | 0.729 / 0.843 / 0.849 / 0.843 / 0.925 | 0.991 / 0.994 / 0.994 / 0.994 / 0.997 |
| Heuristics_Strict | 0.925 / 0.949 / 0.951 / 0.949 / 0.981 | 0.998 / 0.998 / 0.998 / 0.998 / 0.999 |
| Inductive_Strict | 0.998 / 0.995 / 1.000 / 0.995 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |
| Inductive_Infrequent | 0.726 / 0.841 / 0.848 / 0.842 / 0.929 | 0.986 / 0.991 / 0.991 / 0.991 / 0.996 |
| Flower | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |
| Trie-10 | 0.000 / 0.000 / 0.000 / 0.000 / 0.542 | 0.786 / 0.794 / 0.794 / 0.794 / 0.914 |
| Trie-50 | 0.000 / 0.000 / 0.000 / 0.000 / 0.714 | 0.739 / 0.734 / 0.734 / 0.734 / 0.934 |
| Trie-100 | 0.000 / 0.000 / 0.000 / 0.000 / 0.766 | 0.880 / 0.835 / 0.835 / 0.835 / 0.972 |
| Trie-200 | 0.000 / 0.000 / 0.000 / 0.000 / 0.816 | 0.845 / 0.796 / 0.796 / 0.796 / 0.971 |
| Trie-400 | 0.000 / 0.000 / 0.000 / 0.000 / 0.859 | 0.808 / 0.715 / 0.714 / 0.715 / 0.973 |
| Trie-all | 0.000 / 0.000 / 0.000 / 0.000 / 1.000 | 0.822 / 0.748 / 0.748 / 0.748 / 1.000 |
| IM-10 | 0.479 / 0.739 / 0.746 / 0.740 / 0.847 | 0.982 / 0.990 / 0.990 / 0.990 / 0.993 |
| IM-50 | 0.780 / 0.877 / 0.883 / 0.878 / 0.953 | 0.994 / 0.996 / 0.996 / 0.996 / 0.999 |
| IM-100 | 0.994 / 0.997 / 0.997 / 0.997 / 0.999 | 0.999 / 0.999 / 0.999 / 0.999 / 1.000 |
| IM-200 | 0.998 / 0.994 / 0.996 / 0.994 / 1.000 | 1.000 / 0.999 / 0.999 / 0.999 / 1.000 |
| IM-400 | 0.998 / 0.994 / 0.998 / 0.994 / 0.999 | 1.000 / 0.999 / 1.000 / 0.999 / 1.000 |
| IM-all | 0.998 / 0.995 / 1.000 / 0.995 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |

## D. Unfiltered score against the stored value

miner: largest difference strict 0.0000 (Trace_Filtered), graded 0.0152 (Trace_Filtered), 24 models.
ladder: largest difference strict 0.0000 (Trie-10), graded 0.0832 (Trie-400), 36 models.
