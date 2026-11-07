# Shadow trace validity, D1 (Sepsis), 1050 cases, 3 repetitions pooled

real = future cases with a variant absent from training; shadow = ShadowGen's 1,000 traces per repetition (seed 42, N=6, tau=5, mle, v2.6). Invariants: see benchmark/shadow_validity_check.py.

Per repetition: rep 0: 246 real unseen cases, mutated share 0.569, duplicates kept 0, truncated 0; rep 1: 244 real unseen cases, mutated share 0.594, duplicates kept 0, truncated 0; rep 2: 243 real unseen cases, mutated share 0.589, duplicates kept 0, truncated 0

## A. Share of traces that violate an invariant

| reference | group | n | any | end | count | mandatory | ef | df | length |
|---|---|---|---|---|---|---|---|---|---|
| train | real | 733 | 0.022 | 0.000 | 0.003 | 0.000 | 0.008 | 0.019 | 0.000 |
| train | shadow | 3000 | 0.292 | 0.000 | 0.200 | 0.102 | 0.198 | 0.004 | 0.000 |
| train | shadow_regular | 1248 | 0.195 | 0.000 | 0.058 | 0.137 | 0.058 | 0.000 | 0.000 |
| train | shadow_mutated | 1752 | 0.362 | 0.000 | 0.301 | 0.078 | 0.297 | 0.007 | 0.000 |
| full | shadow | 3000 | 0.292 | 0.000 | 0.200 | 0.102 | 0.198 | 0.004 | 0.000 |
| full | shadow_regular | 1248 | 0.195 | 0.000 | 0.058 | 0.137 | 0.058 | 0.000 | 0.000 |
| full | shadow_mutated | 1752 | 0.362 | 0.000 | 0.301 | 0.078 | 0.297 | 0.007 | 0.000 |

## B. Strict acceptance by group and invariant status

| model | group | n | accepted | n clean (train) | accepted, clean | n violating (train) | accepted, violating |
|---|---|---|---|---|---|---|---|
| Inductive_Strict | real | 733 | 0.993 | 717 | 1.000 | 16 | 0.688 |
| Inductive_Strict | shadow | 3000 | 0.694 | 2123 | 0.976 | 877 | 0.013 |
| Inductive_Strict | shadow_regular | 1248 | 0.787 | 1005 | 0.976 | 243 | 0.004 |
| Inductive_Strict | shadow_mutated | 1752 | 0.628 | 1118 | 0.975 | 634 | 0.016 |
| Inductive_Infrequent | real | 733 | 0.795 | 717 | 0.803 | 16 | 0.438 |
| Inductive_Infrequent | shadow | 3000 | 0.552 | 2123 | 0.773 | 877 | 0.015 |
| Inductive_Infrequent | shadow_regular | 1248 | 0.633 | 1005 | 0.783 | 243 | 0.012 |
| Inductive_Infrequent | shadow_mutated | 1752 | 0.494 | 1118 | 0.765 | 634 | 0.016 |

## C. Shadow traces by full-log invariant status

| model | n clean (full) | accepted, clean | n violating (full) | accepted, violating |
|---|---|---|---|---|
| Inductive_Strict | 2123 | 0.976 | 877 | 0.013 |
| Inductive_Infrequent | 2123 | 0.773 | 877 | 0.015 |

## D. Rejected shadow traces

| model | rejected | violates train | violates full | by kind (full): end, count, mandatory, ef, df, length | incomplete only (no missing token) | mutated |
|---|---|---|---|---|---|---|
| Inductive_Strict | 918 | 0.943 | 0.943 | 0.000, 0.644, 0.334, 0.645, 0.012, 0.000 | 0.000 | 0.710 |

Inductive_Strict, transitions with problems (share of rejected traces): IV Antibiotics 0.49, IV Liquid 0.41, ER Sepsis Triage 0.19, Release A 0.16, Admission NC 0.14, Admission IC 0.04, ER Registration 0.02, Release B 0.02

| Inductive_Infrequent | 1345 | 0.642 | 0.642 | 0.000, 0.442, 0.223, 0.441, 0.008, 0.000 | 0.000 | 0.659 |

Inductive_Infrequent, transitions with problems (share of rejected traces): IV Antibiotics 0.35, IV Liquid 0.30, ER Sepsis Triage 0.14, Admission NC 0.14, Admission IC 0.13, Return ER 0.08, LacticAcid 0.07, ER Triage 0.04

## E. Shadow traces that are a real unseen future variant

0.013 of the shadow traces equal a real unseen future variant (regular 0.028, mutated 0.002).

## F. Stored values reproduced

rep 0 Inductive_Strict: strict score 0.7040 (stored 0.704), truth 0.9959349593495935 (stored 0.9959349593495935)
rep 0 Inductive_Infrequent: strict score 0.6060 (stored 0.606), truth 0.8821138211382114 (stored 0.8821138211382115)
rep 1 Inductive_Strict: strict score 0.6940 (stored 0.694), truth 0.9959016393442623 (stored 0.9959016393442623)
rep 1 Inductive_Infrequent: strict score 0.4740 (stored 0.474), truth 0.6434426229508197 (stored 0.6434426229508197)
rep 2 Inductive_Strict: strict score 0.6840 (stored 0.684), truth 0.9876543209876543 (stored 0.9876543209876543)
rep 2 Inductive_Infrequent: strict score 0.5750 (stored 0.575), truth 0.8600823045267489 (stored 0.8600823045267489)

## G. First rejected shadow traces, Inductive_Strict, repetition 0

- IV Liquid > CRP > Leucocytes > Release A  [mutated False; train ['mandatory']; full ['mandatory']; missing 2, remaining 6; problems ['Release A']]
- ER Registration > IV Liquid > ER Triage > ER Sepsis Triage > LacticAcid > Leucocytes > CRP > IV Antibiotics > IV Liquid > Admission NC > Admission IC > LacticAcid > Leucocytes > CRP > CRP > LacticAcid > Leucocytes > Admission NC > CRP > Leucocytes > Release D > Return ER  [mutated True; train ['count', 'ef']; full ['count', 'ef']; missing 1, remaining 1; problems ['IV Liquid']]
- CRP > Leucocytes > Admission IC > Leucocytes > CRP > LacticAcid > Admission NC > CRP > CRP > Release A  [mutated False; train ['mandatory']; full ['mandatory']; missing 2, remaining 4; problems ['Admission IC']]
- ER Triage > ER Sepsis Triage > Leucocytes > CRP > LacticAcid > IV Liquid > IV Antibiotics > Admission NC > CRP > Leucocytes > Release A  [mutated False; train ['mandatory']; full ['mandatory']; missing 1, remaining 3; problems []]
- Leucocytes > Leucocytes > Leucocytes > CRP > CRP > Leucocytes > Leucocytes > CRP > Release A  [mutated False; train ['mandatory']; full ['mandatory']; missing 2, remaining 6; problems ['Release A']]
- ER Registration > ER Triage > ER Sepsis Triage > Leucocytes > LacticAcid > CRP > IV Liquid > IV Antibiotics > Admission NC > CRP > Leucocytes > Admission NC > CRP > Leucocytes > Leucocytes > CRP > Admission IC > LacticAcid > Leucocytes > LacticAcid > Leucocytes > CRP > Admission NC > Admission NC > Admission NC > IV Liquid > Release A > Return ER  [mutated True; train ['count', 'ef']; full ['count', 'ef']; missing 1, remaining 1; problems ['IV Liquid']]
- ER Registration > ER Sepsis Triage > ER Triage > LacticAcid > CRP > Leucocytes > ER Sepsis Triage > IV Liquid > IV Antibiotics > Admission NC > CRP > Leucocytes > CRP > Leucocytes > CRP > Leucocytes > CRP > Release A  [mutated False; train ['count', 'ef']; full ['count', 'ef']; missing 1, remaining 1; problems ['ER Sepsis Triage']]
- ER Registration > ER Triage > ER Sepsis Triage > IV Liquid > CRP > Leucocytes > LacticAcid > IV Antibiotics > Admission NC > LacticAcid > LacticAcid > Leucocytes > CRP > Leucocytes > LacticAcid > CRP > CRP > LacticAcid > Leucocytes > IV Antibiotics > Admission NC > Leucocytes > CRP > Leucocytes > Admission NC > Leucocytes > Leucocytes > LacticAcid > CRP > Admission NC > Leucocytes > CRP > Leucocytes > CRP > CRP > Leucocytes > Leucocytes > CRP > Release A > Return ER  [mutated True; train ['count', 'ef']; full ['count', 'ef']; missing 1, remaining 1; problems ['IV Antibiotics']]
- ER Registration > Admission IC > Leucocytes > CRP > LacticAcid > CRP > LacticAcid > Leucocytes > Admission NC > Leucocytes > Leucocytes > LacticAcid > CRP > Admission NC > CRP > CRP > Leucocytes > Leucocytes > CRP > CRP > Leucocytes > Release A  [mutated True; train ['mandatory']; full ['mandatory']; missing 1, remaining 1; problems ['Admission IC']]
- ER Registration > ER Triage > ER Sepsis Triage > Leucocytes > LacticAcid > CRP > IV Liquid > IV Antibiotics > Admission NC > LacticAcid > Leucocytes > CRP > IV Liquid > IV Antibiotics > Admission NC > Leucocytes > Leucocytes > Leucocytes > Leucocytes > CRP > Admission NC > Admission NC > IV Liquid  [mutated True; train ['count', 'ef']; full ['count', 'ef']; missing 3, remaining 3; problems ['IV Antibiotics', 'IV Liquid']]
- ER Registration > ER Triage > ER Sepsis Triage > IV Liquid > CRP > Leucocytes > LacticAcid > IV Antibiotics > IV Liquid > Admission NC > Leucocytes > CRP > Admission NC > Leucocytes > CRP > CRP > Release A  [mutated True; train ['count', 'ef']; full ['count', 'ef']; missing 1, remaining 1; problems ['IV Liquid']]
- ER Registration > Admission IC > Leucocytes > CRP > LacticAcid > Leucocytes > Leucocytes > LacticAcid > CRP > Leucocytes > LacticAcid > CRP > Leucocytes > LacticAcid > LacticAcid > Leucocytes > CRP > LacticAcid > Admission NC > CRP > Leucocytes > CRP > Leucocytes > Leucocytes > Leucocytes > CRP > CRP > Leucocytes > CRP > Leucocytes > Leucocytes > CRP > LacticAcid > Leucocytes > CRP > LacticAcid > LacticAcid > CRP > Leucocytes > LacticAcid > CRP > LacticAcid > Leucocytes > Admission IC > Admission NC > Admission NC > Leucocytes > CRP > CRP > Leucocytes > Admission NC > LacticAcid > CRP > Leucocytes > LacticAcid > Admission NC > CRP > Leucocytes > Leucocytes > CRP > CRP > Leucocytes > Release A > Return ER  [mutated True; train ['mandatory']; full ['mandatory']; missing 1, remaining 1; problems ['Admission IC']]

## H. Inductive_Strict process tree, repetition 0

```
->( +( X( tau, *( 'Admission NC', tau ) ), 'ER Registration', ->( +( X( tau, 'Return ER' ), ->( +( X( tau, *( 'Leucocytes', tau ) ), X( tau, *( 'CRP', tau ) ), X( tau, *( 'LacticAcid', tau ) ), ->( +( X( tau, ->( 'ER Sepsis Triage', X( tau, 'IV Antibiotics' ) ) ), ->( *( 'ER Triage', tau ), X( tau, *( 'Admission IC', tau ) ) ), X( tau, 'IV Liquid' ) ), X( tau, 'Release A' ) ) ), X( tau, 'Release D', 'Release C' ) ) ), X( tau, 'Release B' ) ) ), X( tau, 'Release E' ) )
```
