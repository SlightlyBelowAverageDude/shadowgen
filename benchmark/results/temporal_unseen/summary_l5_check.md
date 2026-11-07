# L5 strict-reading gap on the temporal split (temporal split 70/30 by case start; random split control seeds 0,1,2; shadow seed 42, K=1, N=6, tau=5, mle; v2.6 core; pm4py 2.7.22.2)

Train 176213 cases (1948-01-26 22:59:00+00:00 to 2018-08-31 13:54:00+00:00), test 75521 (2018-08-31 13:54:00+00:00 to 2019-01-17 14:32:00+00:00), unseen test 15618; last event 2020-04-09 21:59:00+00:00.

Training end activities (>= 1 % of training cases): {'Clear Invoice': 0.8557881654588481, 'Delete Purchase Order Item': 0.03290903622320714, 'Record Goods Receipt': 0.07178812005924648, 'Record Invoice Receipt': 0.017546946025548626}

Unseen test profile: {'prefix_of_training_variant': 0.4761813292354975, 'last_activity_is_training_end': 0.6281213983864772, 'seen_last_activity_is_training_end': 0.8875348480042736, 'train_last_activity_is_training_end': 0.9780322677668504}

Shadow log: {'n': 1000, 'mutated': 244, 'duplicates_kept': 0, 'truncated': 0, 'cap': 1000, 'seen_share': 0.0, 'prefix_of_training_variant': 0.055, 'last_activity_is_training_end': 0.901, 'lengths': {0.1: 4, 0.25: 5, 0.5: 9, 0.75: 15, 0.9: 42, 'mean': 19.352}}

Lengths: {'train': {0.1: 3, 0.25: 5, 0.5: 5, 0.75: 6, 0.9: 7, 'mean': 6.51656801711565}, 'test_unseen': {0.1: 4, 0.25: 6, 0.5: 7, 0.75: 8, 0.9: 11, 'mean': 10.347675758739916}}

## Inductive_Infrequent (68 transitions)

| set | n | strict | graded |
|---|---|---|---|
| shadow | 1000 | 0.957 | 0.996 |
| shadow_regular | 756 | 0.956 | 0.995 |
| shadow_mutated | 244 | 0.959 | 0.999 |
| train | 176213 | 0.987 | 0.999 |
| test_all | 75521 | 0.390 | 0.975 |
| test_seen | 59903 | 0.448 | 0.977 |
| test_unseen | 15618 | 0.168 | 0.967 |
| unseen, prefix | 7437 | 0.177 | 0.962 |
| unseen, not_prefix | 8181 | 0.160 | 0.971 |
| unseen, end_ok | 9810 | 0.154 | 0.970 |
| unseen, end_not_ok | 5808 | 0.191 | 0.961 |
| unseen, end_ok_not_prefix | 6346 | 0.147 | 0.972 |
| train, end_ok | 172342 | 0.989 | 1.000 |
| train, end_not_ok | 3871 | 0.892 | 0.987 |
| shadow, end_ok | 901 | 0.969 | 0.998 |
| shadow, end_not_ok | 99 | 0.848 | 0.974 |

Reproduces stored (fresh, stored): {'shadow_strict': [0.957, 0.957], 'shadow_graded': [0.9958436753455544, 0.9958436753455544], 'unseen_strict': [0.1678191829939813, 0.1678191829939813], 'unseen_graded': [0.9669023340638423, 0.9669023340638423]}

| decile | train from | train strict | test from | test strict | unseen n | unseen strict |
|---|---|---|---|---|---|---|
| 1 | 1948-01-26 | 0.985 | 2018-08-31 | 0.409 | 1494 | 0.177 |
| 2 | 2018-01-26 | 0.989 | 2018-09-11 | 0.391 | 1438 | 0.153 |
| 3 | 2018-02-19 | 0.988 | 2018-09-25 | 0.381 | 1351 | 0.165 |
| 4 | 2018-03-14 | 0.981 | 2018-10-06 | 0.362 | 1457 | 0.123 |
| 5 | 2018-04-06 | 0.988 | 2018-10-17 | 0.299 | 1817 | 0.125 |
| 6 | 2018-04-26 | 0.984 | 2018-10-29 | 0.394 | 1598 | 0.183 |
| 7 | 2018-05-23 | 0.986 | 2018-11-08 | 0.419 | 1303 | 0.250 |
| 8 | 2018-06-14 | 0.992 | 2018-11-19 | 0.387 | 1938 | 0.195 |
| 9 | 2018-07-10 | 0.988 | 2018-11-29 | 0.436 | 1424 | 0.173 |
| 10 | 2018-08-06 | 0.989 | 2018-12-11 | 0.425 | 1798 | 0.147 |

## Inductive_Strict (133 transitions)

| set | n | strict | graded |
|---|---|---|---|
| shadow | 1000 | 0.791 | 0.995 |
| shadow_regular | 756 | 0.747 | 0.994 |
| shadow_mutated | 244 | 0.926 | 0.999 |
| train | 176213 | 1.000 | 1.000 |
| test_all | 75521 | 1.000 | 1.000 |
| test_seen | 59903 | 1.000 | 1.000 |
| test_unseen | 15618 | 1.000 | 1.000 |
| unseen, prefix | 7437 | 1.000 | 1.000 |
| unseen, not_prefix | 8181 | 1.000 | 1.000 |
| unseen, end_ok | 9810 | 1.000 | 1.000 |
| unseen, end_not_ok | 5808 | 1.000 | 1.000 |
| unseen, end_ok_not_prefix | 6346 | 1.000 | 1.000 |
| train, end_ok | 172342 | 1.000 | 1.000 |
| train, end_not_ok | 3871 | 1.000 | 1.000 |
| shadow, end_ok | 901 | 0.782 | 0.995 |
| shadow, end_not_ok | 99 | 0.869 | 0.997 |

Reproduces stored (fresh, stored): {'shadow_strict': [0.791, 0.791], 'shadow_graded': [0.995299251294053, 0.9952992512940531], 'unseen_strict': [0.9998719426302983, 0.9998719426302983], 'unseen_graded': [0.9999954454157938, 0.9999954454157937]}

| decile | train from | train strict | test from | test strict | unseen n | unseen strict |
|---|---|---|---|---|---|---|
| 1 | 1948-01-26 | 1.000 | 2018-08-31 | 1.000 | 1494 | 0.999 |
| 2 | 2018-01-26 | 1.000 | 2018-09-11 | 1.000 | 1438 | 1.000 |
| 3 | 2018-02-19 | 1.000 | 2018-09-25 | 1.000 | 1351 | 1.000 |
| 4 | 2018-03-14 | 1.000 | 2018-10-06 | 1.000 | 1457 | 1.000 |
| 5 | 2018-04-06 | 1.000 | 2018-10-17 | 1.000 | 1817 | 1.000 |
| 6 | 2018-04-26 | 1.000 | 2018-10-29 | 1.000 | 1598 | 0.999 |
| 7 | 2018-05-23 | 1.000 | 2018-11-08 | 1.000 | 1303 | 1.000 |
| 8 | 2018-06-14 | 1.000 | 2018-11-19 | 1.000 | 1938 | 1.000 |
| 9 | 2018-07-10 | 1.000 | 2018-11-29 | 1.000 | 1424 | 1.000 |
| 10 | 2018-08-06 | 1.000 | 2018-12-11 | 1.000 | 1798 | 1.000 |

## Random 70/30 split (no time order)

| seed | model | shadow strict | train strict | test strict | unseen n | unseen strict | unseen graded |
|---|---|---|---|---|---|---|---|
| 0 | Inductive_Infrequent | 0.489 | 0.892 | 0.891 | 2884 | 0.670 | 0.985 |
| 0 | Inductive_Strict | 0.791 | 1.000 | 1.000 | 2884 | 1.000 | 1.000 |
| 1 | Inductive_Infrequent | 0.506 | 0.887 | 0.886 | 2915 | 0.668 | 0.985 |
| 1 | Inductive_Strict | 0.780 | 0.999 | 0.999 | 2915 | 0.988 | 1.000 |
| 2 | Inductive_Infrequent | 0.528 | 0.898 | 0.898 | 2958 | 0.691 | 0.986 |
| 2 | Inductive_Strict | 0.784 | 1.000 | 1.000 | 2958 | 0.999 | 1.000 |
