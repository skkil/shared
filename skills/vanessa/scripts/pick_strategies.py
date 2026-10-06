#!/usr/bin/env python3
"""pick_strategies: real randomness for creative copy, so options differ in strategy, not wording.

A model asked for "three headline options" tends to write one idea three ways. This script deals
distinct strategies from the library in references/copy-strategies.md, filtered by format and by the
voice guide, and avoids strategies used recently. Vanessa then writes one option per strategy and
names the strategy with a one-line reason it might work.

Usage
  python scripts/pick_strategies.py pick --format headline [--n 3] [--require problem-led]
                                         [--avoid playful] [--voice .vanessa/voice.md] [--seed S]
  python scripts/pick_strategies.py list [--format cta]
  python scripts/pick_strategies.py record STRATEGY_ID      remember a winner so future picks vary

Formats: headline, tagline, cta, name, hook, concept, subject, social, store, push, all
History is kept in .vanessa/strategy_history.json when a .vanessa folder exists.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import secrets
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "references" / "copy-strategies.md"
HIST = Path(".vanessa/strategy_history.json")


def load_library():
    rows = []
    for line in LIB.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 5:
            continue
        rows.append({"id": c[0].strip("`"), "name": c[1], "formats": {x.strip() for x in c[2].split(",")},
                     "avoid_when": c[3], "how": c[4], "risk": c[5] if len(c) > 5 else ""})
    return rows


def voice_avoid(path):
    if not path or not Path(path).exists():
        return set()
    m = re.search(r"```vanessa-config\s*\n(.*?)```", Path(path).read_text(encoding="utf-8"), re.S)
    try:
        return set(json.loads(m.group(1)).get("strategies_avoid", [])) if m else set()
    except json.JSONDecodeError:
        return set()


def history():
    try:
        return json.loads(HIST.read_text(encoding="utf-8")) if HIST.exists() else []
    except json.JSONDecodeError:
        return []


def pick(args):
    lib = load_library()
    want = args.format
    pool = [s for s in lib if want == "all" or want in s["formats"] or "all" in s["formats"]]
    banned = set(args.avoid or []) | voice_avoid(args.voice)
    pool = [s for s in pool if s["id"] not in banned]
    required = [s for s in lib if s["id"] in set(args.require or [])]
    unknown = set(args.require or []) - {s["id"] for s in lib}
    if unknown:
        print(f"unknown strategy: {', '.join(sorted(unknown))} (see pick_strategies.py list)")
        return 1
    pool = [s for s in pool if s["id"] not in {r["id"] for r in required}]
    seed = args.seed or secrets.token_hex(4)
    rng = random.Random(seed)
    recent = history()[-12:]
    weights = [0.35 if s["id"] in recent else 1.0 for s in pool]
    chosen = list(required)
    while len(chosen) < args.n and pool:
        s = rng.choices(pool, weights=weights, k=1)[0]
        i = pool.index(s)
        pool.pop(i)
        weights.pop(i)
        chosen.append(s)
    print(f"format={want} seed={seed} (rerun with --seed {seed} to reproduce)")
    for s in chosen:
        tag = " (you asked for this one)" if s in required else ""
        print(f"\n- {s['id']}: {s['name']}{tag}\n  how: {s['how']}\n  skip when: {s['avoid_when']}\n  risk: {s['risk']}")
    if len(chosen) < args.n:
        print(f"\nonly {len(chosen)} strategies fit this format and voice; write fewer options rather than reword one")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pick")
    p.add_argument("--format", default="headline")
    p.add_argument("--n", type=int, default=3)
    p.add_argument("--require", nargs="*")
    p.add_argument("--avoid", nargs="*")
    p.add_argument("--voice", default=".vanessa/voice.md")
    p.add_argument("--seed")
    lp = sub.add_parser("list")
    lp.add_argument("--format", default="all")
    r = sub.add_parser("record")
    r.add_argument("strategy")
    args = ap.parse_args(argv)
    if args.cmd == "pick":
        return pick(args)
    if args.cmd == "list":
        for s in load_library():
            if args.format == "all" or args.format in s["formats"] or "all" in s["formats"]:
                print(f"{s['id']:<18} {s['name']:<32} {', '.join(sorted(s['formats']))}")
        return 0
    if not HIST.parent.exists():
        print("no .vanessa folder here; nothing recorded")
        return 0
    h = history() + [args.strategy]
    HIST.write_text(json.dumps(h[-50:]), encoding="utf-8")
    print(f"recorded {args.strategy}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
