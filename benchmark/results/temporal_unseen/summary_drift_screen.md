# Drift screen of the temporal splits

Activity case share in training and future; random split (seed 0, same sizes) as calibration.

| log | split | unseen share | max abs shift | shifts above 0.1 | rise above 0.2 | fall above 0.2 | labels new in future | future with new DF pair | unseen with new DF pair |
|---|---|---|---|---|---|---|---|---|---|
| L1 | temporal | 0.759 | 0.092 | 0 | -- | -- | 0 | 0.035 | 0.046 |
| L1 | random | 0.781 | 0.059 | 0 | -- | -- | 0 | 0.016 | 0.020 |
| L2 | temporal | 0.073 | 0.208 | 1 | -- | Queued | 0 | 0.000 | 0.000 |
| L2 | random | 0.175 | 0.007 | 0 | -- | -- | 0 | 0.000 | 0.000 |
| L3 | temporal | 0.462 | 0.034 | 0 | -- | -- | 0 | 0.003 | 0.006 |
| L3 | random | 0.461 | 0.007 | 0 | -- | -- | 1 | 0.001 | 0.002 |
| L4 | temporal | 0.640 | 0.938 | 8 | finish pre-check; create | abort payment; revoke decision; save; check | 0 | 0.010 | 0.016 |
| L4 | random | 0.616 | 0.010 | 0 | -- | -- | 0 | 0.003 | 0.004 |
| L5 | temporal | 0.207 | 0.588 | 4 | Create Purchase Requisition Item | Clear Invoice | 1 | 0.006 | 0.031 |
| L5 | random | 0.038 | 0.002 | 0 | -- | -- | 0 | 0.000 | 0.011 |

## Largest temporal shifts

| log | activity | train | future | future unseen |
|---|---|---|---|---|
| L1 | Return ER | 0.307 | 0.216 | 0.255 |
| L1 | Release A | 0.648 | 0.619 | 0.749 |
| L1 | IV Antibiotics | 0.790 | 0.768 | 0.866 |
| L1 | Release D | 0.016 | 0.038 | 0.050 |
| L1 | Admission IC | 0.110 | 0.092 | 0.121 |
| L2 | Queued | 0.660 | 0.452 | 0.939 |
| L2 | Completed | 1.000 | 0.997 | 0.958 |
| L2 | Unmatched | 0.001 | 0.001 | 0.000 |
| L2 | Accepted | 1.000 | 1.000 | 0.994 |
| L3 | W_Call incomplete files | 0.466 | 0.500 | 0.791 |
| L3 | A_Incomplete | 0.466 | 0.500 | 0.791 |
| L3 | A_Denied | 0.116 | 0.127 | 0.173 |
| L3 | O_Refused | 0.115 | 0.126 | 0.171 |
| L3 | A_Pending | 0.550 | 0.539 | 0.674 |
| L4 | finish pre-check | 0.062 | 1.000 | 1.000 |
| L4 | abort payment | 0.812 | 0.131 | 0.119 |
| L4 | revoke decision | 0.670 | 0.017 | 0.027 |
| L4 | create | 0.519 | 1.000 | 1.000 |
| L4 | save | 0.750 | 0.510 | 0.760 |
| L5 | Create Purchase Requisition Item | 0.009 | 0.596 | 0.792 |
| L5 | Clear Invoice | 0.868 | 0.407 | 0.292 |
| L5 | Record Invoice Receipt | 0.881 | 0.743 | 0.774 |
| L5 | Vendor creates invoice | 0.873 | 0.743 | 0.774 |
| L5 | Record Goods Receipt | 0.953 | 0.880 | 0.896 |

## Alpha and Alpha+: temporal split against random split (graded)

| log | net | temporal ShadowGen | temporal train | train with flag | temporal future | temporal unseen | future without flag | unseen without flag | random ShadowGen | random train | random unseen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | Alpha | 0.228 | 0.245 | -- | 0.245 | 0.221 | -- | -- | 0.266 | 0.282 | 0.272 |
| L1 | Alpha+ | 0.756 | 0.802 | -- | 0.801 | 0.845 | -- | -- | 0.747 | 0.802 | 0.823 |
| L2 | Alpha | 0.226 | 0.282 | -- | 0.369 | 0.181 | -- | -- | 0.256 | 0.308 | 0.129 |
| L2 | Alpha+ | 0.674 | 0.623 | -- | 0.531 | 0.743 | -- | -- | 0.631 | 0.596 | 0.808 |
| L3 | Alpha | 0.394 | 0.409 | -- | 0.410 | 0.392 | -- | -- | 0.422 | 0.436 | 0.423 |
| L3 | Alpha+ | 0.853 | 0.860 | -- | 0.860 | 0.855 | -- | -- | 0.861 | 0.882 | 0.859 |
| L4 | Alpha | 0.237 | 0.232 | 0.258 | 0.256 | 0.255 | -- | -- | 0.220 | 0.217 | 0.209 |
| L4 | Alpha+ | 0.501 | 0.475 | 0.297 | 0.261 | 0.265 | -- | -- | 0.583 | 0.608 | 0.628 |
| L5 | Alpha | 0.390 | 0.388 | 0.459 | 0.468 | 0.487 | 0.416 | 0.375 | 0.367 | 0.344 | 0.274 |
| L5 | Alpha+ | 0.286 | 0.333 | 0.643 | 0.518 | 0.580 | 0.335 | 0.346 | 0.291 | 0.364 | 0.361 |

## L4: share of cases with ['finish pre-check', 'create'] by start month (cut 2017-04-09)

| month | n | share |
|---|---|---|
| 2015-04 | 6031 | 0.000 |
| 2015-05 | 8691 | 0.000 |
| 2016-04 | 5856 | 1.000 |
| 2016-05 | 8672 | 1.000 |
| 2017-03 | 107 | 1.000 |
| 2017-04 | 7071 | 1.000 |
| 2017-05 | 7296 | 1.000 |

## L5: share of cases with ['Create Purchase Requisition Item'] by start month (cut 2018-08-31)

| month | n | share |
|---|---|---|
| 2017-12 | 123 | 0.041 |
| 2018-01 | 21269 | 0.010 |
| 2018-02 | 20894 | 0.008 |
| 2018-03 | 24846 | 0.007 |
| 2018-04 | 22460 | 0.009 |
| 2018-05 | 23000 | 0.010 |
| 2018-06 | 22271 | 0.006 |
| 2018-07 | 21081 | 0.010 |
| 2018-08 | 20198 | 0.012 |
| 2018-09 | 18650 | 0.612 |
| 2018-10 | 21855 | 0.632 |
| 2018-11 | 20616 | 0.598 |
| 2018-12 | 14128 | 0.528 |
| 2019-01 | 202 | 0.000 |
