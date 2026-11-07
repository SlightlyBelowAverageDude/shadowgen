# Alpha+ undershoot: score and unseen reference on the same net

| log | split | miner | score | reference | gap | len shadow | len unseen | reweighted score | reference on covered bins | within-bin gap | covered | miss term shadow / unseen | rem term shadow / unseen | regular / mutated |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | temporal | Alpha | 0.228 | 0.221 | +0.008 | 17.7 | 16.1 | 0.235 | 0.221 | 0.015 | 1.000 | 0.367 / 0.372 | 0.404 / 0.407 | 0.259 / 0.206 |
| L1 | temporal | Alpha+ | 0.756 | 0.845 | -0.088 | 17.7 | 16.1 | 0.762 | 0.845 | -0.083 | 1.000 | 0.071 / 0.034 | 0.172 / 0.121 | 0.754 / 0.758 |
| L1 | temporal | Heuristics | 0.877 | 0.874 | +0.003 | 17.7 | 16.1 | 0.869 | 0.874 | -0.005 | 1.000 | 0.057 / 0.058 | 0.065 / 0.067 | 0.873 / 0.880 |
| L1 | temporal | Heuristics_Strict | 0.926 | 0.929 | -0.003 | 17.7 | 16.1 | 0.922 | 0.929 | -0.007 | 1.000 | 0.039 / 0.038 | 0.035 / 0.034 | 0.925 / 0.926 |
| L1 | temporal | Inductive_Strict | 0.976 | 1.000 | -0.024 | 17.7 | 16.1 | 0.980 | 1.000 | -0.020 | 1.000 | 0.007 / 0.000 | 0.017 / 0.000 | 0.971 / 0.980 |
| L1 | temporal | Inductive_Infrequent | 0.966 | 0.991 | -0.025 | 17.7 | 16.1 | 0.969 | 0.991 | -0.022 | 1.000 | 0.011 / 0.002 | 0.023 / 0.007 | 0.955 / 0.973 |
| L1 | random | Alpha | 0.266 | 0.272 | -0.006 | 16.6 | 16.2 | 0.275 | 0.272 | 0.002 | 1.000 | 0.347 / 0.344 | 0.386 / 0.383 | 0.293 / 0.246 |
| L1 | random | Alpha+ | 0.747 | 0.823 | -0.076 | 16.6 | 16.2 | 0.753 | 0.823 | -0.070 | 1.000 | 0.076 / 0.039 | 0.177 / 0.138 | 0.744 / 0.749 |
| L1 | random | Heuristics | 0.914 | 0.919 | -0.004 | 16.6 | 16.2 | 0.911 | 0.919 | -0.008 | 1.000 | 0.045 / 0.039 | 0.041 / 0.042 | 0.912 / 0.916 |
| L1 | random | Heuristics_Strict | 0.922 | 0.932 | -0.010 | 16.6 | 16.2 | 0.919 | 0.932 | -0.012 | 1.000 | 0.041 / 0.036 | 0.037 / 0.032 | 0.922 / 0.922 |
| L1 | random | Inductive_Strict | 0.982 | 1.000 | -0.018 | 16.6 | 16.2 | 0.983 | 1.000 | -0.017 | 1.000 | 0.006 / 0.000 | 0.012 / 0.000 | 0.977 / 0.986 |
| L1 | random | Inductive_Infrequent | 0.969 | 0.990 | -0.022 | 16.6 | 16.2 | 0.970 | 0.990 | -0.020 | 1.000 | 0.010 / 0.002 | 0.022 / 0.007 | 0.962 / 0.974 |
| L2 | temporal | Alpha | 0.226 | 0.181 | +0.045 | 14.0 | 15.5 | 0.176 | 0.181 | -0.005 | 1.000 | 0.394 / 0.421 | 0.380 / 0.398 | 0.227 / 0.130 |
| L2 | temporal | Alpha+ | 0.674 | 0.743 | -0.069 | 14.0 | 15.5 | 0.743 | 0.743 | -0.000 | 1.000 | 0.145 / 0.111 | 0.181 / 0.146 | 0.672 / 0.832 |
| L2 | temporal | Heuristics | 0.993 | 0.987 | +0.006 | 14.0 | 15.5 | 0.993 | 0.987 | 0.006 | 1.000 | 0.003 / 0.007 | 0.003 / 0.007 | 0.994 / 0.967 |
| L2 | temporal | Heuristics_Strict | 0.998 | 0.996 | +0.001 | 14.0 | 15.5 | 0.998 | 0.996 | 0.002 | 1.000 | 0.001 / 0.002 | 0.001 / 0.002 | 0.998 / 0.979 |
| L2 | temporal | Inductive_Strict | 1.000 | 1.000 | -0.000 | 14.0 | 15.5 | 1.000 | 1.000 | -0.000 | 1.000 | 0.000 / 0.000 | 0.000 / 0.000 | 1.000 / 0.992 |
| L2 | temporal | Inductive_Infrequent | 0.990 | 0.978 | +0.012 | 14.0 | 15.5 | 0.989 | 0.978 | 0.011 | 1.000 | 0.005 / 0.010 | 0.005 / 0.012 | 0.990 / 0.960 |
| L2 | random | Alpha | 0.256 | 0.129 | +0.126 | 12.1 | 19.6 | 0.138 | 0.129 | 0.009 | 1.000 | 0.380 / 0.443 | 0.365 / 0.427 | 0.258 / 0.135 |
| L2 | random | Alpha+ | 0.631 | 0.808 | -0.177 | 12.1 | 19.6 | 0.799 | 0.808 | -0.009 | 1.000 | 0.166 / 0.081 | 0.203 / 0.111 | 0.627 / 0.859 |
| L2 | random | Heuristics | 0.995 | 0.992 | +0.003 | 12.1 | 19.6 | 0.993 | 0.992 | 0.002 | 1.000 | 0.003 / 0.004 | 0.003 / 0.004 | 0.995 / 0.976 |
| L2 | random | Heuristics_Strict | 0.998 | 0.998 | +0.000 | 12.1 | 19.6 | 0.998 | 0.998 | 0.000 | 1.000 | 0.001 / 0.001 | 0.001 / 0.001 | 0.998 / 0.984 |
| L2 | random | Inductive_Strict | 1.000 | 1.000 | -0.000 | 12.1 | 19.6 | 1.000 | 1.000 | -0.000 | 1.000 | 0.000 / 0.000 | 0.000 / 0.000 | 1.000 / 0.994 |
| L2 | random | Inductive_Infrequent | 0.992 | 0.987 | +0.006 | 12.1 | 19.6 | 0.989 | 0.987 | 0.002 | 1.000 | 0.004 / 0.007 | 0.004 / 0.007 | 0.993 / 0.954 |

## L1 temporal, Alpha+ by length bin (deciles of the unseen cases)

| length | shadow n | unseen cases | fit shadow | fit unseen |
|---|---|---|---|---|
| 1 to 9 | 97 | 15 | 0.494 | 0.596 |
| 9 to 11 | 78 | 25 | 0.691 | 0.742 |
| 11 to 12 | 39 | 21 | 0.747 | 0.831 |
| 12 to 13 | 67 | 21 | 0.749 | 0.865 |
| 13 to 14 | 83 | 28 | 0.796 | 0.873 |
| 14 to 15 | 96 | 18 | 0.833 | 0.895 |
| 15 to 17 | 118 | 37 | 0.835 | 0.903 |
| 17 to 19 | 80 | 24 | 0.764 | 0.860 |
| 19 to 23 | 122 | 22 | 0.799 | 0.879 |
| 23 to 128 | 220 | 28 | 0.782 | 0.885 |

Net: 18 transitions (2 silent), 18 places; labels missing from net []; transitions without input or output arcs ['Admission IC', 'Admission NC', 'CRP', 'ER Registration', 'LacticAcid', 'Leucocytes']

| activity | shadow: contain | shadow: problem rate | unseen: contain | unseen: problem rate |
|---|---|---|---|---|
| IV Antibiotics | 0.838 | 0.204 | 0.866 | 0.000 |
| IV Liquid | 0.730 | 0.210 | 0.791 | 0.000 |
| Release A | 0.681 | 0.341 | 0.749 | 0.201 |
| ER Sepsis Triage | 0.908 | 0.084 | 0.996 | 0.000 |
| ER Triage | 0.903 | 0.045 | 1.000 | 0.000 |
| Release C | 0.056 | 0.375 | 0.021 | 0.400 |
| Release B | 0.105 | 0.257 | 0.071 | 0.235 |
| ER Registration | 0.924 | 0.003 | 1.000 | 0.000 |
| Release D | 0.039 | 0.154 | 0.050 | 0.167 |
| Return ER | 0.347 | 0.006 | 0.255 | 0.016 |

## L1 random, Alpha+ by length bin (deciles of the unseen cases)

| length | shadow n | unseen cases | fit shadow | fit unseen |
|---|---|---|---|---|
| 2 to 8 | 66 | 13 | 0.411 | 0.566 |
| 8 to 11 | 128 | 35 | 0.590 | 0.603 |
| 11 to 12 | 60 | 20 | 0.735 | 0.804 |
| 12 to 13 | 70 | 17 | 0.746 | 0.831 |
| 13 to 14 | 70 | 30 | 0.842 | 0.893 |
| 14 to 15 | 86 | 23 | 0.849 | 0.927 |
| 15 to 16 | 73 | 22 | 0.860 | 0.900 |
| 16 to 19 | 143 | 35 | 0.813 | 0.904 |
| 19 to 24 | 166 | 26 | 0.775 | 0.863 |
| 24 to 119 | 138 | 25 | 0.785 | 0.870 |

Net: 18 transitions (2 silent), 20 places; labels missing from net []; transitions without input or output arcs ['Admission IC', 'Admission NC', 'CRP', 'ER Registration', 'LacticAcid', 'Leucocytes']

| activity | shadow: contain | shadow: problem rate | unseen: contain | unseen: problem rate |
|---|---|---|---|---|
| IV Antibiotics | 0.816 | 0.148 | 0.833 | 0.000 |
| IV Liquid | 0.706 | 0.170 | 0.736 | 0.000 |
| Release A | 0.699 | 0.368 | 0.736 | 0.232 |
| ER Sepsis Triage | 0.894 | 0.048 | 1.000 | 0.000 |
| Release B | 0.084 | 0.357 | 0.081 | 0.250 |
| Release C | 0.043 | 0.302 | 0.033 | 0.125 |
| ER Triage | 0.891 | 0.019 | 1.000 | 0.008 |
| ER Registration | 0.935 | 0.007 | 1.000 | 0.000 |
| Release E | 0.029 | 0.207 | 0.004 | 0.000 |
| Release D | 0.058 | 0.293 | 0.024 | 0.500 |

## L2 temporal, Alpha+ by length bin (deciles of the unseen cases)

| length | shadow n | unseen cases | fit shadow | fit unseen |
|---|---|---|---|---|
| 1 to 6 | 201 | 13 | 0.294 | 0.471 |
| 6 to 9 | 122 | 14 | 0.590 | 0.527 |
| 9 to 11 | 74 | 18 | 0.677 | 0.671 |
| 11 to 13 | 101 | 15 | 0.735 | 0.720 |
| 13 to 15 | 70 | 22 | 0.766 | 0.764 |
| 15 to 17 | 95 | 14 | 0.794 | 0.798 |
| 17 to 18 | 46 | 8 | 0.816 | 0.812 |
| 18 to 22 | 132 | 25 | 0.837 | 0.824 |
| 22 to 25 | 42 | 12 | 0.860 | 0.850 |
| 25 to 69 | 117 | 24 | 0.901 | 0.876 |

Net: 6 transitions (2 silent), 6 places; labels missing from net []; transitions without input or output arcs ['Completed', 'Queued']

| activity | shadow: contain | shadow: problem rate | unseen: contain | unseen: problem rate |
|---|---|---|---|---|
| Accepted | 0.999 | 1.000 | 0.994 | 1.000 |
| Unmatched | 0.008 | 0.000 | -- | -- |
| Completed | 0.999 | 0.000 | 0.958 | 0.000 |
| Queued | 0.789 | 0.000 | 0.939 | 0.000 |

## L2 random, Alpha+ by length bin (deciles of the unseen cases)

| length | shadow n | unseen cases | fit shadow | fit unseen |
|---|---|---|---|---|
| 2 to 11 | 491 | 28 | 0.445 | 0.601 |
| 11 to 13 | 91 | 35 | 0.731 | 0.719 |
| 13 to 15 | 89 | 55 | 0.771 | 0.770 |
| 15 to 16 | 39 | 30 | 0.790 | 0.795 |
| 16 to 17 | 39 | 24 | 0.805 | 0.801 |
| 17 to 19 | 61 | 56 | 0.818 | 0.819 |
| 19 to 22 | 70 | 50 | 0.843 | 0.839 |
| 22 to 25 | 28 | 25 | 0.863 | 0.862 |
| 25 to 31 | 54 | 50 | 0.882 | 0.878 |
| 31 to 91 | 38 | 44 | 0.909 | 0.910 |

Net: 6 transitions (2 silent), 6 places; labels missing from net []; transitions without input or output arcs ['Completed', 'Queued']

| activity | shadow: contain | shadow: problem rate | unseen: contain | unseen: problem rate |
|---|---|---|---|---|
| Accepted | 0.998 | 1.000 | 1.000 | 1.000 |
| Unmatched | 0.012 | 0.000 | -- | -- |
| Completed | 1.000 | 0.000 | 0.992 | 0.000 |
| Queued | 0.756 | 0.000 | 0.987 | 0.000 |
