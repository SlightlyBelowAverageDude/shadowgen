# Overfitting ladder, D2 (BPI2013_Incidents), 7554 cases, 3 repetitions

random 70/30 case split with the p = 0 seeds of randomization_test.py; IM-k = Inductive Miner (noise 0) on the training cases of those variants; ShadowGen seed 42, one 1,000-trace draw, N=6, tau=5, mle, v2.6 core, scored with the full training split; Trie-k = prefix-tree trace model over the k most frequent variants, Trace-k = flat trace model (k = 50 and all only); truth = token replay of future cases with a variant absent from training; pm4py 2.7.22.2

Training variants 1145, unseen share of the future 0.168, errors 0.

## A. Per family and k (mean over repetitions): training fitness / truth / ShadowGen

### Trie

| k | n | coverage | graded | strict |
|---|---|---|---|---|
| 10 | 3 | 0.542 | 0.914 / 0.786 / 0.790 | 0.542 / 0.000 / 0.000 |
| 50 | 3 | 0.714 | 0.934 / 0.739 / 0.717 | 0.714 / 0.000 / 0.000 |
| 100 | 3 | 0.766 | 0.972 / 0.880 / 0.840 | 0.766 / 0.000 / 0.000 |
| 200 | 3 | 0.816 | 0.971 / 0.845 / 0.790 | 0.816 / 0.000 / 0.000 |
| 400 | 3 | 0.859 | 0.973 / 0.808 / 0.744 | 0.859 / 0.000 / 0.000 |
| all | 3 | 1.000 | 1.000 / 0.822 / 0.752 | 1.000 / 0.000 / 0.000 |

### IM

| k | n | coverage | graded | strict |
|---|---|---|---|---|
| 10 | 3 | 0.542 | 0.993 / 0.982 / 0.990 | 0.847 / 0.479 / 0.739 |
| 50 | 3 | 0.714 | 0.999 / 0.994 / 0.996 | 0.953 / 0.780 / 0.877 |
| 100 | 3 | 0.766 | 1.000 / 0.999 / 0.999 | 0.999 / 0.994 / 0.997 |
| 200 | 3 | 0.816 | 1.000 / 1.000 / 0.999 | 1.000 / 0.998 / 0.994 |
| 400 | 3 | 0.859 | 1.000 / 1.000 / 0.999 | 0.999 / 0.998 / 0.994 |
| all | 3 | 1.000 | 1.000 / 1.000 / 1.000 | 1.000 / 0.998 / 0.995 |

### Trace

| k | n | coverage | graded | strict |
|---|---|---|---|---|
| 50 | 3 | 0.714 | 0.717 / 0.713 / 0.634 | 0.018 / 0.000 / 0.000 |
| all | 1 | 1.000 | 0.683 / 0.672 / 0.600 | 0.002 / 0.000 / 0.000 |

## B. Agreement with the truth over the ladder (median over repetitions)

| models | reading | predictor | Pearson | Spearman | MAE | spread predictor | spread truth |
|---|---|---|---|---|---|---|---|
| Trie | graded | ShadowGen | 0.824 | 0.600 | 0.049 | 0.139 | 0.149 |
| Trie | graded | fitness | 0.670 | 0.429 | 0.145 | 0.087 | 0.149 |
| Trie | strict | ShadowGen | - | - | 0.000 | 0.000 | 0.000 |
| Trie | strict | fitness | - | - | 0.783 | 0.460 | 0.000 |
| IM | graded | ShadowGen | 0.997 | 0.829 | 0.002 | 0.010 | 0.018 |
| IM | graded | fitness | 0.982 | 0.899 | 0.003 | 0.007 | 0.018 |
| IM | strict | ShadowGen | 0.998 | 0.708 | 0.062 | 0.257 | 0.516 |
| IM | strict | fitness | 0.994 | 0.941 | 0.094 | 0.153 | 0.516 |
| Trie and IM | graded | ShadowGen | 0.976 | 0.930 | 0.025 | 0.301 | 0.271 |
| Trie and IM | graded | fitness | 0.819 | 0.704 | 0.074 | 0.087 | 0.271 |
| Trie and IM | strict | ShadowGen | 0.989 | 0.962 | 0.031 | 0.998 | 1.000 |
| Trie and IM | strict | fitness | 0.706 | 0.661 | 0.438 | 0.460 | 1.000 |
