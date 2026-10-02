#!/usr/bin/env python3
"""creative_roll: real randomness for design direction (an LLM cannot be random on its own).

It does two things the model can't do for itself:
  1. String-seed-of-thought: prints a fresh random seed string for the model to mine for
     inspiration (numbers, letter shapes, rhythms). Never shown in the design.
  2. Deals N materially different directions from curated decks (assets/decks/decks.json),
     filtered to fit the surface mode and platform, excluding recently used options.

The dealt directions are raw material, not orders: ground each in the product's real world,
replace anything that would make a false claim, and keep the brief's pinned choices (the brief wins).

Usage
  python scripts/creative_roll.py seed
  python scripts/creative_roll.py deal --mode persuade --platform web --n 3 [--register bold]
         [--lock world=risograph-zine] [--axes world,illustration,type_voice] [--seed abc]
  python scripts/creative_roll.py axis ground --mode operate        # re-roll a single axis
  python scripts/creative_roll.py list world                          # browse a deck
  python scripts/creative_roll.py record <direction-json-file>        # mark a chosen direction as used

Modes: persuade (landing, marketing, pricing) | operate (app UI, dashboards, tools) |
       read (docs, articles) | experience (portfolios, showcases, games) | marketing (assets, video)
Register: safe | balanced (default) | bold
"""
from __future__ import annotations

import argparse
import json
import random
import secrets
import string
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECKS = HERE.parent / "assets" / "decks" / "decks.json"
MODE_CODE = {"persuade": "P", "operate": "O", "read": "R", "experience": "E", "marketing": "M"}
AXES_DEFAULT = ["world", "palette_strategy", "ground", "type_voice", "layout", "hero", "motion",
                "illustration", "texture", "voice", "signature"]
OPERATE_SKIP = {"hero", "signature"}  # app surfaces get no hero; signature becomes optional delight
DIALS = {  # (variance, motion, density) ranges by mode
    "persuade": ((5, 9), (4, 8), (2, 5)), "operate": ((2, 5), (2, 4), (4, 8)),
    "read": ((3, 6), (1, 3), (3, 5)), "experience": ((6, 10), (5, 9), (2, 4)),
    "marketing": ((5, 9), (4, 9), (2, 5)),
}


def load_decks():
    d = json.loads(DECKS.read_text())
    return {k: v for k, v in d.items() if not k.startswith("_")}


def fits(item, mode_code):
    modes = item[3]
    return "*" in modes or mode_code in modes


def weight(item, register, used):
    e = item[4]
    w = {"safe": [3, 3, 2, 1, 0.4], "balanced": [1, 1.4, 1.6, 1.4, 1], "bold": [0.3, 0.7, 1.2, 2, 2.4]}[register][e - 1]
    if item[0] in used:
        w *= 0.08  # strongly avoid repeats across sessions, never impossible
    return w


def history(root: Path):
    p = root / "roll-history.jsonl"
    used = set()
    if p.exists():
        for line in p.read_text().splitlines()[-40:]:
            try:
                used.update(json.loads(line).get("ids", []))
            except Exception:
                pass
    return used


def pick(rng, items, register, used, exclude_families=(), exclude_ids=()):
    pool = [it for it in items if it[5] not in exclude_families and it[0] not in exclude_ids] or \
        [it for it in items if it[0] not in exclude_ids] or items
    ws = [weight(it, register, used) for it in pool]
    return rng.choices(pool, weights=ws, k=1)[0]


def describe(axis, it, rng):
    out = {"axis": axis, "id": it[0], "label": it[1], "detail": it[2]}
    if axis == "type_voice" and len(it) > 6:
        fams = list(it[6])
        rng.shuffle(fams)
        out["candidates"] = fams[:3]
    return out


def deal(args):
    decks = load_decks()
    mode_code = MODE_CODE[args.mode]
    seed = args.seed or secrets.token_hex(8)
    rng = random.Random(seed)
    root = Path(args.root) if args.root else Path.cwd() / ".design"
    used = history(root)
    axes = args.axes.split(",") if args.axes else [a for a in AXES_DEFAULT
                                                       if not (args.mode == "operate" and a in OPERATE_SKIP)]
    locks = dict(kv.split("=", 1) for kv in (args.lock or []))
    taken_families = {a: set() for a in axes}
    taken_ids = {a: set() for a in axes}
    directions = []
    for n in range(args.n):
        d = {"name": None, "picks": {}}
        for axis in axes:
            items = [it for it in decks[axis] if fits(it, mode_code)]
            if args.platform in ("ios", "android", "flutter", "desktop") and axis == "type_voice" and args.mode == "operate":
                items = [it for it in items if it[5] in ("native", "geometric", "grotesk", "rounded", "serif-text")] or items
            if axis in locks:
                it = next((x for x in decks[axis] if x[0] == locks[axis]), None) or sys.exit(f"unknown lock {locks[axis]}")
            else:
                distinct = axis in ("world", "illustration", "type_voice", "layout", "palette_strategy")
                it = pick(rng, items, args.register, used, taken_families[axis] if distinct else (), taken_ids[axis])
            taken_families[axis].add(it[5])
            taken_ids[axis].add(it[0])
            d["picks"][axis] = describe(axis, it, rng)
        v, m, dn = DIALS[args.mode]
        d["dials"] = {"variance": rng.randint(*v), "motion": rng.randint(*m), "density": rng.randint(*dn)}
        w = d["picks"].get("world", {}).get("label", "Direction")
        d["name"] = f"{chr(65 + n)}. {w}"
        directions.append(d)
    seed_string = "".join(rng.choice(string.ascii_letters + string.digits) for _ in range(48))
    result = {"seed": seed, "seed_string": seed_string, "mode": args.mode, "platform": args.platform,
              "register": args.register, "directions": directions}
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(f"# Creative roll  seed={seed}  mode={args.mode}  platform={args.platform}  register={args.register}")
    print(f"Seed string (inspiration only, never shown): {seed_string}\n")
    for d in directions:
        print(f"## {d['name']}")
        for axis, p in d["picks"].items():
            extra = f"  candidates: {', '.join(p['candidates'])}" if p.get("candidates") else ""
            print(f"- **{axis}**: {p['label']} - {p['detail']}{extra}")
        dl_ = d["dials"]
        print(f"- **dials**: variance {dl_['variance']}/10, motion {dl_['motion']}/10, density {dl_['density']}/10\n")
    print("Next: fuse each direction with the product's real world (who, where, what it proves). Replace any pick "
          "that would make a false claim or break the platform; never replace a pick just because it feels unfamiliar. "
          "Present the directions, then `record` the one the user chooses.")


def axis_cmd(args):
    decks = load_decks()
    rng = random.Random(args.seed or secrets.token_hex(8))
    root = Path(args.root) if args.root else Path.cwd() / ".design"
    items = [it for it in decks[args.axis] if fits(it, MODE_CODE[args.mode])]
    seen = set()
    for _ in range(min(args.n, len(items))):
        it = pick(rng, items, args.register, history(root), (), seen)
        seen.add(it[0])
        p = describe(args.axis, it, rng)
        print(f"- {p['label']}: {p['detail']}" + (f"  ({', '.join(p['candidates'])})" if p.get("candidates") else ""))


def list_cmd(args):
    for it in load_decks()[args.axis]:
        print(f"{it[0]:26} e{it[4]} [{it[3]}] {it[1]}: {it[2]}")


def record(args):
    data = json.loads(Path(args.file).read_text())
    ids = [p["id"] for p in data.get("picks", {}).values()] if "picks" in data else data.get("ids", [])
    root = Path(args.root) if args.root else Path.cwd() / ".design"
    root.mkdir(parents=True, exist_ok=True)
    with open(root / "roll-history.jsonl", "a") as fh:
        fh.write(json.dumps({"ids": ids, "name": data.get("name", "")}) + "\n")
    print(f"recorded {len(ids)} picks")


def seed_cmd(args):
    print(secrets.token_urlsafe(36))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("seed")
    p = sp.add_parser("deal")
    p.add_argument("--mode", default="persuade", choices=list(MODE_CODE))
    p.add_argument("--platform", default="web", choices=["web", "ios", "android", "flutter", "desktop", "marketing", "game", "other"])
    p.add_argument("--n", type=int, default=3)
    p.add_argument("--register", default="balanced", choices=["safe", "balanced", "bold"])
    p.add_argument("--lock", action="append")
    p.add_argument("--axes")
    p.add_argument("--seed")
    p.add_argument("--json", action="store_true")
    p = sp.add_parser("axis"); p.add_argument("axis"); p.add_argument("--mode", default="persuade", choices=list(MODE_CODE))
    p.add_argument("--register", default="balanced", choices=["safe", "balanced", "bold"]); p.add_argument("--n", type=int, default=3)
    p.add_argument("--seed")
    p = sp.add_parser("list"); p.add_argument("axis")
    p = sp.add_parser("record"); p.add_argument("file")
    a = ap.parse_args()
    {"seed": seed_cmd, "deal": deal, "axis": axis_cmd, "list": list_cmd, "record": record}[a.cmd](a)


if __name__ == "__main__":
    main()
