# Generator premise on the synthetic known systems (78 systems, seed 42; 1,000 shadow traces; N=6, tau=5, mle; v2.6 generator; pm4py 2.7.22.2)

Trees match the stored study on 78 of 78; logs resampled. Shadow log generated once per system from the 300-trace training log and replayed on the system itself.

| quantity | n | mean | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|---|
| shadow traces in the system's language (strict) | 78 | 0.595 | 0.000 | 0.217 | 0.704 | 1.000 | 1.000 |
| shadow log replay fitness on the system (graded) | 78 | 0.938 | 0.582 | 0.899 | 0.983 | 1.000 | 1.000 |
| strict, regular traces | 78 | 0.656 | 0.000 | 0.256 | 0.868 | 1.000 | 1.000 |
| strict, mutated traces | 49 | 0.099 | 0.000 | 0.000 | 0.015 | 0.135 | 0.509 |
| graded, regular traces | 78 | 0.940 | 0.582 | 0.900 | 0.991 | 1.000 | 1.000 |
| graded, mutated traces | 49 | 0.925 | 0.818 | 0.890 | 0.949 | 0.964 | 0.979 |
| shadow traces that are an unseen future variant (hit rate) | 78 | 0.232 | 0.000 | 0.073 | 0.191 | 0.325 | 0.914 |
| hit rate, regular | 78 | 0.260 | 0.000 | 0.074 | 0.236 | 0.360 | 0.914 |
| hit rate, mutated | 49 | 0.017 | 0.000 | 0.000 | 0.000 | 0.008 | 0.185 |
| share of unseen future variants covered by the shadow log | 74 | 0.356 | 0.000 | 0.083 | 0.206 | 0.596 | 1.000 |
| random traces in the system's language (strict) | 78 | 0.014 | 0.000 | 0.000 | 0.000 | 0.000 | 0.359 |
| random traces replay fitness (graded) | 78 | 0.487 | 0.333 | 0.443 | 0.477 | 0.524 | 0.812 |
| random traces that are an unseen future variant | 78 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| shadow traces whose variant is in the training log (duplicates kept) | 78 | 0.119 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| mutated share of the shadow log | 78 | 0.115 | 0.000 | 0.000 | 0.040 | 0.170 | 0.599 |

Pooled over all 78000 shadow traces: valid strict 0.595, valid graded 0.938, hit rate 0.232; random: valid strict 0.0142, hit rate 0.0000.

Valid share against the number of training variants: Pearson -0.323 (log variants); systems with valid share < 0.5: 30; < 0.9: 51.

Inductive strict net (n=74): strict score mean 0.646, strict reference mean 0.999, valid share mean 0.613; Pearson(strict score, valid share) 0.922; mean |strict score - valid share| 0.053; undershoot mean 0.353 against invalid share mean 0.387. Graded: score mean 0.949, valid graded mean 0.945, reference mean 1.000, mean |graded score - valid graded| 0.010.
