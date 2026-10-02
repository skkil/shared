#!/usr/bin/env python3
"""Experiment sample size and duration (two-sided test), or the smallest detectable effect at your traffic.

Proportions (conversion-style metrics):
  python sample_size.py --baseline 0.12 --mde 0.02 --daily-traffic 800        absolute lift (12% -> 14%)
  python sample_size.py --baseline 0.12 --mde-rel 0.15 --daily-traffic 800    relative lift (12% -> 13.8%)
  python sample_size.py --baseline 0.12 --daily-traffic 800 --weeks 4         smallest detectable lift in 4 weeks
Means (continuous metrics, e.g. minutes per session):
  python sample_size.py --mean 14 --sd 9 --mde 1.5 --daily-traffic 800
Options: --alpha 0.05 --power 0.8 --arms 2. daily-traffic = eligible users entering the experiment per day, all arms.
Rule of thumb: if the test needs more than about 6 weeks, use low-traffic methods instead (see metrics-experiments.md).
"""
import argparse, math
from statistics import NormalDist

Z = NormalDist().inv_cdf


def n_prop(p1, p2, alpha, power):
    pbar = (p1 + p2) / 2
    za, zb = Z(1 - alpha / 2), Z(power)
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (p2 - p1) ** 2)


def n_mean(sd, delta, alpha, power):
    return math.ceil(2 * (Z(1 - alpha / 2) + Z(power)) ** 2 * sd ** 2 / delta ** 2)


def report(n, arms, daily):
    total = n * arms
    print(f"Sample size: {n:,} per arm, {total:,} total.")
    if daily:
        days = math.ceil(total / daily)
        weeks = math.ceil(days / 7)
        print(f"Duration at {daily:,.0f}/day: {days} days -> run {weeks} full week(s) ({weeks * 7} days) to cover weekly cycles.")
        if weeks > 6:
            print("Over ~6 weeks: consider a bolder change, a broader population, or low-traffic methods (fake door, "
                  "before/after with caveats, qualitative tests). Label results directional.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline", type=float, help="baseline proportion, e.g. 0.12")
    ap.add_argument("--mean", type=float); ap.add_argument("--sd", type=float)
    ap.add_argument("--mde", type=float, help="absolute minimum detectable effect")
    ap.add_argument("--mde-rel", type=float, help="relative MDE, e.g. 0.15 for +15%%")
    ap.add_argument("--daily-traffic", type=float)
    ap.add_argument("--weeks", type=float, help="solve for the smallest detectable effect in this many weeks")
    ap.add_argument("--alpha", type=float, default=0.05); ap.add_argument("--power", type=float, default=0.8)
    ap.add_argument("--arms", type=int, default=2)
    a = ap.parse_args()
    print(f"alpha={a.alpha} (two-sided), power={a.power}, arms={a.arms}")
    if a.baseline is not None:
        p1 = a.baseline
        if a.weeks:
            if not a.daily_traffic:
                raise SystemExit("--weeks needs --daily-traffic")
            n_avail = a.daily_traffic * a.weeks * 7 / a.arms
            lo, hi = 1e-6, 1 - p1 - 1e-9
            for _ in range(200):
                mid = (lo + hi) / 2
                if n_prop(p1, p1 + mid, a.alpha, a.power) > n_avail:
                    lo = mid
                else:
                    hi = mid
            print(f"With {n_avail:,.0f} users per arm over {a.weeks:g} weeks, the smallest detectable lift from {p1:.2%} is "
                  f"+{hi:.2%} absolute ({hi / p1:.0%} relative), i.e. {p1:.2%} -> {p1 + hi:.2%}.")
            return
        d = a.mde if a.mde is not None else (p1 * a.mde_rel if a.mde_rel is not None else None)
        if d is None:
            raise SystemExit("Give --mde or --mde-rel (or --weeks)")
        p2 = p1 + d
        if not 0 < p2 < 1:
            raise SystemExit("baseline + MDE must be between 0 and 1")
        print(f"Detecting {p1:.2%} -> {p2:.2%} ({d / p1:+.0%} relative)")
        report(n_prop(p1, p2, a.alpha, a.power), a.arms, a.daily_traffic)
    elif a.mean is not None and a.sd is not None:
        if a.weeks:
            n_avail = a.daily_traffic * a.weeks * 7 / a.arms
            delta = math.sqrt(2 * (Z(1 - a.alpha / 2) + Z(a.power)) ** 2 * a.sd ** 2 / n_avail)
            print(f"Smallest detectable difference in {a.weeks:g} weeks: {delta:.3g} ({delta / a.mean:.1%} of the mean).")
            return
        d = a.mde if a.mde is not None else a.mean * a.mde_rel
        print(f"Detecting a difference of {d:g} on a mean of {a.mean:g} (sd {a.sd:g})")
        report(n_mean(a.sd, d, a.alpha, a.power), a.arms, a.daily_traffic)
    else:
        raise SystemExit("Give --baseline (proportions) or --mean and --sd (means)")


if __name__ == "__main__":
    main()
