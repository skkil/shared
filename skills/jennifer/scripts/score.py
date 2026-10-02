#!/usr/bin/env python3
"""Reproducible prioritization scores with sensitivity analysis.

CSV columns (one row per item; a 'name' column is required; 'evidence'/'notes' columns are passed through):
  rice:        reach, impact (0.25/0.5/1/2/3), confidence (0-1 or 0-100), effort (person-weeks)
  ice:         impact, confidence, ease (each 1-10)
  wsjf:        value, time_criticality, risk_reduction, job_size
  opportunity: importance, satisfaction (each 0-10)   score = importance + max(importance - satisfaction, 0)

Usage:
  python score.py backlog.csv --method rice [--sensitivity] [--swing 0.3]
Sensitivity perturbs each input of each item by +/- swing (default 30%) one at a time and reports how far each
item's rank can move, and which input moves it most. Items whose rank swings deserve better evidence before deciding.
"""
import argparse, csv, sys

METHODS = {
    "rice": (["reach", "impact", "confidence", "effort"],
             lambda r: r["reach"] * r["impact"] * r["confidence"] / max(r["effort"], 1e-9)),
    "ice": (["impact", "confidence", "ease"], lambda r: r["impact"] * r["confidence"] * r["ease"]),
    "wsjf": (["value", "time_criticality", "risk_reduction", "job_size"],
             lambda r: (r["value"] + r["time_criticality"] + r["risk_reduction"]) / max(r["job_size"], 1e-9)),
    "opportunity": (["importance", "satisfaction"],
                    lambda r: r["importance"] + max(r["importance"] - r["satisfaction"], 0)),
}


def load(path, fields, method):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for raw in csv.DictReader(fh):
            raw = {k.strip().lower(): (v or "").strip() for k, v in raw.items() if k}
            if not raw.get("name"):
                continue
            r = {"name": raw["name"], "evidence": raw.get("evidence", raw.get("notes", ""))}
            for f in fields:
                try:
                    r[f] = float(raw[f])
                except (KeyError, ValueError):
                    sys.exit(f"Row '{raw.get('name')}': missing or non-numeric '{f}'")
            if method == "rice" and r["confidence"] > 1:
                r["confidence"] /= 100.0
            rows.append(r)
    return rows


def ranks(rows, fn):
    order = sorted(range(len(rows)), key=lambda i: -fn(rows[i]))
    return {i: pos + 1 for pos, i in enumerate(order)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--method", required=True, choices=METHODS)
    ap.add_argument("--sensitivity", action="store_true")
    ap.add_argument("--swing", type=float, default=0.3)
    a = ap.parse_args()
    fields, fn = METHODS[a.method]
    rows = load(a.file, fields, a.method)
    if not rows:
        sys.exit("No rows found.")
    base = ranks(rows, fn)
    print(f"## {a.method.upper()} ranking ({len(rows)} items)\n")
    print("| Rank | Item | Score | " + " | ".join(fields) + " | Evidence |")
    print("|---|---|---|" + "---|" * len(fields) + "---|")
    for i in sorted(base, key=base.get):
        r = rows[i]
        vals = " | ".join(f"{r[f]:g}" for f in fields)
        print(f"| {base[i]} | {r['name']} | {fn(r):.2f} | {vals} | {r['evidence']} |")
    if a.sensitivity:
        print(f"\n## Sensitivity (each input of each item varied ±{a.swing:.0%}, one at a time)\n")
        print("| Item | Base rank | Rank range | Most sensitive input |")
        print("|---|---|---|---|")
        unstable = 0
        for i in sorted(base, key=base.get):
            lo, hi, worst, worst_span = base[i], base[i], "-", 0
            for f in fields:
                rs = []
                for mult in (1 - a.swing, 1 + a.swing):
                    orig = rows[i][f]
                    rows[i][f] = orig * mult
                    if a.method == "rice" and f == "confidence":
                        rows[i][f] = min(rows[i][f], 1.0)
                    rs.append(ranks(rows, fn)[i])
                    rows[i][f] = orig
                span = max(rs) - min(rs)
                lo, hi = min([lo] + rs), max([hi] + rs)
                if span > worst_span:
                    worst, worst_span = f, span
            if hi != lo:
                unstable += 1
            print(f"| {rows[i]['name']} | {base[i]} | {lo}-{hi} | {worst} |")
        print(f"\n{unstable} of {len(rows)} items can change rank under a ±{a.swing:.0%} error in a single input.")


if __name__ == "__main__":
    main()
