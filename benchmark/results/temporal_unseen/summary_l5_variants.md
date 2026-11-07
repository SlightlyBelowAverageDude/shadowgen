# L5 variants and activities at the temporal cut (Inductive_Infrequent, 68 transitions)

Strict from variant flags: train 0.987, seen test 0.448; rejected seen test cases 33041.

Cases with a repeated activity: {'train': 0.09636065443525733, 'test': 0.07227128878060407}

## Top test variants

| test n | test share | train n | train share | accepted | variant |
|---|---|---|---|---|---|
| 8466 | 0.112 | 455 | 0.0026 | False | Create Purchase Requisition Item > Create Purchase Order Item > Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt > Clear Invoice |
| 4208 | 0.056 | 2 | 0.0000 | False | Create Purchase Requisition Item > Create Purchase Order Item > Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt |
| 3571 | 0.047 | 152 | 0.0009 | False | Create Purchase Requisition Item > Create Purchase Order Item > Record Goods Receipt |
| 3444 | 0.046 | 104 | 0.0006 | True | Create Purchase Order Item > Record Goods Receipt > Vendor creates invoice > Record Invoice Receipt |
| 3316 | 0.044 | 8898 | 0.0505 | True | Create Purchase Order Item > Record Goods Receipt |
| 2971 | 0.039 | 27827 | 0.1579 | True | Create Purchase Order Item > Record Goods Receipt > Vendor creates invoice > Record Invoice Receipt > Clear Invoice |
| 2626 | 0.035 | 47660 | 0.2705 | True | Create Purchase Order Item > Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt > Clear Invoice |
| 2550 | 0.034 | 144 | 0.0008 | False | Create Purchase Requisition Item > Create Purchase Order Item > Record Goods Receipt > Vendor creates invoice > Record Invoice Receipt > Clear Invoice |
| 2516 | 0.033 | 249 | 0.0014 | True | Create Purchase Order Item > Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt |
| 2439 | 0.032 | 396 | 0.0022 | True | Create Purchase Order Item |
| 2220 | 0.029 | 1 | 0.0000 | False | Create Purchase Requisition Item > Create Purchase Order Item > Receive Order Confirmation > Record Goods Receipt > Vendor creates invoice > Record Invoice Receipt |
| 2051 | 0.027 | 3 | 0.0000 | False | Create Purchase Requisition Item > Create Purchase Order Item > Record Goods Receipt > Vendor creates invoice > Record Invoice Receipt |
| 1853 | 0.025 | 18 | 0.0001 | False | Create Purchase Requisition Item > Create Purchase Order Item > Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt > Remove Payment Block > Clear Invoice |
| 1486 | 0.020 | 2 | 0.0000 | False | Create Purchase Requisition Item > Create Purchase Order Item |
| 1175 | 0.016 | 130 | 0.0007 | False | Create Purchase Requisition Item > Create Purchase Order Item > Vendor creates invoice > Record Invoice Receipt > Record Goods Receipt > Remove Payment Block > Clear Invoice |

## Rejected seen variants, by test count

| test n | train n | variant |
|---|---|---|
| 8466 | 455 | Create Purchase Requisition Item > Create Purchase Order Item > Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt > Clear Invoice |
| 4208 | 2 | Create Purchase Requisition Item > Create Purchase Order Item > Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt |
| 3571 | 152 | Create Purchase Requisition Item > Create Purchase Order Item > Record Goods Receipt |
| 2550 | 144 | Create Purchase Requisition Item > Create Purchase Order Item > Record Goods Receipt > Vendor creates invoice > Record Invoice Receipt > Clear Invoice |
| 2220 | 1 | Create Purchase Requisition Item > Create Purchase Order Item > Receive Order Confirmation > Record Goods Receipt > Vendor creates invoice > Record Invoice Receipt |
| 2051 | 3 | Create Purchase Requisition Item > Create Purchase Order Item > Record Goods Receipt > Vendor creates invoice > Record Invoice Receipt |
| 1853 | 18 | Create Purchase Requisition Item > Create Purchase Order Item > Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt > Remove Payment Block > Clear Invoice |
| 1486 | 2 | Create Purchase Requisition Item > Create Purchase Order Item |
| 1175 | 130 | Create Purchase Requisition Item > Create Purchase Order Item > Vendor creates invoice > Record Invoice Receipt > Record Goods Receipt > Remove Payment Block > Clear Invoice |
| 935 | 64 | Create Purchase Requisition Item > Create Purchase Order Item > Delete Purchase Order Item |

## Activity case share, largest changes

| activity | train | test |
|---|---|---|
| Create Purchase Requisition Item | 0.009 | 0.596 |
| Clear Invoice | 0.868 | 0.407 |
| Record Invoice Receipt | 0.881 | 0.743 |
| Vendor creates invoice | 0.873 | 0.743 |
| Record Goods Receipt | 0.953 | 0.880 |
| Remove Payment Block | 0.240 | 0.178 |
| Receive Order Confirmation | 0.117 | 0.152 |
| Cancel Invoice Receipt | 0.032 | 0.012 |
| Vendor creates debit memo | 0.028 | 0.013 |
| Change Approval for Purchase Order | 0.013 | 0.028 |
| Change Quantity | 0.074 | 0.061 |
| Change Price | 0.047 | 0.039 |

## Future split by new activities ['Create Purchase Requisition Item']

Share of cases with a new activity: {'test': 0.596337442565644, 'test_unseen': 0.7922269176591112, 'train': 0.008830222514797433}; infrequent net has the label: {'Create Purchase Requisition Item': True}

| miner | label in net | ShadowGen | all | unseen | with new | without new | unseen without new | strict SG | strict all | strict with new | strict without new | strict unseen without new |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Alpha | {'Create Purchase Requisition Item': True} | 0.390 | 0.468 | 0.487 | 0.503 | 0.416 | 0.375 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 |
| Alpha+ | {'Create Purchase Requisition Item': True} | 0.286 | 0.518 | 0.580 | 0.643 | 0.335 | 0.346 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Heuristics | {'Create Purchase Requisition Item': True} | 0.839 | 0.837 | 0.831 | 0.832 | 0.844 | 0.872 | 0.004 | 0.056 | 0.038 | 0.083 | 0.031 |
| Heuristics_Strict | {'Create Purchase Requisition Item': True} | 0.896 | 0.918 | 0.902 | 0.914 | 0.923 | 0.934 | 0.020 | 0.069 | 0.039 | 0.113 | 0.206 |
| Inductive_Strict | {'Create Purchase Requisition Item': True} | 0.995 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.791 | 1.000 | 1.000 | 1.000 | 0.999 |
| Inductive_Infrequent | {'Create Purchase Requisition Item': True} | 0.996 | 0.975 | 0.967 | 0.960 | 0.997 | 0.980 | 0.957 | 0.390 | 0.001 | 0.966 | 0.803 |

n: {'all': 75521, 'unseen': 15618, 'with_new': 45036, 'without_new': 30485, 'unseen_without_new': 3245}

## Strict acceptance by start month (months with >= 200 cases)

| month | n | strict |
|---|---|---|
| 2018-01 | 21269 | 0.987 |
| 2018-02 | 20894 | 0.989 |
| 2018-03 | 24846 | 0.984 |
| 2018-04 | 22460 | 0.987 |
| 2018-05 | 23000 | 0.983 |
| 2018-06 | 22271 | 0.992 |
| 2018-07 | 21081 | 0.989 |
| 2018-08 | 20198 | 0.988 |
| 2018-09 | 18650 | 0.386 |
| 2018-10 | 21855 | 0.359 |
| 2018-11 | 20616 | 0.398 |
| 2018-12 | 14128 | 0.431 |
| 2019-01 | 202 | 0.391 |
