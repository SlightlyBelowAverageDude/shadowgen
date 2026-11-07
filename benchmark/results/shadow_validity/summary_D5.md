# Shadow trace validity, D5 (BPI2019), 251734 cases, 2 repetitions pooled

real = future cases with a variant absent from training; shadow = ShadowGen's 1,000 traces per repetition (seed 42, N=6, tau=5, mle, v2.6). Invariants: see benchmark/shadow_validity_check.py.

Per repetition: rep 0: 2875 real unseen cases, mutated share 0.232, duplicates kept 0, truncated 0; rep 1: 2986 real unseen cases, mutated share 0.239, duplicates kept 0, truncated 0

## A. Share of traces that violate an invariant

| reference | group | n | any | end | count | mandatory | ef | df | length |
|---|---|---|---|---|---|---|---|---|---|
| train | real | 5861 | 0.015 | 0.001 | 0.002 | 0.000 | 0.007 | 0.009 | 0.000 |
| train | shadow | 2000 | 0.246 | 0.000 | 0.021 | 0.200 | 0.048 | 0.002 | 0.000 |
| train | shadow_regular | 1529 | 0.268 | 0.000 | 0.014 | 0.247 | 0.021 | 0.000 | 0.000 |
| train | shadow_mutated | 471 | 0.174 | 0.000 | 0.042 | 0.047 | 0.134 | 0.006 | 0.000 |
| full | shadow | 2000 | 0.245 | 0.000 | 0.021 | 0.200 | 0.046 | 0.002 | 0.000 |
| full | shadow_regular | 1529 | 0.268 | 0.000 | 0.014 | 0.247 | 0.021 | 0.000 | 0.000 |
| full | shadow_mutated | 471 | 0.170 | 0.000 | 0.042 | 0.047 | 0.130 | 0.006 | 0.000 |

## B. Strict acceptance by group and invariant status

| model | group | n | accepted | n clean (train) | accepted, clean | n violating (train) | accepted, violating |
|---|---|---|---|---|---|---|---|
| Inductive_Strict | real | 5861 | 1.000 | 5773 | 1.000 | 88 | 0.989 |
| Inductive_Strict | shadow | 2000 | 0.779 | 1508 | 1.000 | 492 | 0.104 |
| Inductive_Strict | shadow_regular | 1529 | 0.739 | 1119 | 1.000 | 410 | 0.027 |
| Inductive_Strict | shadow_mutated | 471 | 0.911 | 389 | 1.000 | 82 | 0.488 |
| Inductive_Infrequent | real | 5861 | 0.680 | 5773 | 0.685 | 88 | 0.318 |
| Inductive_Infrequent | shadow | 2000 | 0.517 | 1508 | 0.667 | 492 | 0.057 |
| Inductive_Infrequent | shadow_regular | 1529 | 0.556 | 1119 | 0.751 | 410 | 0.024 |
| Inductive_Infrequent | shadow_mutated | 471 | 0.391 | 389 | 0.427 | 82 | 0.220 |

## C. Shadow traces by full-log invariant status

| model | n clean (full) | accepted, clean | n violating (full) | accepted, violating |
|---|---|---|---|---|
| Inductive_Strict | 1510 | 1.000 | 490 | 0.100 |
| Inductive_Infrequent | 1510 | 0.668 | 490 | 0.053 |

## D. Rejected shadow traces

| model | rejected | violates train | violates full | by kind (full): end, count, mandatory, ef, df, length | incomplete only (no missing token) | mutated |
|---|---|---|---|---|---|---|
| Inductive_Strict | 441 | 1.000 | 1.000 | 0.000, 0.095, 0.907, 0.102, 0.005, 0.000 | 0.000 | 0.095 |

Inductive_Strict, transitions with problems (share of rejected traces): Create Purchase Order Item 0.09

| Inductive_Infrequent | 966 | 0.480 | 0.480 | 0.000, 0.043, 0.414, 0.069, 0.003, 0.000 | 0.000 | 0.297 |

Inductive_Infrequent, transitions with problems (share of rejected traces): Clear Invoice 0.37, Remove Payment Block 0.28, Cancel Invoice Receipt 0.13, Record Invoice Receipt 0.05, SRM: Change was Transmitted 0.05, Create Purchase Order Item 0.04, Record Goods Receipt 0.04, Vendor creates invoice 0.04

## E. Shadow traces that are a real unseen future variant

0.011 of the shadow traces equal a real unseen future variant (regular 0.013, mutated 0.004).

## F. Stored values reproduced

rep 0 Inductive_Strict: strict score 0.7750 (stored 0.775), truth 0.9996521739130435 (stored 0.9996521739130435)
rep 0 Inductive_Infrequent: strict score 0.5020 (stored 0.502), truth 0.6768695652173913 (stored 0.6768695652173914)
rep 1 Inductive_Strict: strict score 0.7840 (stored 0.784), truth 1.0 (stored 1.0)
rep 1 Inductive_Infrequent: strict score 0.5320 (stored 0.532), truth 0.6821835231078366 (stored 0.6821835231078366)

## G. First rejected shadow traces, Inductive_Strict, repetition 0

- Vendor creates invoice > Record Invoice Receipt > Clear Invoice  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 2; problems []]
- Vendor creates invoice > Record Invoice Receipt > Clear Invoice  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 2; problems []]
- Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt > Remove Payment Block  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 2; problems []]
- Vendor creates invoice > Record Invoice Receipt > Remove Payment Block > Clear Invoice  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 2; problems []]
- Change Approval for Purchase Order > Release Purchase Order > Change Approval for Purchase Order > Record Invoice Receipt > Clear Invoice  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 2; problems []]
- Vendor creates invoice > Record Invoice Receipt  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 2; problems []]
- Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt > Clear Invoice  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 2; problems []]
- Vendor creates invoice > Record Invoice Receipt > Clear Invoice  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 2; problems []]
- Create Purchase Order Item > Vendor creates invoice > Create Purchase Order Item > Vendor creates invoice > Record Goods Receipt > Record Goods Receipt > Record Invoice Receipt > Clear Invoice  [mutated True; train ['count', 'ef']; full ['count', 'ef']; missing 1, remaining 1; problems ['Create Purchase Order Item']]
- Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 2; problems []]
- Vendor creates invoice > Record Goods Receipt > Record Goods Receipt > Record Invoice Receipt > Remove Payment Block > Clear Invoice  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 2; problems []]
- Vendor creates invoice > Record Goods Receipt > Record Invoice Receipt > Clear Invoice  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 2; problems []]

## H. Inductive_Strict process tree, repetition 0

```
+( 'Create Purchase Order Item', X( tau, +( X( tau, 'Create Purchase Requisition Item' ), X( tau, ->( X( tau, 'Release Purchase Requisition' ), X( tau, +( X( tau, *( 'Delete Purchase Order Item', tau ) ), X( tau, ->( X( tau, *( 'Change Rejection Indicator', tau ) ), +( X( tau, *( 'SRM: Created', tau ) ), ->( X( tau, ->( 'SRM: Incomplete', 'SRM: Held' ) ), *( X( 'Change Currency', 'Block Purchase Order Item', ->( X( tau, 'Change Storage Location', 'Reactivate Purchase Order Item', 'Change Final Invoice Indicator', 'Change payment term', 'Record Service Entry Sheet', 'Cancel Goods Receipt', ->( 'SRM: Complete', 'SRM: Awaiting Approval' ), 'Receive Order Confirmation', 'Vendor creates debit memo', 'Change Delivery Indicator', 'Update Order Confirmation', ->( X( tau, 'Release Purchase Order' ), X( tau, 'Change Approval for Purchase Order', 'Change Price', 'Change Quantity' ) ) ), X( tau, ->( +( X( tau, *( 'Clear Invoice', tau ) ), X( tau, ->( X( tau, +( X( tau, 'SRM: Document Completed' ), ->( X( tau, 'Record Invoice Receipt' ), X( tau, +( X( tau, *( 'SRM: In Transfer to Execution Syst.', tau ) ), X( tau, ->( X( tau, +( X( tau, 'SRM: Ordered' ), X( tau, ->( X( tau, 'SRM: Change was Transmitted' ), X( tau, 'Vendor creates invoice' ) ) ) ) ), X( tau, 'Record Goods Receipt', ->( X( tau, 'SRM: Deleted' ), X( tau, 'SRM: Transaction Completed' ) ) ) ) ) ) ) ) ) ), X( tau, +( X( tau, *( 'Remove Payment Block', tau ) ), X( tau, +( X( tau, *( 'Cancel Invoice Receipt', tau ) ), X( tau, ->( X( tau, +( X( tau, *( 'Record Subsequent Invoice', tau ) ), X( tau, *( 'Cancel Subsequent Invoice', tau ) ) ) ), X( tau, *( 'Set Payment Block', tau ) ) ) ) ) ) ) ) ) ) ), X( tau, 'SRM: Transfer Failed (E.Sys.)' ) ) ) ) ), tau ) ) ) ) ) ) ) ) ) ) ) )
```
