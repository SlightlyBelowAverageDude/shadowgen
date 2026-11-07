# Overfitting ladder, D1 (Sepsis), 1050 cases, 1 repetitions

random 70/30 case split with the p = 0 seeds of randomization_test.py; IM-k = Inductive Miner (noise 0) on the training cases of those variants; ShadowGen seed 42, one 1,000-trace draw, N=6, tau=5, mle, v2.6 core, scored with the full training split; Trie-k = prefix-tree trace model over the k most frequent variants, Trace-k = flat trace model (k = 50 and all only); truth = token replay of future cases with a variant absent from training; pm4py 2.7.22.2

Training variants 603, unseen share of the future 0.781, errors 0.

## A. Per family and k (mean over repetitions): training fitness / truth / ShadowGen

### Trie

| k | n | coverage | graded | strict |
|---|---|---|---|---|
| 10 | 1 | 0.129 | 0.737 / 0.693 / 0.657 | 0.129 / 0.000 / 0.003 |
| 50 | 1 | 0.248 | 0.830 / 0.783 / 0.737 | 0.248 / 0.000 / 0.000 |
| 100 | 1 | 0.316 | 0.790 / 0.704 / 0.675 | 0.316 / 0.000 / 0.000 |
| 200 | 1 | 0.452 | 0.888 / 0.793 / 0.756 | 0.452 / 0.000 / 0.000 |
| 400 | 1 | 0.724 | 0.943 / 0.802 / 0.769 | 0.724 / 0.000 / 0.000 |
| all | 1 | 1.000 | 1.000 / 0.818 / 0.791 | 1.000 / 0.000 / 0.000 |

### IM

| k | n | coverage | graded | strict |
|---|---|---|---|---|
| 10 | 1 | 0.129 | 0.760 / 0.724 / 0.652 | 0.161 / 0.037 / 0.010 |
| 50 | 1 | 0.248 | 0.986 / 0.983 / 0.953 | 0.703 / 0.679 / 0.446 |
| 100 | 1 | 0.316 | 1.000 / 1.000 / 0.983 | 0.985 / 0.984 / 0.668 |
| 200 | 1 | 0.452 | 1.000 / 1.000 / 0.984 | 0.995 / 0.988 / 0.691 |
| 400 | 1 | 0.724 | 1.000 / 1.000 / 0.981 | 1.000 / 0.996 / 0.704 |
| all | 1 | 1.000 | 1.000 / 1.000 / 0.982 | 1.000 / 0.996 / 0.704 |

### Trace

| k | n | coverage | graded | strict |
|---|---|---|---|---|
| 50 | 1 | 0.248 | 0.677 / 0.641 / 0.620 | 0.003 / 0.000 / 0.000 |
| all | 1 | 1.000 | 0.658 / 0.651 / 0.626 | 0.008 / 0.000 / 0.000 |

## B. Agreement with the truth over the ladder (median over repetitions)

| models | reading | predictor | Pearson | Spearman | MAE | spread predictor | spread truth |
|---|---|---|---|---|---|---|---|
| Trie | graded | ShadowGen | 0.993 | 1.000 | 0.035 | 0.134 | 0.125 |
| Trie | graded | fitness | 0.915 | 1.000 | 0.099 | 0.263 | 0.125 |
| Trie | strict | ShadowGen | - | - | 0.001 | 0.003 | 0.000 |
| Trie | strict | fitness | - | - | 0.478 | 0.871 | 0.000 |
| IM | graded | ShadowGen | 1.000 | 0.522 | 0.029 | 0.332 | 0.276 |
| IM | graded | fitness | 1.000 | 1.000 | 0.006 | 0.240 | 0.276 |
| IM | strict | ShadowGen | 0.999 | 1.000 | 0.243 | 0.694 | 0.959 |
| IM | strict | fitness | 1.000 | 1.000 | 0.027 | 0.839 | 0.959 |
| Trie and IM | graded | ShadowGen | 0.997 | 0.921 | 0.032 | 0.332 | 0.307 |
| Trie and IM | graded | fitness | 0.879 | 0.924 | 0.053 | 0.263 | 0.307 |
| Trie and IM | strict | ShadowGen | 0.999 | 0.971 | 0.122 | 0.704 | 0.996 |
| Trie and IM | strict | fitness | 0.741 | 0.591 | 0.253 | 0.871 | 0.996 |
