# Invalid shadow traces that pass the six rules (78 known systems; seed 42; 1,000 shadow traces; N=6, tau=5, mle; v2.6 generator; rules from the 300-trace training log; pm4py 2.7.22.2)

Shadow traces 78000; invalid 31812 (0.408); removed by the six rules 16542; survivors 15270 (0.480 of the invalid), in 45 systems. Survivors that are mutated traces: 0.174 (all shadow traces: 0.119).

## A. What the survivors break, and what each rule kind costs

| rule kind | survivors caught | valid shadow traces (passing the six rules) removed | fresh unseen system traces (passing the six rules) removed |
|---|---|---|---|
| excl | 0.000 | 0.000 | 0.000 |
| impl | 0.521 | 0.000 | 0.000 |
| balance | 0.786 | 0.020 | 0.023 |
| tri | 0.121 | 0.002 | 0.036 |
| any of the four | 0.802 | 0.022 | 0.058 |
| any of excl, impl, balance | 0.788 | 0.020 | 0.023 |

Survivors that are only incomplete (no activity fires while disabled in the system, an obligatory part is missing):0.255; among the survivors caught by none of the four kinds: 0.571 (n = 3024).

## B. The six rules extended (pooled over all shadow traces; systems = per-system counts)

| filter | kept | valid share after | invalid removed | valid removed | fresh unseen removed, pooled | fresh unseen removed, median system | systems with valid share >= 0.9 | systems with no trace kept |
|---|---|---|---|---|---|---|---|---|
| none | 1.000 | 0.592 | 0.000 | 0.000 | 0.000 | 0.000 | 26 | 0 |
| six rules | 0.762 | 0.743 | 0.520 | 0.044 | 0.031 | 0.032 | 35 | 2 |
| + excl | 0.762 | 0.743 | 0.520 | 0.044 | 0.031 | 0.032 | 35 | 2 |
| + impl | 0.660 | 0.858 | 0.770 | 0.044 | 0.031 | 0.032 | 42 | 4 |
| + balance | 0.597 | 0.930 | 0.897 | 0.062 | 0.054 | 0.052 | 57 | 4 |
| + tri | 0.737 | 0.767 | 0.578 | 0.046 | 0.066 | 0.054 | 39 | 2 |
| + excl, impl | 0.660 | 0.858 | 0.770 | 0.044 | 0.031 | 0.032 | 42 | 4 |
| + excl, impl, balance | 0.597 | 0.930 | 0.898 | 0.062 | 0.054 | 0.052 | 58 | 4 |
| + all four | 0.593 | 0.935 | 0.905 | 0.064 | 0.087 | 0.078 | 59 | 4 |

## C. Survivors caught by none of the four kinds (first examples)

- system mode 6 seed 1000: `+( X( 'c', ->( tau, 'a' ) ), ->( 'b', *( 'e', +( 'd', ->( 'g', 'f' ) ) ) ) )`
  - b > e
  - b > e
- system mode 6 seed 1259: `->( *( X( 'd', 'c' ), +( X( 'a', 'f' ), +( 'e', 'h' ) ) ), ->( 'b', 'g' ) )`
  - c > a > h > e > c > e > a > h > d > a > h > e > f > d > b > g
  - c > e > a > h > d > a > h > e > f > d > a > e > h > d > h > f > e > d > b > g
- system mode 6 seed 1555: `->( tau, +( X( 'b', 'c' ), +( 'a', 'd' ) ) )`
  - a > d
  - a > d
- system mode 8 seed 1000: `+( X( 'c', ->( tau, 'a' ) ), ->( *( 'e', +( 'd', ->( 'g', 'f' ) ) ), *( 'b', ->( 'h', 'i' ) ) ) )`
  - e > b
  - e > b
- system mode 8 seed 1259: `->( *( X( 'c', X( 'd', ->( 'j', 'i' ) ) ), +( X( 'a', 'f' ), +( 'e', 'h' ) ) ), ->( 'b', *( tau, 'g' ) ) )`
  - d > a > e > h > d > f > h > e > f > j > i > h > e > f > d > e > h > a > c > f > e > h > d > b > g
  - j > i > a > e > h > j > i > f > e > h > a > c > e > a > h > c > b > g > g
- system mode 8 seed 1444: `+( +( 'c', *( 'a', ->( 'd', ->( 'f', *( 'e', 'g' ) ) ) ) ), X( tau, 'b' ) )`
  - c > e > g > e > a > d > f > e > a
  - c > e > g > e > g > e > g > e > a > d > f > e > a
