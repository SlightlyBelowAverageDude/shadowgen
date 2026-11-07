# v27 against the tested variant (extended rules, seen traces dropped)

pm4py 2.7.22.2; seed 42; 1,000 drawn traces; N=6, tau=5, mle; 162 s.

## A. Real logs

| log | rep | drawn | seen dropped | rule dropped | scored | same traces as the tested mask | models | largest strict difference to stored | largest graded difference to stored |
|---|---|---|---|---|---|---|---|---|---|
| D1 | 0 | 1000 | 0 | 376 | 624 | yes | 8 | 0.00e+00 (Trace_Filtered) | 3.27e-02 (Trace_Filtered) |
| D1 | 1 | 1000 | 0 | 356 | 644 | yes | 8 | 0.00e+00 (Trace_Filtered) | 1.12e-02 (Trace_Filtered) |
| D1 | 2 | 1000 | 0 | 369 | 631 | yes | 8 | 0.00e+00 (Trace_Filtered) | 9.08e-03 (Trace_Filtered) |
| D2 | 0 | 1000 | 0 | 8 | 992 | yes | 8 | 0.00e+00 (Trace_Filtered) | 1.58e-02 (Trace_Filtered) |
| D2 | 1 | 1000 | 0 | 10 | 990 | yes | 8 | 0.00e+00 (Trace_Filtered) | 2.11e-02 (Trace_Filtered) |
| D2 | 2 | 1000 | 0 | 8 | 992 | yes | 8 | 0.00e+00 (Trace_Filtered) | 7.82e-03 (Trace_Filtered) |

## B. Known systems

Systems: 12. Same traces as the tested mask: 12 of 12. Models with the same score: 96 of 96. Systems with seen traces dropped: 4. Systems with an empty scored set (score None): 4. v27 seen-dropped count equals the v26 duplicates count on 12 of 12.
