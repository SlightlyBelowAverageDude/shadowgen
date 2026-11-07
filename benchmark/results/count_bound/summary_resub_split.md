# Training-split fitness against the unseen-only reference (count-bound test, control)

| log | split | score | Pearson | Spearman | MAE | spread (ref) | max dev |
|---|---|---|---|---|---|---|---|
| L1 | temporal | resub, case-weighted | 0.998 | 1.00 | 0.014 | 0.75 (0.78) | 0.042 |
|  |  | resub, variant mean | 1.000 | 1.00 | 0.004 | 0.77 (0.78) | 0.010 |
|  |  | resub, singleton mean | 1.000 | 1.00 | 0.002 | 0.77 (0.78) | 0.006 |
|  |  | resub, token-aggregated | 1.000 | 1.00 | 0.007 | 0.79 (0.78) | 0.015 |
|  |  | ShadowGen | 0.993 | 1.00 | 0.025 | 0.75 (0.78) | 0.088 |
|  |  | ShadowGen bounded | 1.000 | 1.00 | 0.006 | 0.77 (0.78) | 0.017 |
|  |  | strict resub, case-weighted | 0.997 | 1.00 | 0.021 | 1.00 (0.99) | 0.083 |
|  |  | strict resub, singleton mean | 1.000 | 1.00 | 0.008 | 1.00 (0.99) | 0.026 |
|  |  | strict ShadowGen | 1.000 | 0.94 | 0.115 | 0.64 (0.99) | 0.348 |
|  |  | strict ShadowGen bounded | 0.999 | 1.00 | 0.010 | 1.00 (0.99) | 0.041 |
| L1 | random | resub, case-weighted | 0.999 | 1.00 | 0.008 | 0.72 (0.73) | 0.021 |
|  |  | resub, variant mean | 1.000 | 1.00 | 0.004 | 0.72 (0.73) | 0.013 |
|  |  | resub, singleton mean | 1.000 | 1.00 | 0.004 | 0.73 (0.73) | 0.018 |
|  |  | resub, token-aggregated | 0.999 | 1.00 | 0.009 | 0.74 (0.73) | 0.018 |
|  |  | ShadowGen | 0.995 | 1.00 | 0.023 | 0.72 (0.73) | 0.076 |
|  |  | ShadowGen bounded | 1.000 | 1.00 | 0.005 | 0.73 (0.73) | 0.013 |
|  |  | strict resub, case-weighted | 0.998 | 1.00 | 0.021 | 1.00 (1.00) | 0.083 |
|  |  | strict resub, singleton mean | 1.000 | 1.00 | 0.005 | 1.00 (1.00) | 0.015 |
|  |  | strict ShadowGen | 1.000 | 1.00 | 0.095 | 0.70 (1.00) | 0.292 |
|  |  | strict ShadowGen bounded | 1.000 | 1.00 | 0.011 | 0.98 (1.00) | 0.048 |
| L2 | temporal | resub, case-weighted | 0.977 | 1.00 | 0.042 | 0.72 (0.82) | 0.120 |
|  |  | resub, variant mean | 0.997 | 1.00 | 0.019 | 0.86 (0.82) | 0.055 |
|  |  | resub, singleton mean | 0.994 | 1.00 | 0.024 | 0.88 (0.82) | 0.076 |
|  |  | resub, token-aggregated | 0.998 | 1.00 | 0.014 | 0.80 (0.82) | 0.032 |
|  |  | ShadowGen | 0.994 | 1.00 | 0.022 | 0.77 (0.82) | 0.069 |
|  |  | ShadowGen bounded | 0.994 | 1.00 | 0.022 | 0.77 (0.82) | 0.069 |
|  |  | strict resub, case-weighted | 0.988 | 0.89 | 0.067 | 1.00 (1.00) | 0.183 |
|  |  | strict resub, singleton mean | 0.998 | 0.89 | 0.025 | 1.00 (1.00) | 0.075 |
|  |  | strict ShadowGen | 0.997 | 0.94 | 0.027 | 0.99 (1.00) | 0.079 |
|  |  | strict ShadowGen bounded | 0.997 | 0.94 | 0.027 | 0.99 (1.00) | 0.079 |
| L2 | random | resub, case-weighted | 0.937 | 1.00 | 0.068 | 0.69 (0.87) | 0.212 |
|  |  | resub, variant mean | 1.000 | 1.00 | 0.006 | 0.86 (0.87) | 0.021 |
|  |  | resub, singleton mean | 1.000 | 1.00 | 0.002 | 0.87 (0.87) | 0.004 |
|  |  | resub, token-aggregated | 0.982 | 1.00 | 0.039 | 0.78 (0.87) | 0.124 |
|  |  | ShadowGen | 0.962 | 1.00 | 0.052 | 0.74 (0.87) | 0.177 |
|  |  | ShadowGen bounded | 0.962 | 1.00 | 0.052 | 0.74 (0.87) | 0.177 |
|  |  | strict resub, case-weighted | 0.986 | 0.89 | 0.071 | 1.00 (1.00) | 0.190 |
|  |  | strict resub, singleton mean | 0.998 | 0.89 | 0.024 | 1.00 (1.00) | 0.066 |
|  |  | strict ShadowGen | 0.993 | 1.00 | 0.043 | 0.99 (1.00) | 0.116 |
|  |  | strict ShadowGen bounded | 0.993 | 1.00 | 0.043 | 0.99 (1.00) | 0.116 |
| L3 | temporal | resub, case-weighted | 1.000 | 1.00 | 0.007 | 0.59 (0.61) | 0.018 |
|  |  | resub, variant mean | 1.000 | 1.00 | 0.001 | 0.61 (0.61) | 0.002 |
|  |  | resub, singleton mean | 1.000 | 1.00 | 0.001 | 0.61 (0.61) | 0.002 |
|  |  | resub, token-aggregated | 1.000 | 1.00 | 0.003 | 0.61 (0.61) | 0.005 |
|  |  | ShadowGen | 1.000 | 1.00 | 0.002 | 0.61 (0.61) | 0.003 |
|  |  | ShadowGen bounded | 1.000 | 1.00 | 0.003 | 0.60 (0.61) | 0.005 |
|  |  | strict resub, case-weighted | 0.947 | 1.00 | 0.054 | 1.00 (1.00) | 0.325 |
|  |  | strict resub, singleton mean | 1.000 | 1.00 | 0.004 | 1.00 (1.00) | 0.022 |
|  |  | strict ShadowGen | 0.991 | 1.00 | 0.026 | 0.96 (1.00) | 0.123 |
|  |  | strict ShadowGen bounded | 0.990 | 1.00 | 0.023 | 1.00 (1.00) | 0.135 |
| L3 | random | resub, case-weighted | 0.998 | 1.00 | 0.011 | 0.56 (0.58) | 0.023 |
|  |  | resub, variant mean | 1.000 | 1.00 | 0.001 | 0.57 (0.58) | 0.003 |
|  |  | resub, singleton mean | 1.000 | 1.00 | 0.000 | 0.58 (0.58) | 0.001 |
|  |  | resub, token-aggregated | 0.999 | 1.00 | 0.007 | 0.58 (0.58) | 0.024 |
|  |  | ShadowGen | 1.000 | 1.00 | 0.002 | 0.58 (0.58) | 0.005 |
|  |  | ShadowGen bounded | 1.000 | 1.00 | 0.002 | 0.58 (0.58) | 0.005 |
|  |  | strict resub, case-weighted | 0.951 | 1.00 | 0.073 | 1.00 (1.00) | 0.302 |
|  |  | strict resub, singleton mean | 1.000 | 1.00 | 0.001 | 1.00 (1.00) | 0.004 |
|  |  | strict ShadowGen | 1.000 | 1.00 | 0.010 | 0.98 (1.00) | 0.027 |
|  |  | strict ShadowGen bounded | 1.000 | 1.00 | 0.007 | 1.00 (1.00) | 0.030 |
| L5 | temporal | resub, case-weighted | 0.978 | 0.94 | 0.065 | 0.67 (0.51) | 0.247 |
|  |  | resub, variant mean | 0.988 | 1.00 | 0.077 | 0.69 (0.51) | 0.225 |
|  |  | resub, singleton mean | 0.988 | 1.00 | 0.081 | 0.70 (0.51) | 0.227 |
|  |  | resub, token-aggregated | 0.982 | 0.94 | 0.066 | 0.66 (0.51) | 0.236 |
|  |  | ShadowGen | 0.965 | 0.89 | 0.074 | 0.71 (0.51) | 0.294 |
|  |  | ShadowGen bounded | 0.988 | 1.00 | 0.073 | 0.67 (0.51) | 0.234 |
|  |  | strict resub, case-weighted | 0.746 | 1.00 | 0.149 | 1.00 (1.00) | 0.819 |
|  |  | strict resub, singleton mean | 0.765 | 1.00 | 0.142 | 1.00 (1.00) | 0.775 |
|  |  | strict ShadowGen | 0.659 | 0.89 | 0.176 | 0.96 (1.00) | 0.789 |
|  |  | strict ShadowGen bounded | 0.755 | 1.00 | 0.143 | 1.00 (1.00) | 0.799 |
| L5 | random | resub, case-weighted | 0.997 | 1.00 | 0.019 | 0.66 (0.73) | 0.070 |
|  |  | resub, variant mean | 1.000 | 1.00 | 0.004 | 0.72 (0.73) | 0.011 |
|  |  | resub, singleton mean | 1.000 | 1.00 | 0.001 | 0.73 (0.73) | 0.003 |
|  |  | resub, token-aggregated | 0.999 | 1.00 | 0.022 | 0.66 (0.73) | 0.063 |
|  |  | ShadowGen | 0.987 | 0.94 | 0.038 | 0.70 (0.73) | 0.092 |
|  |  | ShadowGen bounded | 0.999 | 1.00 | 0.009 | 0.71 (0.73) | 0.019 |
|  |  | strict resub, case-weighted | 0.987 | 1.00 | 0.042 | 1.00 (1.00) | 0.214 |
|  |  | strict resub, singleton mean | 1.000 | 1.00 | 0.001 | 1.00 (1.00) | 0.005 |
|  |  | strict ShadowGen | 0.999 | 0.94 | 0.072 | 0.78 (1.00) | 0.225 |
|  |  | strict ShadowGen bounded | 1.000 | 1.00 | 0.004 | 1.00 (1.00) | 0.019 |
