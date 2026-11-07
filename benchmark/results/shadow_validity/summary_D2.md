# Shadow trace validity, D2 (BPI2013_Incidents), 7554 cases, 3 repetitions pooled

real = future cases with a variant absent from training; shadow = ShadowGen's 1,000 traces per repetition (seed 42, N=6, tau=5, mle, v2.6). Invariants: see benchmark/shadow_validity_check.py.

Per repetition: rep 0: 397 real unseen cases, mutated share 0.017, duplicates kept 0, truncated 0; rep 1: 369 real unseen cases, mutated share 0.027, duplicates kept 0, truncated 0; rep 2: 378 real unseen cases, mutated share 0.022, duplicates kept 0, truncated 0

## A. Share of traces that violate an invariant

| reference | group | n | any | end | count | mandatory | ef | df | length |
|---|---|---|---|---|---|---|---|---|---|
| train | real | 1144 | 0.009 | 0.000 | 0.007 | 0.002 | 0.000 | 0.000 | 0.000 |
| train | shadow | 3000 | 0.009 | 0.000 | 0.001 | 0.000 | 0.005 | 0.006 | 0.000 |
| train | shadow_regular | 2934 | 0.001 | 0.000 | 0.001 | 0.000 | 0.001 | 0.000 | 0.000 |
| train | shadow_mutated | 66 | 0.333 | 0.000 | 0.000 | 0.000 | 0.212 | 0.288 | 0.000 |
| full | shadow | 3000 | 0.008 | 0.000 | 0.000 | 0.000 | 0.005 | 0.006 | 0.000 |
| full | shadow_regular | 2934 | 0.001 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 | 0.000 |
| full | shadow_mutated | 66 | 0.333 | 0.000 | 0.000 | 0.000 | 0.212 | 0.288 | 0.000 |

## B. Strict acceptance by group and invariant status

| model | group | n | accepted | n clean (train) | accepted, clean | n violating (train) | accepted, violating |
|---|---|---|---|---|---|---|---|
| Inductive_Strict | real | 1144 | 0.998 | 1134 | 1.000 | 10 | 0.800 |
| Inductive_Strict | shadow | 3000 | 0.995 | 2974 | 1.000 | 26 | 0.385 |
| Inductive_Strict | shadow_regular | 2934 | 0.999 | 2930 | 1.000 | 4 | 0.500 |
| Inductive_Strict | shadow_mutated | 66 | 0.788 | 44 | 1.000 | 22 | 0.364 |
| Inductive_Infrequent | real | 1144 | 0.726 | 1134 | 0.732 | 10 | 0.100 |
| Inductive_Infrequent | shadow | 3000 | 0.841 | 2974 | 0.848 | 26 | 0.077 |
| Inductive_Infrequent | shadow_regular | 2934 | 0.857 | 2930 | 0.858 | 4 | 0.000 |
| Inductive_Infrequent | shadow_mutated | 66 | 0.136 | 44 | 0.159 | 22 | 0.091 |

## C. Shadow traces by full-log invariant status

| model | n clean (full) | accepted, clean | n violating (full) | accepted, violating |
|---|---|---|---|---|
| Inductive_Strict | 2976 | 1.000 | 24 | 0.333 |
| Inductive_Infrequent | 2976 | 0.847 | 24 | 0.083 |

## D. Rejected shadow traces

| model | rejected | violates train | violates full | by kind (full): end, count, mandatory, ef, df, length | incomplete only (no missing token) | mutated |
|---|---|---|---|---|---|---|
| Inductive_Strict | 16 | 1.000 | 1.000 | 0.000, 0.000, 0.000, 1.000, 0.688, 0.000 | 0.000 | 0.875 |

Inductive_Strict, transitions with problems (share of rejected traces): Queued 1.00

| Inductive_Infrequent | 476 | 0.050 | 0.046 | 0.000, 0.000, 0.000, 0.034, 0.036, 0.000 | 0.000 | 0.120 |

Inductive_Infrequent, transitions with problems (share of rejected traces): Accepted 0.97, Queued 0.75, Completed 0.01

## E. Shadow traces that are a real unseen future variant

0.052 of the shadow traces equal a real unseen future variant (regular 0.054, mutated 0.000).

## F. Stored values reproduced

rep 0 Inductive_Strict: strict score 0.9940 (stored 0.994), truth 1.0 (stored 1.0)
rep 0 Inductive_Infrequent: strict score 0.8540 (stored 0.854), truth 0.7380352644836272 (stored 0.7380352644836272)
rep 1 Inductive_Strict: strict score 0.9950 (stored 0.995), truth 1.0 (stored 1.0)
rep 1 Inductive_Infrequent: strict score 0.8360 (stored 0.836), truth 0.7018970189701897 (stored 0.7018970189701896)
rep 2 Inductive_Strict: strict score 0.9950 (stored 0.995), truth 0.9947089947089947 (stored 0.9947089947089947)
rep 2 Inductive_Infrequent: strict score 0.8340 (stored 0.834), truth 0.7380952380952381 (stored 0.7380952380952381)

## G. First rejected shadow traces, Inductive_Strict, repetition 0

- Accepted > Accepted > Completed > Unmatched > Accepted > Accepted > Queued > Accepted > Queued > Accepted > Queued > Accepted > Completed > Completed  [mutated False; train ['ef']; full ['ef']; missing 1, remaining 1; problems ['Queued']]
- Accepted > Queued > Accepted > Queued > Accepted > Accepted > Accepted > Completed > Completed > Accepted > Accepted > Accepted > Completed > Unmatched > Accepted > Queued > Accepted > Queued > Accepted > Accepted > Accepted > Accepted > Completed > Completed  [mutated True; train ['ef']; full ['ef']; missing 1, remaining 1; problems ['Queued']]
- Queued > Accepted > Queued > Queued > Accepted > Completed > Unmatched > Accepted > Queued > Accepted > Queued > Accepted > Queued > Accepted > Queued > Accepted > Completed > Completed  [mutated True; train ['ef']; full ['ef']; missing 1, remaining 1; problems ['Queued']]
- Accepted > Accepted > Queued > Accepted > Completed > Accepted > Accepted > Unmatched > Accepted > Accepted > Queued > Accepted > Accepted > Accepted > Completed > Completed  [mutated True; train ['ef', 'df']; full ['ef', 'df']; missing 1, remaining 1; problems ['Queued']]
- Accepted > Accepted > Completed > Completed > Accepted > Accepted > Accepted > Accepted > Unmatched > Accepted > Queued > Accepted > Accepted > Queued > Accepted > Queued > Accepted > Accepted > Accepted > Queued > Accepted > Queued > Accepted > Accepted > Accepted > Completed > Completed  [mutated True; train ['ef', 'df']; full ['ef', 'df']; missing 1, remaining 1; problems ['Queued']]
- Accepted > Accepted > Queued > Queued > Accepted > Accepted > Queued > Unmatched > Accepted > Accepted > Completed > Completed > Accepted > Accepted > Queued > Queued > Accepted > Accepted > Queued > Accepted > Accepted > Queued > Accepted > Accepted > Accepted > Queued > Accepted > Accepted > Accepted > Completed > Completed  [mutated True; train ['ef', 'df']; full ['ef', 'df']; missing 1, remaining 1; problems ['Queued']]

## H. Inductive_Strict process tree, repetition 0

```
+( X( tau, *( 'Completed', tau ) ), X( tau, +( X( tau, *( 'Accepted', tau ) ), X( tau, ->( X( tau, *( 'Queued', tau ) ), X( tau, 'Unmatched' ) ) ) ) ) )
```
