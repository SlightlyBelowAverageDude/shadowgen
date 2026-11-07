# Rule filter on the shadow traces, D1 (Sepsis), 1050 cases, 3 repetitions

Protocol: benchmark/shadow_filter_test.py. Truth = stored acceptance of future cases with a variant absent from training. Errors: none.

## A. What the filter removes (all = six rules, cm = count and mandatory, impl = six rules and a implies b, ext = impl and balance)

| rep | mutated share | shadow kept, all | shadow kept, cm | shadow kept, impl | shadow kept, ext | real unseen removed, all | real unseen removed, cm | real unseen removed, impl | real unseen removed, ext |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.569 | 0.711 | 0.713 | 0.635 | 0.624 | 0.020 | 0.000 | 0.037 | 0.057 |
| 1 | 0.594 | 0.713 | 0.716 | 0.647 | 0.644 | 0.016 | 0.000 | 0.020 | 0.037 |
| 2 | 0.589 | 0.699 | 0.700 | 0.636 | 0.631 | 0.029 | 0.008 | 0.029 | 0.041 |

## B. Agreement with the truth (median over repetitions)

| models | n | reading | predictor | Pearson | Spearman | MAE | mean signed error |
|---|---|---|---|---|---|---|---|
| six miners | 6 | strict | unfiltered | 1.000 | 0.955 | 0.095 | -0.094 |
| six miners | 6 | strict | filter all | 1.000 | 1.000 | 0.011 | -0.009 |
| six miners | 6 | strict | filter cm | 1.000 | 1.000 | 0.011 | -0.009 |
| six miners | 6 | strict | filter impl | 1.000 | 1.000 | 0.005 | +0.004 |
| six miners | 6 | strict | filter ext | 1.000 | 1.000 | 0.005 | +0.004 |
| six miners | 6 | strict | fitness | 0.998 | 0.955 | 0.017 | -0.001 |
| six miners | 6 | graded | unfiltered | 0.993 | 1.000 | 0.027 | -0.026 |
| six miners | 6 | graded | filter all | 0.999 | 1.000 | 0.009 | -0.007 |
| six miners | 6 | graded | filter cm | 0.999 | 1.000 | 0.009 | -0.007 |
| six miners | 6 | graded | filter impl | 1.000 | 1.000 | 0.007 | -0.003 |
| six miners | 6 | graded | filter ext | 1.000 | 1.000 | 0.007 | -0.003 |
| six miners | 6 | graded | fitness | 0.998 | 1.000 | 0.010 | -0.005 |
| ladder (Trie, IM) | 12 | strict | unfiltered | 0.999 | 0.971 | 0.122 | -0.121 |
| ladder (Trie, IM) | 12 | strict | filter all | 1.000 | 0.971 | 0.015 | -0.007 |
| ladder (Trie, IM) | 12 | strict | filter cm | 1.000 | 0.971 | 0.016 | -0.008 |
| ladder (Trie, IM) | 12 | strict | filter impl | 1.000 | 1.000 | 0.008 | +0.005 |
| ladder (Trie, IM) | 12 | strict | filter ext | 1.000 | 1.000 | 0.009 | +0.005 |
| ladder (Trie, IM) | 12 | strict | fitness | 0.742 | 0.591 | 0.253 | +0.253 |
| ladder (Trie, IM) | 12 | graded | unfiltered | 0.997 | 0.921 | 0.032 | -0.032 |
| ladder (Trie, IM) | 12 | graded | filter all | 0.998 | 0.986 | 0.006 | -0.004 |
| ladder (Trie, IM) | 12 | graded | filter cm | 0.998 | 0.986 | 0.006 | -0.004 |
| ladder (Trie, IM) | 12 | graded | filter impl | 0.998 | 0.991 | 0.005 | +0.000 |
| ladder (Trie, IM) | 12 | graded | filter ext | 0.998 | 0.991 | 0.005 | +0.001 |
| ladder (Trie, IM) | 12 | graded | fitness | 0.878 | 0.876 | 0.053 | +0.053 |
| six miners and ladder | 18 | strict | unfiltered | 0.999 | 0.965 | 0.113 | -0.112 |
| six miners and ladder | 18 | strict | filter all | 1.000 | 0.979 | 0.014 | -0.009 |
| six miners and ladder | 18 | strict | filter cm | 1.000 | 0.979 | 0.014 | -0.009 |
| six miners and ladder | 18 | strict | filter impl | 1.000 | 1.000 | 0.007 | +0.004 |
| six miners and ladder | 18 | strict | filter ext | 1.000 | 1.000 | 0.007 | +0.004 |
| six miners and ladder | 18 | strict | fitness | 0.791 | 0.670 | 0.176 | +0.173 |
| six miners and ladder | 18 | graded | unfiltered | 0.994 | 0.955 | 0.029 | -0.029 |
| six miners and ladder | 18 | graded | filter all | 0.999 | 0.994 | 0.007 | -0.006 |
| six miners and ladder | 18 | graded | filter cm | 0.999 | 0.994 | 0.007 | -0.006 |
| six miners and ladder | 18 | graded | filter impl | 0.999 | 0.994 | 0.005 | -0.001 |
| six miners and ladder | 18 | graded | filter ext | 0.999 | 0.994 | 0.006 | -0.001 |
| six miners and ladder | 18 | graded | fitness | 0.946 | 0.847 | 0.038 | +0.034 |

## C. Per model (mean over repetitions): truth / unfiltered / filter all / filter cm / filter impl / filter ext / fitness

| model | strict | graded |
|---|---|---|
| Trace_Filtered | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.012 | 0.637 / 0.614 / 0.633 / 0.633 / 0.638 / 0.638 / 0.656 |
| Alpha | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.285 / 0.272 / 0.273 / 0.273 / 0.274 / 0.275 / 0.291 |
| Alpha+ | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.836 / 0.751 / 0.806 / 0.806 / 0.823 / 0.823 / 0.795 |
| Heuristics | 0.000 / 0.003 / 0.000 / 0.000 / 0.000 / 0.000 / 0.031 | 0.900 / 0.897 / 0.898 / 0.898 / 0.900 / 0.900 / 0.900 |
| Heuristics_Strict | 0.035 / 0.034 / 0.041 / 0.041 / 0.042 / 0.042 / 0.056 | 0.930 / 0.922 / 0.929 / 0.929 / 0.934 / 0.934 / 0.930 |
| Inductive_Strict | 0.993 / 0.694 / 0.976 / 0.974 / 1.000 / 1.000 / 1.000 | 1.000 / 0.981 / 0.999 / 0.999 / 1.000 / 1.000 / 1.000 |
| Inductive_Infrequent | 0.795 / 0.552 / 0.774 / 0.773 / 0.827 / 0.828 / 0.750 | 0.986 / 0.963 / 0.983 / 0.983 / 0.987 / 0.988 / 0.977 |
| Flower | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |
| Trie-10 | 0.010 / 0.007 / 0.010 / 0.010 / 0.009 / 0.010 / 0.142 | 0.670 / 0.642 / 0.665 / 0.665 / 0.667 / 0.667 / 0.724 |
| Trie-50 | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.242 | 0.765 / 0.723 / 0.752 / 0.752 / 0.758 / 0.759 / 0.817 |
| Trie-100 | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.310 | 0.749 / 0.721 / 0.748 / 0.748 / 0.756 / 0.756 / 0.823 |
| Trie-200 | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.446 | 0.777 / 0.745 / 0.776 / 0.776 / 0.783 / 0.784 / 0.878 |
| Trie-400 | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.718 | 0.807 / 0.771 / 0.800 / 0.800 / 0.806 / 0.807 / 0.944 |
| Trie-all | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 0.000 / 1.000 | 0.814 / 0.784 / 0.813 / 0.813 / 0.820 / 0.821 / 1.000 |
| IM-10 | 0.298 / 0.254 / 0.308 / 0.307 / 0.325 / 0.325 / 0.413 | 0.803 / 0.755 / 0.786 / 0.786 / 0.791 / 0.793 / 0.830 |
| IM-50 | 0.701 / 0.487 / 0.688 / 0.686 / 0.722 / 0.726 / 0.771 | 0.985 / 0.953 / 0.985 / 0.985 / 0.989 / 0.989 / 0.989 |
| IM-100 | 0.953 / 0.653 / 0.920 / 0.919 / 0.962 / 0.964 / 0.971 | 0.999 / 0.978 / 0.994 / 0.994 / 0.999 / 0.999 / 0.999 |
| IM-200 | 0.982 / 0.675 / 0.949 / 0.948 / 0.985 / 0.985 / 0.991 | 0.999 / 0.979 / 0.996 / 0.996 / 0.999 / 0.999 / 1.000 |
| IM-400 | 0.992 / 0.691 / 0.970 / 0.969 / 0.996 / 0.996 / 0.999 | 1.000 / 0.979 / 0.999 / 0.999 / 1.000 / 1.000 / 1.000 |
| IM-all | 0.993 / 0.694 / 0.976 / 0.974 / 1.000 / 1.000 / 1.000 | 1.000 / 0.981 / 0.999 / 0.999 / 1.000 / 1.000 / 1.000 |

## D. Unfiltered score against the stored value

miner: largest difference strict 0.0000 (Trace_Filtered), graded 0.0141 (Trace_Filtered), 24 models.
ladder: largest difference strict 0.0000 (Trie-10), graded 0.0107 (Trie-200), 36 models.
