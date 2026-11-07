# Overfitting ladder, D1 (Sepsis), 1050 cases, 3 repetitions

random 70/30 case split with the p = 0 seeds of randomization_test.py; IM-k = Inductive Miner (noise 0) on the training cases of those variants; ShadowGen seed 42, one 1,000-trace draw, N=6, tau=5, mle, v2.6 core, scored with the full training split; Trie-k = prefix-tree trace model over the k most frequent variants, Trace-k = flat trace model (k = 50 and all only); truth = token replay of future cases with a variant absent from training; pm4py 2.7.22.2

Training variants 607, unseen share of the future 0.776, errors 0.

## A. Per family and k (mean over repetitions): training fitness / truth / ShadowGen

### Trie

| k | n | coverage | graded | strict |
|---|---|---|---|---|
| 10 | 3 | 0.133 | 0.724 / 0.670 / 0.641 | 0.142 / 0.010 / 0.007 |
| 50 | 3 | 0.242 | 0.817 / 0.765 / 0.724 | 0.242 / 0.000 / 0.000 |
| 100 | 3 | 0.310 | 0.823 / 0.749 / 0.722 | 0.310 / 0.000 / 0.000 |
| 200 | 3 | 0.446 | 0.878 / 0.777 / 0.752 | 0.446 / 0.000 / 0.000 |
| 400 | 3 | 0.718 | 0.944 / 0.807 / 0.773 | 0.718 / 0.000 / 0.000 |
| all | 3 | 1.000 | 1.000 / 0.814 / 0.785 | 1.000 / 0.000 / 0.000 |

### IM

| k | n | coverage | graded | strict |
|---|---|---|---|---|
| 10 | 3 | 0.133 | 0.830 / 0.803 / 0.755 | 0.413 / 0.298 / 0.254 |
| 50 | 3 | 0.242 | 0.989 / 0.985 / 0.953 | 0.771 / 0.701 / 0.487 |
| 100 | 3 | 0.310 | 0.999 / 0.999 / 0.978 | 0.971 / 0.953 / 0.653 |
| 200 | 3 | 0.446 | 1.000 / 0.999 / 0.979 | 0.991 / 0.982 / 0.675 |
| 400 | 3 | 0.718 | 1.000 / 1.000 / 0.979 | 0.999 / 0.992 / 0.691 |
| all | 3 | 1.000 | 1.000 / 1.000 / 0.981 | 1.000 / 0.993 / 0.694 |

### Trace

| k | n | coverage | graded | strict |
|---|---|---|---|---|
| 50 | 3 | 0.242 | 0.649 / 0.629 / 0.609 | 0.002 / 0.000 / 0.000 |
| all | 1 | 1.000 | 0.658 / 0.649 / 0.626 | 0.008 / 0.000 / 0.000 |

## B. Agreement with the truth over the ladder (median over repetitions)

| models | reading | predictor | Pearson | Spearman | MAE | spread predictor | spread truth |
|---|---|---|---|---|---|---|---|
| Trie | graded | ShadowGen | 0.992 | 1.000 | 0.029 | 0.132 | 0.122 |
| Trie | graded | fitness | 0.914 | 0.943 | 0.100 | 0.263 | 0.122 |
| Trie | strict | ShadowGen | 1.000 | 1.000 | 0.001 | 0.003 | 0.000 |
| Trie | strict | fitness | -0.487 | -0.655 | 0.475 | 0.863 | 0.000 |
| IM | graded | ShadowGen | 0.999 | 0.522 | 0.029 | 0.332 | 0.276 |
| IM | graded | fitness | 1.000 | 1.000 | 0.006 | 0.240 | 0.276 |
| IM | strict | ShadowGen | 0.999 | 0.986 | 0.243 | 0.652 | 0.926 |
| IM | strict | fitness | 0.999 | 1.000 | 0.032 | 0.784 | 0.926 |
| Trie and IM | graded | ShadowGen | 0.997 | 0.921 | 0.032 | 0.353 | 0.309 |
| Trie and IM | graded | fitness | 0.878 | 0.876 | 0.053 | 0.265 | 0.309 |
| Trie and IM | strict | ShadowGen | 0.999 | 0.971 | 0.122 | 0.704 | 0.996 |
| Trie and IM | strict | fitness | 0.742 | 0.591 | 0.253 | 0.863 | 0.996 |
