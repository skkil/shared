#!/usr/bin/env python3
"""extract_excerpts: pull exact source sections into collapsible <details> dropdowns.

Vanessa decides which section supports each point and records its locator. This script pulls that
section from the source file itself, so the excerpt is verbatim, long passages carry no
transcription errors, and copyrighted books are reproduced only by the user's own tooling for
their private document. When a page holds equations, tables or figures that text extraction would
garble, the script renders that page (or a cropped region) as an image inside the dropdown.

Spec file (JSON list), one object per excerpt:
  {"id": "X07", "source": "books/finance.pdf", "locator": "pages=42-43",
   "from": "Compound interest is", "to": "each period.",          optional: trim inside the range
   "heading": "3.2 Compound interest",                          optional: section start (md/docx/html/epub/pdf)
   "title": "...", "author": "...", "year": "2019", "url": "https://...", "cite": "pp. 30-31",
   "lang": "en", "render": "auto|always|never", "region": "42:72,300,540,620"}
  source may also be a source id (S01) when --sources points at sources.jsonl.

Locators: pdf pages=N-M (physical page index, 1-based; cite printed numbers in "cite") ·
  md/text/code lines=A-B · md/docx/html heading="Title" · epub chapter=file.xhtml;heading="Title" ·
  pptx slides=N-M · transcript time=hh:mm:ss-hh:mm:ss · directory sources: file=rel/path;<locator>

Usage
  python scripts/extract_excerpts.py show SOURCE --locator "pages=42-43" [--from TEXT] [--to TEXT]
  python scripts/extract_excerpts.py build SPEC.json --out excerpts.html [--sources sources.jsonl]
  python scripts/extract_excerpts.py inject PAGE.html SPEC.json [-o OUT.html] [--sources sources.jsonl]
  python scripts/extract_excerpts.py check PAGE.html SPEC.json [--sources sources.jsonl]

inject replaces each <!-- excerpt:ID --> placeholder with its dropdown. check re-extracts every
excerpt and fails if the page no longer matches the source (sha256 per excerpt).
Exit code 1 when a locator or anchor cannot be resolved: fix the locator, never paste text by hand.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sourcelib  # noqa: E402

MATH = re.compile(r"[∑∫∂√≤≥≠≈±×÷∞πθλμσΣΠΔ∇→⇒⇔∀∃∈∉⊂⊆∪∩⌈⌉⌊⌋]")
MAX_RENDER_PAGES = 6


class LocatorError(Exception):
    pass


def parse_locator(loc: str):
    parts = {}
    for piece in re.findall(r'(\w+)=("[^"]*"|[^;]*)', loc or ""):
        parts[piece[0]] = piece[1].strip('"')
    return parts


def rng(value: str):
    a, _, b = value.partition("-")
    return int(a), int(b or a)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def trim(text: str, start: str | None, end: str | None) -> str:
    """Cut text from the first occurrence of start through end, matching across line breaks."""
    if not start and not end:
        return text.strip()
    flat, index = [], []
    prev_space = False
    for i, ch in enumerate(text):
        if ch.isspace():
            if not prev_space:
                flat.append(" ")
                index.append(i)
            prev_space = True
        else:
            flat.append(ch)
            index.append(i)
            prev_space = False
    flat_s = "".join(flat)
    low_s = flat_s.lower()

    def find(needle, at=0):
        i = flat_s.find(norm(needle), at)
        return i if i >= 0 else low_s.find(norm(needle).lower(), at)

    a = 0
    if start:
        a = find(start)
        if a < 0:
            raise LocatorError(f"start anchor not found: {start[:60]!r}")
    b = len(flat_s)
    if end:
        e = find(end, a)
        if e < 0:
            raise LocatorError(f"end anchor not found after start: {end[:60]!r}")
        b = e + len(norm(end))
    return text[index[a]: index[b - 1] + 1].strip()


def section_by_heading(segs, heading: str):
    want = norm(heading).lower()
    hit = [i for i, s in enumerate(segs) if norm(s.get("heading", "").split(" > ")[-1]).lower() == want]
    if not hit:
        hit = [i for i, s in enumerate(segs) if want in norm(s.get("heading", "")).lower()]
    if not hit:
        raise LocatorError(f"heading not found: {heading!r}")
    i = hit[0]
    depth = len(segs[i].get("heading", "").split(" > "))
    out = [segs[i]]
    for s in segs[i + 1:]:
        if len(s.get("heading", "").split(" > ")) <= depth and s.get("heading") and \
                s.get("heading").split(" > ")[:depth] != segs[i]["heading"].split(" > ")[:depth]:
            break
        out.append(s)
    return out


def resolve(source: Path, spec: dict):
    """Return (text, pdf_pages) for one excerpt spec."""
    loc = spec.get("locator", "")
    parts = parse_locator(loc)
    kind, segs = sourcelib.segments(source)
    if kind == "directory" or "file" in parts:
        raise LocatorError("for a directory source, pass the file itself as source")
    pages = []
    if kind == "pdf":
        texts = [s["text"] for s in segs]
        if "pages" not in parts:
            raise LocatorError("PDF excerpts need pages=N-M")
        a, b = rng(parts["pages"])
        if a < 1 or b > len(texts):
            raise LocatorError(f"pages {a}-{b} outside 1-{len(texts)}")
        pages = list(range(a, b + 1))
        body = "\n".join(texts[p - 1] for p in pages)
        start = spec.get("from") or spec.get("heading")
        return trim(body, start, spec.get("to")), pages
    if "heading" in parts or spec.get("heading"):
        chosen = section_by_heading(segs, parts.get("heading") or spec["heading"])
        if "chapter" in parts:
            chosen = [s for s in chosen if f"chapter={parts['chapter']};" in s["locator"]] or chosen
        body = "\n\n".join(s["text"] for s in chosen)
        return trim(body, spec.get("from"), spec.get("to")), pages
    if "lines" in parts:
        a, b = rng(parts["lines"])
        lines = source.read_text(encoding="utf-8", errors="replace").split("\n")
        if b > len(lines):
            raise LocatorError(f"lines {a}-{b} outside 1-{len(lines)}")
        return trim("\n".join(lines[a - 1: b]), spec.get("from"), spec.get("to")), pages
    if "slides" in parts:
        a, b = rng(parts["slides"])
        chosen = [s for s in segs if a <= s.get("slide", 0) <= b]
        if not chosen:
            raise LocatorError(f"slides {a}-{b} not found")
        return trim("\n\n".join(f"[Slide {s['slide']}]\n{s['text']}" for s in chosen), spec.get("from"), spec.get("to")), pages
    if "time" in parts:
        t0, _, t1 = parts["time"].partition("-")
        s0, s1 = sourcelib._secs(t0), sourcelib._secs(t1 or t0)
        cues = [c for c in sourcelib.transcript_cues(source) if c[1] >= s0 and c[0] <= s1]
        if not cues:
            raise LocatorError(f"no transcript cues between {t0} and {t1}")
        lines = [f"[{sourcelib.hms(c[0])}] " + (f"{c[2]}: " if c[2] else "") + c[3] for c in cues]
        return trim("\n".join(lines), spec.get("from"), spec.get("to")), pages
    raise LocatorError(f"cannot resolve locator {loc!r} for a {kind} source")


def needs_render(source: Path, pages, text: str, mode: str):
    if mode == "never" or not pages:
        return []
    if mode == "always":
        return pages[:MAX_RENDER_PAGES]
    picked = []
    texts = sourcelib.pdf_page_texts(source)
    for p in pages:
        t = texts[p - 1]
        objs = sourcelib.pdf_page_objects(source, p - 1)
        lines = [ln for ln in t.split("\n") if ln.strip()]
        numeric = sum(1 for ln in lines if len(re.findall(r"\b\d+(?:\.\d+)?\b", ln)) >= 3)
        reasons = []
        if len(MATH.findall(t)) >= 3:
            reasons.append("equations")
        if lines and numeric / len(lines) > 0.25:
            reasons.append("a table")
        if objs["images"] or objs["paths"] > 40:
            reasons.append("a figure")
        if len(t.strip()) < 40:
            reasons.append("no text layer")
        if reasons:
            picked.append((p, reasons))
    return picked[:MAX_RENDER_PAGES]


def render_pages(source: Path, picked, dpi: int, region=None):
    figs = []
    for item in picked:
        p, reasons = item if isinstance(item, tuple) else (item, ["requested"])
        bbox = None
        if region and int(region.split(":")[0]) == p:
            bbox = [float(x) for x in region.split(":")[1].split(",")]
        img = sourcelib.pdf_render(source, p - 1, dpi=dpi, bbox=bbox).convert("RGB")
        if img.width > 1100:
            img = img.resize((1100, int(img.height * 1100 / img.width)))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=78, optimize=True)
        figs.append((p, reasons, base64.b64encode(buf.getvalue()).decode("ascii")))
    return figs


def load_sources(path):
    if not path or not Path(path).exists():
        return {}
    rows = [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
    return {r["id"]: r for r in rows}


def build_one(spec: dict, sources: dict, dpi: int):
    src_ref = spec["source"]
    meta = dict(sources.get(src_ref, {}))
    source = Path(meta.get("path", src_ref))
    if not source.exists():
        raise LocatorError(f"source file not found: {source}")
    for k in ("title", "author", "year", "url", "date"):
        if spec.get(k):
            meta[k] = spec[k]
    text, pages = resolve(source, spec)
    picked = needs_render(source, pages, text, spec.get("render", "auto")) if pages else []
    if spec.get("region") and pages:
        rp = int(spec["region"].split(":")[0])
        picked = [(rp, ["the cropped region"])] + [x for x in picked if x[0] != rp]
    figs = render_pages(source, picked, dpi, spec.get("region")) if picked else []
    digest = hashlib.sha256(norm(text).encode("utf-8")).hexdigest()[:16]
    cite = spec.get("cite") or spec.get("locator", "")
    title = meta.get("title") or source.name
    who = ", ".join(x for x in (meta.get("author"), str(meta.get("year") or "")) if x)
    link = meta.get("url") or source.as_posix()
    lang = spec.get("lang", "")
    fig_html = "".join(
        f'<figure class="src-render"><img loading="lazy" alt="Page {p} of {html.escape(title)}, '
        f'shown as an image because it contains {html.escape(" and ".join(r))}" '
        f'src="data:image/jpeg;base64,{b64}"><figcaption>Page {p} as printed in the source</figcaption></figure>'
        for p, r, b64 in figs)
    block = (
        f'<details class="src-excerpt" id="excerpt-{html.escape(spec["id"])}" data-excerpt-id="{html.escape(spec["id"])}" '
        f'data-sha256="{digest}">\n'
        f'<summary>Source: {html.escape(title)}{", " + html.escape(who) if who else ""}, {html.escape(cite)}</summary>\n'
        f'<div class="src-body">\n'
        f'<p class="src-meta"><cite>{html.escape(title)}</cite>{" by " + html.escape(meta["author"]) if meta.get("author") else ""}'
        f'{" (" + html.escape(str(meta["year"])) + ")" if meta.get("year") else ""}, {html.escape(cite)}. '
        f'<a href="{html.escape(link)}">Open the original</a></p>\n'
        f'<div class="src-text"{f" lang={chr(34)}{html.escape(lang)}{chr(34)}" if lang else ""}>{html.escape(text)}</div>\n'
        f'{fig_html}\n</div>\n</details>')
    return block, digest, len(text), len(figs)


def run_build(specs, sources, dpi):
    blocks, errors = {}, []
    for spec in specs:
        try:
            block, digest, n, nf = build_one(spec, sources, dpi)
            blocks[spec["id"]] = (block, digest)
            print(f"  ok   {spec['id']}: {n} chars" + (f", {nf} rendered page(s)" if nf else ""))
        except (LocatorError, SystemExit) as exc:
            errors.append(spec.get("id", "?"))
            print(f"  FAIL {spec.get('id', '?')}: {exc}")
    return blocks, errors


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sh = sub.add_parser("show", help="print what a locator resolves to")
    sh.add_argument("source")
    sh.add_argument("--locator", required=True)
    sh.add_argument("--from", dest="from_")
    sh.add_argument("--to")
    sh.add_argument("--heading")
    for name in ("build", "inject", "check"):
        p = sub.add_parser(name)
        if name in ("inject", "check"):
            p.add_argument("page")
        p.add_argument("spec")
        p.add_argument("--sources")
        p.add_argument("--dpi", type=int, default=110)
        if name == "build":
            p.add_argument("--out", required=True)
        if name == "inject":
            p.add_argument("-o", "--output")
    args = ap.parse_args(argv)
    if args.cmd == "show":
        try:
            text, pages = resolve(Path(args.source), {"locator": args.locator, "from": args.from_, "to": args.to,
                                                      "heading": args.heading})
        except LocatorError as exc:
            print(f"FAIL: {exc}")
            return 1
        print(text)
        return 0
    specs = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    sources = load_sources(args.sources)
    blocks, errors = run_build(specs, sources, args.dpi)
    if args.cmd == "build":
        Path(args.out).write_text("\n\n".join(b for b, _ in blocks.values()) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    elif args.cmd == "inject":
        page = Path(args.page).read_text(encoding="utf-8")
        missing = []
        for xid, (block, _) in blocks.items():
            new = re.sub(rf"<!--\s*excerpt:{re.escape(xid)}\s*-->", lambda _m: block, page)
            if new == page:
                missing.append(xid)
            page = new
        left = re.findall(r"<!--\s*excerpt:([\w.-]+)\s*-->", page)
        out = Path(args.output or args.page)
        out.write_text(page, encoding="utf-8")
        print(f"wrote {out}; placeholders without a spec: {left or 'none'}; specs without a placeholder: {missing or 'none'}")
        errors += left
    else:
        page = Path(args.page).read_text(encoding="utf-8")
        for xid, (_, digest) in blocks.items():
            m = re.search(rf'data-excerpt-id="{re.escape(xid)}"\s+data-sha256="([0-9a-f]+)"', page)
            if not m:
                print(f"  FAIL {xid}: not in page")
                errors.append(xid)
            elif m.group(1) != digest:
                print(f"  FAIL {xid}: page differs from source; run inject again")
                errors.append(xid)
            else:
                print(f"  ok   {xid}: matches source")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
