#!/usr/bin/env python3
"""Market sizing: TAM / SAM / SOM, top-down and/or bottom-up, with low/base/high ranges.

Every numeric input accepts a single value or LOW:BASE:HIGH (e.g. 4000:6000:9000). Shares are fractions (0.05 = 5%).
  Bottom-up:  TAM = buyers x price x purchases per year      (--bottom-up --buyers --price [--freq])
  Top-down:   TAM = published total market                    (--top-down --total)
  Both:       SAM = TAM x sam_share ; SOM = SAM x som_share   (--sam-share --som-share)
Give both --bottom-up and --top-down inputs to get a reconciliation note.

Examples:
  python size.py --bottom-up --buyers 4000:6000:9000 --price 60000:90000:120000 --freq 1 \
      --sam-share 0.4:0.5:0.6 --som-share 0.02:0.05:0.08 --currency KRW
  python size.py --top-down --total 1.2e12:1.5e12:1.8e12 --sam-share 0.05:0.08:0.1 --som-share 0.01:0.03:0.05
Note: the 'low' column multiplies all lows together (and 'high' all highs), so it spans an extreme range;
the sensitivity table shows which single input moves SOM most. Label inputs with evidence in the write-up.
"""
import argparse


def rng(s):
    if s is None:
        return None
    parts = [float(x) for x in str(s).split(":")]
    if len(parts) == 1:
        return (parts[0],) * 3
    if len(parts) == 3:
        return tuple(parts)
    raise SystemExit(f"Bad range '{s}': use VALUE or LOW:BASE:HIGH")


def fmt(v, cur):
    if cur and cur.upper() == "KRW":
        for unit, d in (("조", 1e12), ("억", 1e8), ("만", 1e4)):
            if abs(v) >= d:
                return f"{v / d:,.1f}{unit}원"
        return f"{v:,.0f}원"
    for unit, d in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(v) >= d:
            return f"{(cur + ' ') if cur else ''}{v / d:,.2f}{unit}"
    return f"{(cur + ' ') if cur else ''}{v:,.0f}"



def compute(inputs, mode):
    out = {}
    if mode == "bottom":
        out["TAM"] = tuple(b * p * f for b, p, f in zip(inputs["buyers"], inputs["price"], inputs["freq"]))
    else:
        out["TAM"] = inputs["total"]
    out["SAM"] = tuple(t * s for t, s in zip(out["TAM"], inputs["sam"]))
    out["SOM"] = tuple(t * s for t, s in zip(out["SAM"], inputs["som"]))
    return out


def table(title, res, cur):
    print(f"### {title}\n\n| | Low | Base | High |\n|---|---|---|---|")
    for k in ("TAM", "SAM", "SOM"):
        print(f"| {k} | {fmt(res[k][0], cur)} | {fmt(res[k][1], cur)} | {fmt(res[k][2], cur)} |")
    print()


def sensitivity(inputs, mode, cur):
    base_inputs = {k: (v[1],) * 3 for k, v in inputs.items()}
    base_som = compute(base_inputs, mode)["SOM"][1]
    rows = []
    for k, v in inputs.items():
        if v[0] == v[2]:
            continue
        lo_in = dict(base_inputs); lo_in[k] = (v[0],) * 3
        hi_in = dict(base_inputs); hi_in[k] = (v[2],) * 3
        lo, hi = compute(lo_in, mode)["SOM"][1], compute(hi_in, mode)["SOM"][1]
        rows.append((abs(hi - lo), k, lo, hi))
    if rows:
        print("Sensitivity of SOM (one input at its low/high, others at base):\n\n| Input | SOM at low | SOM at high | Swing |\n|---|---|---|---|")
        for swing, k, lo, hi in sorted(rows, reverse=True):
            print(f"| {k} | {fmt(lo, cur)} | {fmt(hi, cur)} | {fmt(swing, cur)} |")
        print(f"\nBase SOM {fmt(base_som, cur)}. The top row is the assumption to validate first.\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bottom-up", action="store_true")
    ap.add_argument("--top-down", action="store_true")
    ap.add_argument("--buyers"); ap.add_argument("--price"); ap.add_argument("--freq", default="1")
    ap.add_argument("--total")
    ap.add_argument("--sam-share", required=True); ap.add_argument("--som-share", required=True)
    ap.add_argument("--currency", default="")
    a = ap.parse_args()
    if not (a.bottom_up or a.top_down):
        raise SystemExit("Choose --bottom-up and/or --top-down")
    shared = {"sam": rng(a.sam_share), "som": rng(a.som_share)}
    results = {}
    if a.bottom_up:
        if not (a.buyers and a.price):
            raise SystemExit("--bottom-up needs --buyers and --price")
        inp = {"buyers": rng(a.buyers), "price": rng(a.price), "freq": rng(a.freq), **shared}
        results["bottom"] = compute(inp, "bottom")
        table("Bottom-up (buyers x price x frequency)", results["bottom"], a.currency)
        sensitivity(inp, "bottom", a.currency)
    if a.top_down:
        if not a.total:
            raise SystemExit("--top-down needs --total")
        inp = {"total": rng(a.total), **shared}
        results["top"] = compute(inp, "top")
        table("Top-down (published total x shares)", results["top"], a.currency)
        sensitivity(inp, "top", a.currency)
    if len(results) == 2:
        b, t = results["bottom"]["TAM"][1], results["top"]["TAM"][1]
        ratio = max(b, t) / max(min(b, t), 1e-9)
        print(f"### Reconciliation\n\nBase TAM: bottom-up {fmt(b, a.currency)} vs top-down {fmt(t, a.currency)} (ratio {ratio:.1f}x).")
        if ratio > 3:
            print("The methods disagree by more than 3x: check definitions (who counts as a buyer, geography, year), "
                  "then state which estimate you trust and why. Bottom-up is usually easier to defend.")
        else:
            print("The methods broadly agree; report the range and the bottom-up logic.")


if __name__ == "__main__":
    main()
