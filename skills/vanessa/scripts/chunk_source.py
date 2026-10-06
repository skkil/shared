#!/usr/bin/env python3
"""chunk_source: inventory long sources and split them into chunks small enough to read in full.

Chunks follow the source's own structure (chapters, sections, slides, speaker turns, pages) and
never cut a page or section in half unless that unit alone is too big. Every chunk file marks the
exact locator of each piece inside it, so a ledger entry can cite page, section or timestamp.

Work folder layout (default .vanessa/work/<task>):
  sources.jsonl          one row per source: id, path, kind, title, author, date, size, structure
  chunks/manifest.jsonl  one row per chunk: id, source, locators, chars, est_tokens, flags
  chunks/S01-C001.md     the chunk text, with === locator === markers between segments
  ledger.jsonl           written by Vanessa while reading (see references/long-source-ingestion.md)
  exclusions.md          written by Vanessa: | ID | Reason |

Usage
  python scripts/chunk_source.py inventory SRC... --work DIR
  python scripts/chunk_source.py chunk SRC... --work DIR [--max-tokens 6000] [--ocr]
  python scripts/chunk_source.py status --work DIR        which chunks have ledger entries
  python scripts/chunk_source.py next --work DIR          path of the next unread chunk

SRC may be a file or a directory. A directory (a repository, a folder of notes) becomes one source
whose locators start with file=<relative path>.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sourcelib  # noqa: E402

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next", ".idea",
             ".gradle", "target", ".mypy_cache", ".pytest_cache", "vendor", ".vanessa", ".design", ".jennifer"}
MAX_FILE_BYTES = 2_000_000


def est_tokens(text: str) -> int:
    return max(1, round(len(text.encode("utf-8")) / 3.6))


def load_jsonl(path: Path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


DATA_EXT = {".csv", ".tsv", ".jsonl", ".ndjson", ".log", ".lock", ".svg"}
DATA_JSON_BYTES = 100_000


def is_data_file(p: Path) -> bool:
    ext = p.suffix.lower()
    return ext in DATA_EXT or (ext == ".json" and p.stat().st_size > DATA_JSON_BYTES)


def walk_dir(root: Path, skipped=None, include_data=False):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for f in sorted(filenames):
            p = Path(dirpath) / f
            too_big = p.stat().st_size > MAX_FILE_BYTES
            if too_big or (not include_data and is_data_file(p)) or sourcelib.kind_of(p) == "unknown":
                if skipped is not None and not f.startswith("."):
                    reason = "over 2 MB" if too_big else ("data file" if is_data_file(p) else "unsupported format")
                    skipped.setdefault(reason, []).append(p.relative_to(root).as_posix())
                continue
            yield p


def pdf_meta(path: Path):
    try:
        from pypdf import PdfReader
        info = PdfReader(str(path)).metadata or {}
        return {"title": str(info.get("/Title") or ""), "author": str(info.get("/Author") or ""),
                "date": str(info.get("/CreationDate") or "")[2:10]}
    except Exception:
        return {}


def is_blank_page(path: Path, page_index: int) -> bool:
    try:
        img = sourcelib.pdf_render(path, page_index, dpi=30).convert("L")
    except SystemExit:
        return False
    hist = img.histogram()
    dark = sum(hist[:200])
    return dark / max(1, img.width * img.height) < 0.003


def source_segments(src: Path, ocr: bool, skipped=None, include_data=False):
    if src.is_dir():
        segs = []
        for f in walk_dir(src, skipped, include_data):
            rel = f.relative_to(src).as_posix()
            kind, fsegs = sourcelib.segments(f, ocr=ocr)
            for s in fsegs:
                s["locator"] = f"file={rel};{s['locator']}"
                s["heading"] = rel + (f" > {s['heading']}" if s.get("heading") else "")
                s["file_start"] = s is fsegs[0]
                segs.append(s)
        return "directory", segs
    kind, segs = sourcelib.segments(src, ocr=ocr)
    if kind == "pdf":
        for s in segs:
            if s.get("needs_ocr"):
                s["blank"] = is_blank_page(src, s["page"] - 1)
                s["needs_ocr"] = not s["blank"]
    return kind, segs


def describe(src: Path, kind: str, segs):
    row = {"path": str(src), "kind": kind, "segments": len(segs),
           "chars": sum(len(s["text"]) for s in segs), "est_tokens": sum(est_tokens(s["text"]) for s in segs)}
    if kind == "pdf":
        row.update({k: v for k, v in pdf_meta(src).items() if v})
        row["pages"] = len(segs)
        row["structure"] = sorted({s["heading"] for s in segs if s.get("heading")}, key=lambda h: next(
            i for i, s in enumerate(segs) if s.get("heading") == h))[:200]
        row["blank_pages"] = [s["page"] for s in segs if s.get("blank")]
        row["needs_ocr_pages"] = [s["page"] for s in segs if s.get("needs_ocr")]
    elif kind == "transcript":
        row["duration"] = sourcelib.hms(max((s.get("end") or 0) for s in segs)) if segs else "00:00:00"
        row["speakers"] = sorted({s.get("speaker") for s in segs if s.get("speaker")})
    elif kind == "directory":
        row["files"] = len({s["locator"].split(";")[0] for s in segs})
    else:
        row["structure"] = [s["heading"] for s in segs if s.get("heading")][:200]
    if "date" not in row:
        row["date"] = time.strftime("%Y-%m-%d", time.localtime(src.stat().st_mtime)) + " (file modified)"
    row.setdefault("title", src.stem if src.is_file() else src.name)
    return row


def inventory(srcs, work: Path, ocr=False, include_data=False):
    rows = load_jsonl(work / "sources.jsonl")
    by_path = {r["path"]: r for r in rows}
    cache = {}
    for raw in srcs:
        src = Path(raw).resolve()
        skipped = {}
        kind, segs = source_segments(src, ocr, skipped, include_data)
        cache[str(src)] = (kind, segs)
        row = describe(src, kind, segs)
        if skipped:
            row["set_aside"] = {k: {"count": len(v), "examples": v[:5]} for k, v in skipped.items()}

        if str(src) in by_path:
            row["id"] = by_path[str(src)]["id"]
            for keep in ("tier", "credibility", "url", "author", "title", "date", "notes"):
                if by_path[str(src)].get(keep) and keep not in {"title", "date"}:
                    row[keep] = by_path[str(src)][keep]
            by_path[str(src)].update(row)
        else:
            row["id"] = f"S{len(by_path) + 1:02d}"
            row.update({"tier": "", "credibility": "", "url": ""})
            by_path[str(src)] = row
    rows = sorted(by_path.values(), key=lambda r: r["id"])
    write_jsonl(work / "sources.jsonl", rows)
    return rows, cache


def pack(segs, max_tokens):
    chunks, cur, cur_tok = [], [], 0
    for s in segs:
        if s.get("blank"):
            continue
        t = est_tokens(s["text"])
        boundary = s.get("starts_section") or s.get("file_start") or bool(s.get("heading") and cur and
                                                                          s["heading"].split(" > ")[0] != cur[-1].get("heading", "").split(" > ")[0])
        if cur and (cur_tok + t > max_tokens or (boundary and cur_tok > 0.6 * max_tokens)):
            chunks.append(cur)
            cur, cur_tok = [], 0
        if t > max_tokens:
            paras = []
            for para in re.split(r"\n\s*\n", s["text"]):
                if est_tokens(para) <= max_tokens:
                    paras.append(para)
                    continue
                buf = []
                for line in para.split("\n"):
                    if buf and est_tokens("\n".join(buf + [line])) > max_tokens:
                        paras.append("\n".join(buf))
                        buf = []
                    buf.append(line[: max_tokens * 3])
                if buf:
                    paras.append("\n".join(buf))
            part, ptok, n = [], 0, 1
            for p in paras:
                pt = est_tokens(p)
                if part and ptok + pt > max_tokens:
                    chunks.append([dict(s, text="\n\n".join(part), locator=f"{s['locator']};part={n}")])
                    part, ptok, n = [], 0, n + 1
                part.append(p)
                ptok += pt
            if part:
                cur, cur_tok = [dict(s, text="\n\n".join(part), locator=f"{s['locator']};part={n}")], ptok
            continue
        cur.append(s)
        cur_tok += t
    if cur:
        chunks.append(cur)
    return chunks


def chunk(srcs, work: Path, max_tokens: int, ocr: bool, include_data=False):
    rows, cache = inventory(srcs, work, ocr, include_data)
    cdir = work / "chunks"
    cdir.mkdir(parents=True, exist_ok=True)
    manifest = [m for m in load_jsonl(cdir / "manifest.jsonl")]
    for row in rows:
        if row["path"] not in cache:
            continue
        manifest = [m for m in manifest if m["source"] != row["id"]]
        for old in cdir.glob(f"{row['id']}-C*.md"):
            old.unlink()
        kind, segs = cache[row["path"]]
        for n, group in enumerate(pack(segs, max_tokens), 1):
            cid = f"{row['id']}-C{n:03d}"
            parts = []
            for s in group:
                label = f" (printed p. {s['label']})" if s.get("label") and str(s.get("label")) != str(s.get("page")) else ""
                head = f" | {s['heading']}" if s.get("heading") else ""
                flag = " | NEEDS OCR: text layer empty, read the rendered page" if s.get("needs_ocr") else ""
                parts.append(f"=== [{s['locator']}]{label}{head}{flag} ===\n{s['text'].strip()}")
            body = (f"<!-- chunk {cid} | source {row['id']} {row.get('title', '')} | read every line; "
                    f"ledger IDs for this chunk start with {cid}- -->\n\n" + "\n\n".join(parts) + "\n")
            (cdir / f"{cid}.md").write_text(body, encoding="utf-8")
            manifest.append({"id": cid, "source": row["id"], "path": str(cdir / f"{cid}.md"),
                             "first": group[0]["locator"], "last": group[-1]["locator"],
                             "headings": sorted({s.get("heading", "") for s in group if s.get("heading")})[:12],
                             "chars": sum(len(s["text"]) for s in group),
                             "est_tokens": sum(est_tokens(s["text"]) for s in group),
                             "needs_ocr": [s["locator"] for s in group if s.get("needs_ocr")]})
    manifest.sort(key=lambda m: m["id"])
    write_jsonl(cdir / "manifest.jsonl", manifest)
    return rows, manifest


def progress(work: Path):
    manifest = load_jsonl(work / "chunks" / "manifest.jsonl")
    ledger = load_jsonl(work / "ledger.jsonl")
    excl_text = (work / "exclusions.md").read_text(encoding="utf-8") if (work / "exclusions.md").exists() else ""
    counts = {}
    for e in ledger:
        cid = e.get("chunk") or "-".join(str(e.get("id", "")).split("-")[:2])
        counts[cid] = counts.get(cid, 0) + 1
    out = []
    for m in manifest:
        whole = re.search(rf"^\|\s*{re.escape(m['id'])}\s*\|", excl_text, re.M) is not None
        out.append({**m, "entries": counts.get(m["id"], 0), "done": counts.get(m["id"], 0) > 0 or whole,
                    "excluded_whole": whole})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("inventory", "chunk"):
        p = sub.add_parser(name)
        p.add_argument("sources", nargs="+")
        p.add_argument("--work", required=True)
        p.add_argument("--ocr", action="store_true", help="OCR pages with no text layer (needs Tesseract)")
        p.add_argument("--include-data", action="store_true",
                       help="also read data files (csv, jsonl, logs, JSON over 100 KB) in directory sources")
        if name == "chunk":
            p.add_argument("--max-tokens", type=int, default=6000)
    for name in ("status", "next"):
        p = sub.add_parser(name)
        p.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    work = Path(args.work)
    if args.cmd == "inventory":
        rows, _ = inventory(args.sources, work, args.ocr, args.include_data)
        for r in rows:
            extra = {k: r[k] for k in ("pages", "duration", "files", "blank_pages", "needs_ocr_pages") if r.get(k)}
            print(f"{r['id']}  {r['kind']:<10} {r.get('title', '')[:50]:<50} {r['est_tokens']:>8} tok  date {r.get('date', '?')}  {extra}")
        print(f"wrote {work / 'sources.jsonl'}")
        return 0
    if args.cmd == "chunk":
        rows, manifest = chunk(args.sources, work, args.max_tokens, args.ocr, args.include_data)
        for r in rows:
            mine = [m for m in manifest if m["source"] == r["id"]]
            print(f"{r['id']}  {r.get('title', '')[:50]:<50} {len(mine):>3} chunks, "
                  f"max {max((m['est_tokens'] for m in mine), default=0)} tok")
            for m in mine:
                if m["needs_ocr"]:
                    print(f"   {m['id']}: needs OCR or a visual read at {', '.join(m['needs_ocr'][:5])}")
            for reason, info in (r.get("set_aside") or {}).items():
                print(f"   set aside ({reason}): {info['count']} files, e.g. {', '.join(info['examples'][:3])}; "
                      f"exclude them with one reason, or rerun with --include-data")
            if r.get("blank_pages"):
                print(f"   blank pages skipped (log them as excluded: blank): {r['blank_pages']}")
        print(f"wrote {work / 'chunks'}")
        return 0
    rows = progress(work)
    if args.cmd == "status":
        done = sum(r["done"] for r in rows)
        print(f"{done}/{len(rows)} chunks read")
        for r in rows:
            mark = "x" if r["done"] else " "
            note = "excluded whole" if r["excluded_whole"] else f"{r['entries']} entries"
            print(f"  [{mark}] {r['id']}  {r['first']} … {r['last']}  ({r['est_tokens']} tok, {note})")
        return 0
    nxt = next((r for r in rows if not r["done"]), None)
    print(nxt["path"] if nxt else "all chunks read")
    return 0


if __name__ == "__main__":
    sys.exit(main())
