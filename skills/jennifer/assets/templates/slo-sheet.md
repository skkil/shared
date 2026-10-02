# SLO sheet: <product>

| Critical journey | SLI (good ÷ valid events) | Measured where | SLO | Window | Owner |
|---|---|---|---|---|---|
| e.g., Sync a file | Sync jobs completing successfully within 30 s ÷ all sync jobs | Client-reported completion | 99.5% | 28 days | Emil |

**Error-budget policy:** while budget remains, ___. When exhausted, ___ until ___. Exceptions: ___. Approved by ___ on ___.

**Alerts:** burn-rate alerts per SLO (fast burn pages; slow burn tickets), owners.

**Client quality targets:** Core Web Vitals at p75 (LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1) · Android user-perceived crash rate < 1.09%, ANR < 0.47% · crash-free users ≥ ___% per release.

**Review cadence:** weekly in product health; quarterly SLO review.
