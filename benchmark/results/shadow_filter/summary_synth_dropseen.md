# Seen shadow traces kept or dropped, synthetic known systems (78 systems; seed 42; 1,000 shadow traces; N=6, tau=5, mle; v2.6 generator; rules from the 300-trace training log; second reference from 25000 fresh traces where the first holds fewer than 250 unseen traces; pm4py 2.7.22.2)

Trees match the stored study on 78 of 78; logs resampled. Model errors: 0. Seen traces in the shadow log equal duplicates_kept on 78 of 78 systems.

## A. Padding

Systems where the generator keeps seen traces: 18 of 78 (more than 500 of 1,000 on 11; all 1,000 on 1).
Systems with no unseen trace in the 2,500 fresh traces: 4; of these, systems with no unseen shadow trace: 1.
Systems with no trace left to score after the drop: unfiltered 1, six rules 6, extended 8 (extended, keep: 4).

| padded system | variants in L | seen kept | unseen shadow traces (variants) | scored, extended drop | valid share of those | unseen fresh, 2,500 | unseen fresh, 25,000 |
|---|---|---|---|---|---|---|---|
| 6/1222 | 3 | 1000 | 0 (0) | 0 | - | 0 | 0 |
| 8/1148 | 9 | 892 | 108 (5) | 95 | 1.000 | 13 | 150 |
| 6/1037 | 10 | 876 | 124 (8) | 0 | - | 7 | 22 |
| 8/1185 | 10 | 850 | 150 (6) | 117 | 1.000 | 6 | 52 |
| 10/1185 | 14 | 838 | 162 (7) | 0 | - | 25 | 244 |
| 6/1148 | 9 | 831 | 169 (6) | 126 | 1.000 | 4 | 72 |
| 8/1111 | 10 | 797 | 203 (9) | 193 | 1.000 | 6 | 57 |
| 8/1222 | 9 | 776 | 224 (9) | 0 | - | 7 | 70 |
| 12/1111 | 10 | 682 | 318 (6) | 300 | 1.000 | 10 | 68 |
| 6/1518 | 10 | 666 | 334 (9) | 262 | 1.000 | 4 | 68 |
| 10/1111 | 9 | 615 | 385 (10) | 373 | 1.000 | 8 | 82 |
| 8/1518 | 27 | 153 | 847 (28) | 679 | 1.000 | 72 | 681 |
| 6/1296 | 15 | 99 | 901 (50) | 756 | 1.000 | 19 | 245 |
| 10/1518 | 42 | 97 | 903 (49) | 712 | 1.000 | 102 | 859 |
| 12/1518 | 50 | 29 | 971 (63) | 922 | 1.000 | 97 | 1010 |
| 8/1037 | 34 | 23 | 977 (73) | 736 | 1.000 | 76 | 826 |
| 10/1148 | 28 | 14 | 986 (276) | 921 | 1.000 | 135 | 1305 |
| 8/1296 | 32 | 8 | 992 (179) | 720 | 1.000 | 271 | - |

## B. Score accuracy, six miners, every predictor on the same pairs; reference = unseen part of 2,500 fresh traces

### all systems: 69 of 78 systems

| reading | predictor | pairs | MAE | signed | off by > 0.2 |
|---|---|---|---|---|---|
| strict | unfiltered, keep | 414 | 0.169 | -0.103 | 122 |
| strict | unfiltered, drop | 414 | 0.155 | -0.113 | 110 |
| strict | six rules, keep | 414 | 0.129 | -0.069 | 87 |
| strict | six rules, drop | 414 | 0.114 | -0.079 | 75 |
| strict | extended, keep | 414 | 0.059 | -0.008 | 36 |
| strict | extended, drop | 414 | 0.044 | -0.018 | 24 |
| strict | fitness | 414 | 0.127 | +0.113 | 100 |
| graded | unfiltered, keep | 414 | 0.047 | -0.018 | 23 |
| graded | unfiltered, drop | 414 | 0.039 | -0.025 | 17 |
| graded | six rules, keep | 414 | 0.038 | -0.008 | 19 |
| graded | six rules, drop | 414 | 0.029 | -0.014 | 13 |
| graded | extended, keep | 414 | 0.021 | +0.006 | 6 |
| graded | extended, drop | 414 | 0.012 | -0.001 | 0 |
| graded | fitness | 414 | 0.073 | +0.004 | 48 |

### padded (seen traces kept): 14 of 18 systems

| reading | predictor | pairs | MAE | signed | off by > 0.2 |
|---|---|---|---|---|---|
| strict | unfiltered, keep | 84 | 0.081 | +0.036 | 14 |
| strict | unfiltered, drop | 84 | 0.011 | -0.011 | 2 |
| strict | six rules, keep | 84 | 0.076 | +0.046 | 12 |
| strict | six rules, drop | 84 | 0.003 | -0.003 | 0 |
| strict | extended, keep | 84 | 0.073 | +0.049 | 12 |
| strict | extended, drop | 84 | 0.000 | +0.000 | 0 |
| strict | fitness | 84 | 0.150 | +0.123 | 21 |
| graded | unfiltered, keep | 84 | 0.044 | +0.031 | 6 |
| graded | unfiltered, drop | 84 | 0.003 | -0.000 | 0 |
| graded | six rules, keep | 84 | 0.046 | +0.034 | 6 |
| graded | six rules, drop | 84 | 0.003 | +0.002 | 0 |
| graded | extended, keep | 84 | 0.046 | +0.035 | 6 |
| graded | extended, drop | 84 | 0.003 | +0.002 | 0 |
| graded | fitness | 84 | 0.095 | +0.045 | 15 |

### no padding, scored set (extended) below 0.9 valid: 15 of 20 systems

| reading | predictor | pairs | MAE | signed | off by > 0.2 |
|---|---|---|---|---|---|
| strict | unfiltered, keep | 90 | 0.265 | -0.205 | 39 |
| strict | unfiltered, drop | 90 | 0.265 | -0.205 | 39 |
| strict | six rules, keep | 90 | 0.207 | -0.146 | 32 |
| strict | six rules, drop | 90 | 0.207 | -0.146 | 32 |
| strict | extended, keep | 90 | 0.160 | -0.088 | 23 |
| strict | extended, drop | 90 | 0.160 | -0.088 | 23 |
| strict | fitness | 90 | 0.111 | +0.111 | 18 |
| graded | unfiltered, keep | 90 | 0.058 | -0.041 | 1 |
| graded | unfiltered, drop | 90 | 0.058 | -0.041 | 1 |
| graded | six rules, keep | 90 | 0.044 | -0.021 | 1 |
| graded | six rules, drop | 90 | 0.044 | -0.021 | 1 |
| graded | extended, keep | 90 | 0.037 | -0.012 | 0 |
| graded | extended, drop | 90 | 0.037 | -0.012 | 0 |
| graded | fitness | 90 | 0.052 | +0.003 | 6 |

### no padding, scored set (extended) at least 0.9 valid: 40 of 40 systems

| reading | predictor | pairs | MAE | signed | off by > 0.2 |
|---|---|---|---|---|---|
| strict | unfiltered, keep | 240 | 0.164 | -0.114 | 69 |
| strict | unfiltered, drop | 240 | 0.164 | -0.114 | 69 |
| strict | six rules, keep | 240 | 0.118 | -0.080 | 43 |
| strict | six rules, drop | 240 | 0.118 | -0.080 | 43 |
| strict | extended, keep | 240 | 0.016 | +0.002 | 1 |
| strict | extended, drop | 240 | 0.016 | +0.002 | 1 |
| strict | fitness | 240 | 0.126 | +0.110 | 61 |
| graded | unfiltered, keep | 240 | 0.044 | -0.027 | 16 |
| graded | unfiltered, drop | 240 | 0.044 | -0.027 | 16 |
| graded | six rules, keep | 240 | 0.033 | -0.017 | 12 |
| graded | six rules, drop | 240 | 0.033 | -0.017 | 12 |
| graded | extended, keep | 240 | 0.006 | +0.002 | 0 |
| graded | extended, drop | 240 | 0.006 | +0.002 | 0 |
| graded | fitness | 240 | 0.074 | -0.009 | 27 |

## C. Systems with the second reference (unseen part of 25000 fresh traces): 25

Unseen traces in the second reference: median 681, min 22, max 2579. Strict reference values, first against second: mean absolute difference 0.001 over 150 pairs.

### padded: 13 of 16 systems

| reading | predictor | pairs | MAE | signed | off by > 0.2 |
|---|---|---|---|---|---|
| strict | unfiltered, keep | 78 | 0.081 | +0.045 | 12 |
| strict | unfiltered, drop | 78 | 0.005 | -0.005 | 0 |
| strict | six rules, keep | 78 | 0.079 | +0.052 | 12 |
| strict | six rules, drop | 78 | 0.000 | +0.000 | 0 |
| strict | extended, keep | 78 | 0.079 | +0.052 | 12 |
| strict | extended, drop | 78 | 0.000 | +0.000 | 0 |
| strict | fitness | 78 | 0.130 | +0.101 | 18 |
| graded | unfiltered, keep | 78 | 0.045 | +0.033 | 6 |
| graded | unfiltered, drop | 78 | 0.002 | -0.001 | 0 |
| graded | six rules, keep | 78 | 0.048 | +0.036 | 6 |
| graded | six rules, drop | 78 | 0.002 | +0.001 | 0 |
| graded | extended, keep | 78 | 0.048 | +0.036 | 6 |
| graded | extended, drop | 78 | 0.002 | +0.001 | 0 |
| graded | fitness | 78 | 0.082 | +0.048 | 12 |

### not padded: 7 of 9 systems

| reading | predictor | pairs | MAE | signed | off by > 0.2 |
|---|---|---|---|---|---|
| strict | unfiltered, keep | 42 | 0.255 | -0.115 | 15 |
| strict | unfiltered, drop | 42 | 0.255 | -0.115 | 15 |
| strict | six rules, keep | 42 | 0.256 | -0.111 | 15 |
| strict | six rules, drop | 42 | 0.256 | -0.111 | 15 |
| strict | extended, keep | 42 | 0.007 | -0.004 | 0 |
| strict | extended, drop | 42 | 0.007 | -0.004 | 0 |
| strict | fitness | 42 | 0.222 | +0.153 | 16 |
| graded | unfiltered, keep | 42 | 0.115 | -0.053 | 12 |
| graded | unfiltered, drop | 42 | 0.115 | -0.053 | 12 |
| graded | six rules, keep | 42 | 0.119 | -0.053 | 12 |
| graded | six rules, drop | 42 | 0.119 | -0.053 | 12 |
| graded | extended, keep | 42 | 0.006 | +0.004 | 0 |
| graded | extended, drop | 42 | 0.006 | +0.004 | 0 |
| graded | fitness | 42 | 0.123 | -0.028 | 9 |

## D. Poles (mean over systems with a value): reference / second reference / unfiltered, keep / unfiltered, drop / six rules, keep / six rules, drop / extended, keep / extended, drop / fitness

| model | group | strict | graded |
|---|---|---|---|
| Trace_Filtered | all | 0.000 / 0.000 / 0.039 / 0.000 / 0.043 / 0.000 / 0.044 / 0.000 / 0.203 | 0.765 / 0.836 / 0.746 / 0.749 / 0.749 / 0.747 / 0.758 / 0.756 / 0.775 |
| Trace_Filtered | padded | 0.000 / 0.000 / 0.168 / 0.000 / 0.183 / 0.000 / 0.183 / 0.000 / 0.290 | 0.873 / 0.883 / 0.858 / 0.878 / 0.860 / 0.883 / 0.860 / 0.883 / 0.855 |
| Flower | all | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |
| Flower | padded | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 / 1.000 |
