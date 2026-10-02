#!/usr/bin/env python3
"""Asset library: search before generating, rate after generating, never throw anything away.

Ratings
  keep     use as-is (or with light finishing)
  salvage  flawed, but has usable parts: crop, recolor, key out, pixelate, composite (post.py)
  reject   not usable now; still kept on disk and searchable (a future brief may want it)

Commands
  list   [--tag T] [--rating R] [--plan P]
  find   WORDS... [--tag T]              rank existing assets against a new need
  show   ID
  rate   ID keep|salvage|reject [--note "why / what part is salvageable"]
  tag    ID TAG [TAG...]
  import FILE [--tags ...] [--source user|stock|code] [--note ...]   register non-generated assets
  sheet  [--plan P | --tag T | --ids A-0001,A-0002] [--out review/sheet.png]   labeled contact sheet
  lineage ID                              show what an asset was derived from / into
  spend                                   cost by tag and by rating (how much was salvaged)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import designlib as dl  # noqa: E402


def fmt(a: dict) -> str:
    return (f"{a['id']}  [{a.get('rating','unrated'):8}] {a['kind']:9} {a['source']:14} "
            f"${a.get('cost_usd',0):.3f}  {a['file']}  tags={','.join(a.get('tags', []))}"
            + (f"  note={a['notes']}" if a.get("notes") else ""))


def cmd_list(args, r):
    for a in dl.lib_load(r)["assets"]:
        if args.tag and args.tag not in a.get("tags", []):
            continue
        if args.rating and a.get("rating") != args.rating:
            continue
        if args.plan and a.get("plan_id") != args.plan:
            continue
        print(fmt(a))


def cmd_find(args, r):
    hits = dl.search(r, args.words, args.tag)
    if not hits:
        print("no matches: a new generation may be justified (still consider code-drawn or post-processed options)")
    for a in hits[:15]:
        print(fmt(a))
        if a.get("prompt"):
            print("      prompt:", a["prompt"][:160])


def cmd_show(args, r):
    rec, p = dl.find_asset(r, args.id)
    if not rec:
        dl.die("not found")
    print(json.dumps(rec, indent=2, ensure_ascii=False))
    print("path:", p)


def _update(r, aid, fn):
    lib = dl.lib_load(r)
    for a in lib["assets"]:
        if a["id"] == aid:
            fn(a)
            dl.lib_save(r, lib)
            print(fmt(a))
            return
    dl.die(f"unknown asset {aid}")


def cmd_rate(args, r):
    def f(a):
        a["rating"] = args.rating
        if args.note:
            a["notes"] = args.note
    _update(r, args.id, f)


def cmd_tag(args, r):
    _update(r, args.id, lambda a: a.__setitem__("tags", sorted(set(a.get("tags", []) + args.tags))))


def cmd_import(args, r):
    src = Path(args.file)
    if not src.exists():
        dl.die(f"missing {src}")
    dest_dir = r / "assets" / "imported"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    kind = {".png": "image", ".jpg": "image", ".jpeg": "image", ".webp": "image", ".svg": "image",
            ".gif": "animation", ".glb": "model3d", ".mp4": "video", ".webm": "video"}.get(dest.suffix.lower(), "other")
    rec = dl.register(r, dest, kind=kind, source=args.source, tags=args.tags or [], notes=args.note or "",
                      rating="keep" if args.source in ("user", "code") else "unrated")
    print(fmt(rec))


def cmd_sheet(args, r):
    from PIL import Image, ImageDraw
    lib = dl.lib_load(r)["assets"]
    ids = set(args.ids.split(",")) if args.ids else None
    sel = [a for a in lib if (not ids or a["id"] in ids) and (not args.plan or a.get("plan_id") == args.plan)
           and (not args.tag or args.tag in a.get("tags", []))]
    tiles = []
    for a in sel:
        p = r / a["file"]
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
            continue
        try:
            im = Image.open(p)
            im.seek(0)
            im = im.convert("RGBA")
        except Exception:
            continue
        tiles.append((a, im))
    if not tiles:
        dl.die("no raster assets matched")
    cell = args.cell
    cols = min(args.cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 26)), (236, 236, 232))
    d = ImageDraw.Draw(sheet)
    for i, (a, im) in enumerate(tiles):
        x, y = (i % cols) * cell, (i // cols) * (cell + 26)
        # checkerboard so transparency is visible
        for cy in range(0, cell, 16):
            for cx in range(0, cell, 16):
                if (cx // 16 + cy // 16) % 2:
                    d.rectangle([x + cx, y + cy, x + cx + 15, y + cy + 15], fill=(214, 214, 210))
        t = im.copy()
        resample = Image.NEAREST if max(im.size) <= 256 else Image.LANCZOS  # keep pixel art crisp
        t.thumbnail((cell - 8, cell - 8), resample)
        if max(im.size) <= 256:
            scale = max(1, (cell - 8) // max(im.size))
            t = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        sheet.paste(t, (x + (cell - t.width) // 2, y + (cell - t.height) // 2), t)
        d.text((x + 6, y + cell + 6), f"{a['id']} {a.get('rating','')}", fill=(20, 20, 20))
    out = Path(args.out) if args.out else r / "review" / "contact-sheet.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(out)


def cmd_lineage(args, r):
    lib = {a["id"]: a for a in dl.lib_load(r)["assets"]}
    if args.id not in lib:
        dl.die("unknown id")

    def up(aid, depth=0):
        a = lib[aid]
        print("  " * depth + f"{aid} {a.get('op') or a['source']} {a['file']}")
        for p in a.get("derived_from", []):
            if p in lib:
                up(p, depth + 1)
    print("ancestry:")
    up(args.id)
    kids = [a for a in lib.values() if args.id in a.get("derived_from", [])]
    print("derivatives:", ", ".join(f"{k['id']}({k.get('op')})" for k in kids) or "none")


def cmd_spend(args, r):
    lib = dl.lib_load(r)["assets"]
    by_rating, by_tag = {}, {}
    for a in lib:
        c = a.get("cost_usd", 0) or 0
        by_rating[a.get("rating", "unrated")] = by_rating.get(a.get("rating", "unrated"), 0) + c
        for t in a.get("tags", []):
            by_tag[t] = by_tag.get(t, 0) + c
    used_parents = {p for a in lib for p in a.get("derived_from", [])}
    salvaged = sum(a.get("cost_usd", 0) for a in lib if a["id"] in used_parents and a.get("rating") in ("salvage", "reject"))
    print("by rating:", {k: round(v, 3) for k, v in by_rating.items()})
    print("by tag:", {k: round(v, 3) for k, v in sorted(by_tag.items(), key=lambda x: -x[1])})
    print(f"spend recovered through salvage/derivation: ${salvaged:.3f}")
    print(f"ledger total: ${dl.ledger_total(r):.2f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("list"); p.add_argument("--tag"); p.add_argument("--rating"); p.add_argument("--plan")
    p = sp.add_parser("find"); p.add_argument("words", nargs="+"); p.add_argument("--tag", action="append")
    p = sp.add_parser("show"); p.add_argument("id")
    p = sp.add_parser("rate"); p.add_argument("id"); p.add_argument("rating", choices=["keep", "salvage", "reject", "unrated"])
    p.add_argument("--note")
    p = sp.add_parser("tag"); p.add_argument("id"); p.add_argument("tags", nargs="+")
    p = sp.add_parser("import"); p.add_argument("file"); p.add_argument("--tags", nargs="*")
    p.add_argument("--source", default="user", choices=["user", "stock", "code", "other"]); p.add_argument("--note")
    p = sp.add_parser("sheet"); p.add_argument("--plan"); p.add_argument("--tag"); p.add_argument("--ids")
    p.add_argument("--out"); p.add_argument("--cell", type=int, default=256); p.add_argument("--cols", type=int, default=5)
    p = sp.add_parser("lineage"); p.add_argument("id")
    sp.add_parser("spend")
    args = ap.parse_args()
    r = dl.root(args.root)
    globals()["cmd_" + args.cmd.replace("-", "_")](args, r)


if __name__ == "__main__":
    main()
