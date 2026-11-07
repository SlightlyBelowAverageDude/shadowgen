# Alpha+ undershoot: score and unseen reference on the same net

| log | split | miner | score | reference | gap | len shadow | len unseen | reweighted score | reference on covered bins | within-bin gap | covered | miss term shadow / unseen | rem term shadow / unseen | regular / mutated |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L3 | temporal | Alpha | 0.394 | 0.392 | +0.002 | 44.7 | 49.3 | 0.388 | 0.392 | -0.004 | 1.000 | 0.203 / 0.195 | 0.403 / 0.413 | 0.395 / 0.378 |
| L3 | temporal | Alpha+ | 0.853 | 0.855 | -0.002 | 44.7 | 49.3 | 0.854 | 0.855 | -0.002 | 1.000 | 0.073 / 0.072 | 0.073 / 0.073 | 0.853 / 0.852 |
| L3 | random | Alpha | 0.422 | 0.423 | -0.001 | 45.4 | 49.8 | 0.420 | 0.423 | -0.004 | 1.000 | 0.176 / 0.168 | 0.402 / 0.409 | 0.422 / 0.401 |
| L3 | random | Alpha+ | 0.861 | 0.859 | +0.003 | 45.4 | 49.8 | 0.862 | 0.859 | 0.003 | 1.000 | 0.041 / 0.041 | 0.097 / 0.101 | 0.862 / 0.827 |
| L5 | temporal | Alpha | 0.390 | 0.487 | -0.096 | 19.4 | 10.3 | 0.411 | 0.487 | -0.075 | 1.000 | 0.209 / 0.184 | 0.400 / 0.329 | 0.425 / 0.283 |
| L5 | temporal | Alpha+ | 0.286 | 0.580 | -0.294 | 19.4 | 10.3 | 0.271 | 0.580 | -0.309 | 1.000 | 0.287 / 0.108 | 0.426 / 0.312 | 0.264 / 0.355 |
| L5 | random | Alpha | 0.367 | 0.274 | +0.092 | 18.8 | 32.1 | 0.295 | 0.274 | 0.021 | 1.000 | 0.239 / 0.294 | 0.394 / 0.432 | 0.396 / 0.269 |
| L5 | random | Alpha+ | 0.291 | 0.361 | -0.069 | 18.8 | 32.1 | 0.357 | 0.361 | -0.004 | 1.000 | 0.273 / 0.218 | 0.435 / 0.421 | 0.264 / 0.381 |

## L3 temporal, Alpha+ by length bin (deciles of the unseen cases)

| length | shadow n | unseen cases | fit shadow | fit unseen |
|---|---|---|---|---|
| 10 to 30 | 196 | 374 | 0.852 | 0.852 |
| 30 to 36 | 158 | 459 | 0.855 | 0.850 |
| 36 to 40 | 88 | 409 | 0.860 | 0.854 |
| 40 to 43 | 82 | 369 | 0.844 | 0.853 |
| 43 to 47 | 94 | 518 | 0.857 | 0.854 |
| 47 to 51 | 79 | 449 | 0.853 | 0.855 |
| 51 to 55 | 74 | 413 | 0.845 | 0.858 |
| 55 to 61 | 72 | 456 | 0.857 | 0.855 |
| 61 to 71 | 77 | 481 | 0.862 | 0.862 |
| 71 to 150 | 80 | 444 | 0.851 | 0.860 |

Net: 26 transitions (0 silent), 13 places; labels missing from net []; transitions without input or output arcs ['A_Incomplete', 'A_Validating', 'O_Cancelled', 'O_Refused', 'O_Returned', 'W_Assess potential fraud', 'W_Call after offers', 'W_Call incomplete files', 'W_Complete application', 'W_Handle leads', 'W_Personal Loan collection', 'W_Shortened completion ', 'W_Validate application']

| activity | shadow: contain | shadow: problem rate | unseen: contain | unseen: problem rate |
|---|---|---|---|---|
| O_Sent (online only) | 0.087 | 1.000 | 0.129 | 1.000 |
| O_Create Offer | 0.998 | 0.239 | 1.000 | 0.219 |
| A_Cancelled | 0.230 | 0.283 | 0.130 | 0.358 |
| A_Accepted | 0.982 | 0.015 | 1.000 | 0.000 |
| A_Denied | 0.126 | 0.286 | 0.173 | 0.259 |
| O_Accepted | 0.641 | 0.587 | 0.674 | 0.548 |
| O_Sent (mail and online) | 0.978 | 1.000 | 0.973 | 1.000 |
| A_Complete | 0.976 | 0.002 | 0.992 | 0.000 |
| A_Concept | 1.000 | 0.350 | 1.000 | 0.351 |
| A_Submitted | 0.651 | 0.000 | 0.649 | 0.000 |

## L3 random, Alpha+ by length bin (deciles of the unseen cases)

| length | shadow n | unseen cases | fit shadow | fit unseen |
|---|---|---|---|---|
| 10 to 31 | 190 | 397 | 0.872 | 0.857 |
| 31 to 36 | 128 | 413 | 0.848 | 0.845 |
| 36 to 40 | 125 | 416 | 0.851 | 0.849 |
| 40 to 44 | 111 | 471 | 0.855 | 0.845 |
| 44 to 48 | 83 | 478 | 0.859 | 0.858 |
| 48 to 51 | 56 | 368 | 0.859 | 0.864 |
| 51 to 56 | 69 | 496 | 0.868 | 0.864 |
| 56 to 61 | 61 | 403 | 0.870 | 0.870 |
| 61 to 72 | 84 | 469 | 0.863 | 0.870 |
| 72 to 160 | 93 | 443 | 0.871 | 0.865 |

Net: 26 transitions (1 silent), 14 places; labels missing from net []; transitions without input or output arcs ['A_Denied', 'A_Incomplete', 'A_Validating', 'O_Cancelled', 'O_Refused', 'O_Returned', 'O_Sent (mail and online)', 'O_Sent (online only)', 'W_Assess potential fraud', 'W_Call after offers', 'W_Call incomplete files', 'W_Complete application', 'W_Handle leads', 'W_Shortened completion ', 'W_Validate application']

| activity | shadow: contain | shadow: problem rate | unseen: contain | unseen: problem rate |
|---|---|---|---|---|
| A_Concept | 1.000 | 0.335 | 1.000 | 0.362 |
| O_Create Offer | 0.997 | 0.257 | 1.000 | 0.229 |
| O_Accepted | 0.673 | 0.605 | 0.692 | 0.553 |
| A_Accepted | 0.987 | 0.011 | 1.000 | 0.000 |
| A_Complete | 0.979 | 0.003 | 0.993 | 0.000 |
| A_Cancelled | 0.192 | 0.312 | 0.151 | 0.401 |
| A_Submitted | 0.665 | 0.000 | 0.638 | 0.000 |
| W_Shortened completion  | 0.006 | 0.000 | 0.006 | 0.000 |
| W_Call incomplete files | 0.658 | 0.000 | 0.756 | 0.000 |
| W_Call after offers | 0.995 | 0.000 | 0.993 | 0.000 |

## L5 temporal, Alpha+ by length bin (deciles of the unseen cases)

| length | shadow n | unseen cases | fit shadow | fit unseen |
|---|---|---|---|---|
| 1 to 4 | 62 | 1190 | 0.077 | 0.452 |
| 4 to 6 | 250 | 1664 | 0.198 | 0.570 |
| 6 to 7 | 30 | 4695 | 0.256 | 0.614 |
| 7 to 8 | 32 | 2889 | 0.309 | 0.624 |
| 8 to 11 | 208 | 3338 | 0.317 | 0.611 |
| 11 to 382 | 418 | 1842 | 0.355 | 0.464 |

Net: 43 transitions (2 silent), 41 places; labels missing from net []; transitions without input or output arcs ['Cancel Goods Receipt', 'Cancel Invoice Receipt', 'Cancel Subsequent Invoice', 'Change Approval for Purchase Order', 'Change Delivery Indicator', 'Change Price', 'Change Quantity', 'Change Rejection Indicator', 'Change Storage Location', 'Clear Invoice', 'Delete Purchase Order Item', 'Reactivate Purchase Order Item', 'Receive Order Confirmation', 'Record Goods Receipt', 'Record Invoice Receipt', 'Record Service Entry Sheet', 'Record Subsequent Invoice', 'Release Purchase Order', 'Remove Payment Block', 'SRM: Created', 'SRM: In Transfer to Execution Syst.', 'Set Payment Block', 'Vendor creates debit memo', 'Vendor creates invoice']

| activity | shadow: contain | shadow: problem rate | unseen: contain | unseen: problem rate |
|---|---|---|---|---|
| Create Purchase Order Item | 0.808 | 0.968 | 1.000 | 0.198 |
| SRM: Change was Transmitted | 0.041 | 0.439 | 0.009 | 0.000 |
| SRM: Complete | 0.035 | 0.600 | 0.009 | 1.000 |
| SRM: Transfer Failed (E.Sys.) | 0.006 | 0.833 | -- | -- |
| Update Order Confirmation | 0.002 | 1.000 | 0.004 | 1.000 |
| SRM: Transaction Completed | 0.002 | 0.500 | 0.000 | 1.000 |
| SRM: Ordered | 0.034 | 0.029 | 0.009 | 0.014 |
| Block Purchase Order Item | 0.005 | 0.000 | 0.001 | 0.556 |
| Change payment term | -- | -- | 0.000 | 1.000 |
| Change Final Invoice Indicator | 0.001 | 0.000 | 0.000 | 1.000 |

## L5 random, Alpha+ by length bin (deciles of the unseen cases)

| length | shadow n | unseen cases | fit shadow | fit unseen |
|---|---|---|---|---|
| 1 to 8 | 390 | 249 | 0.166 | 0.400 |
| 8 to 9 | 81 | 254 | 0.338 | 0.391 |
| 9 to 10 | 79 | 296 | 0.373 | 0.355 |
| 10 to 11 | 54 | 301 | 0.391 | 0.372 |
| 11 to 12 | 54 | 258 | 0.375 | 0.370 |
| 12 to 14 | 78 | 313 | 0.377 | 0.376 |
| 14 to 19 | 62 | 337 | 0.429 | 0.375 |
| 19 to 31 | 63 | 285 | 0.391 | 0.339 |
| 31 to 67 | 80 | 294 | 0.347 | 0.324 |
| 67 to 991 | 59 | 288 | 0.342 | 0.310 |

Net: 44 transitions (2 silent), 47 places; labels missing from net []; transitions without input or output arcs ['Cancel Goods Receipt', 'Cancel Invoice Receipt', 'Cancel Subsequent Invoice', 'Change Approval for Purchase Order', 'Change Delivery Indicator', 'Change Price', 'Change Quantity', 'Change Storage Location', 'Clear Invoice', 'Receive Order Confirmation', 'Record Goods Receipt', 'Record Invoice Receipt', 'Record Service Entry Sheet', 'Record Subsequent Invoice', 'Release Purchase Order', 'Remove Payment Block', 'SRM: Created', 'SRM: In Transfer to Execution Syst.', 'Set Payment Block', 'Update Order Confirmation', 'Vendor creates debit memo', 'Vendor creates invoice']

| activity | shadow: contain | shadow: problem rate | unseen: contain | unseen: problem rate |
|---|---|---|---|---|
| Create Purchase Order Item | 0.802 | 0.857 | 1.000 | 0.832 |
| SRM: Change was Transmitted | 0.056 | 0.429 | 0.032 | 0.000 |
| SRM: Complete | 0.042 | 1.000 | 0.032 | 0.978 |
| SRM: Transfer Failed (E.Sys.) | -- | -- | 0.004 | 1.000 |
| Reactivate Purchase Order Item | 0.015 | 1.000 | 0.014 | 0.949 |
| Change payment term | -- | -- | 0.001 | 0.750 |
| Block Purchase Order Item | 0.006 | 0.167 | 0.006 | 0.000 |
| SRM: Ordered | 0.040 | 0.025 | 0.032 | 0.000 |
| Change Final Invoice Indicator | -- | -- | 0.001 | 1.000 |
| SRM: Transaction Completed | 0.001 | 1.000 | 0.000 | 1.000 |
