#!/usr/bin/env python3
"""sourcelib: one way to read every source format, shared by chunk_source.py and extract_excerpts.py.

Every reader returns segments: the smallest natural units of a source (a PDF page, a Markdown
section, a speaker turn, a slide), each with a precise locator a reader can follow back to the
original. Because chunking and excerpt extraction use the same readers, a locator written while
reading a chunk always resolves to the same text when the excerpt is pulled.

Formats: PDF, EPUB, DOCX, PPTX, Markdown, HTML, plain text and notes, transcripts (.vtt, .srt,
Whisper-style .json, and .txt with [hh:mm:ss] stamps), and source code.

Heavy libraries load only when a format needs them:
  PDF text   pypdfium2, then pypdf, then the pdftotext command
  PDF render pypdfium2, then the pdftoppm command
  OCR        pytesseract with the Tesseract binary (Korean needs the kor language pack)

Usage
  python scripts/sourcelib.py formats          list supported formats and which readers are available
  python scripts/sourcelib.py segments FILE    print the segments and locators a file produces
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

CODE_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".kt", ".go", ".rs", ".rb", ".php", ".c", ".h",
            ".cc", ".cpp", ".hpp", ".cs", ".swift", ".m", ".scala", ".sh", ".sql", ".yaml", ".yml", ".toml",
            ".ini", ".cfg", ".gradle", ".dart", ".vue", ".svelte", ".proto", ".tf"}
TEXT_EXT = {".txt", ".text", ".notes", ".log", ".rst", ".adoc", ".org", ".csv", ".tsv"}
TS = re.compile(r"\[?(\d{1,2}:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?\]?")


def kind_of(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext == ".epub":
        return "epub"
    if ext == ".docx":
        return "docx"
    if ext == ".pptx":
        return "pptx"
    if ext in {".md", ".markdown", ".mdx"}:
        return "md"
    if ext in {".html", ".htm", ".xhtml"}:
        return "html"
    if ext in {".vtt", ".srt"}:
        return "transcript"
    if ext == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("segments"), list):
                return "transcript"
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        return "code"
    if ext in CODE_EXT:
        return "code"
    if ext in TEXT_EXT or ext == "":
        try:
            head = path.read_text(encoding="utf-8", errors="ignore")[:3000]
        except OSError:
            return "text"
        if len(re.findall(r"^\s*\[?\d{1,2}:\d{2}(:\d{2})?\]?\s", head, re.M)) >= 3:
            return "transcript"
        return "text"
    return "unknown"


def seg(locator, text, heading="", page=None, label=None, start=None, end=None, **extra):
    d = {"locator": locator, "heading": heading, "text": text}
    if page is not None:
        d["page"] = page
    if label is not None:
        d["label"] = label
    if start is not None:
        d["start"], d["end"] = start, end
    d.update(extra)
    return d


# ---------- PDF ----------

def clean_pdf_text(t: str) -> str:
    """Normalize line endings and rejoin words the PDF hyphenated across lines (U+FFFE, U+00AD)."""
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"[\ufffe\u00ad]\s*\n\s*", "", t)
    return t.replace("\ufffe", "").replace("\u00ad", "")


def pdf_page_texts(path: Path):
    """Return a list of page texts (1-based order) using the best available extractor."""
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(str(path))
        out = []
        for i in range(len(pdf)):
            tp = pdf[i].get_textpage()
            out.append(clean_pdf_text(tp.get_text_range()))
        return out
    except ImportError:
        pass
    try:
        from pypdf import PdfReader
        return [clean_pdf_text(p.extract_text() or "") for p in PdfReader(str(path)).pages]
    except ImportError:
        pass
    if shutil.which("pdftotext"):
        raw = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True).stdout
        return raw.split("\f")[:-1] if raw.endswith("\f") else raw.split("\f")
    raise SystemExit("No PDF text extractor found. Install one: pip install pypdfium2 (or pypdf).")


def pdf_labels_and_outline(path: Path, n_pages: int):
    """Printed page labels and an outline [(level, title, page_index)] when the PDF provides them."""
    labels, outline = [str(i + 1) for i in range(n_pages)], []
    try:
        from pypdf import PdfReader
    except ImportError:
        return labels, outline
    try:
        r = PdfReader(str(path))
        try:
            got = list(r.page_labels)
            if len(got) == n_pages:
                labels = got
        except Exception:
            pass

        def walk(items, level):
            for it in items:
                if isinstance(it, list):
                    walk(it, level + 1)
                    continue
                try:
                    outline.append((level, str(it.title).strip(), r.get_destination_page_number(it)))
                except Exception:
                    continue
        walk(r.outline, 1)
    except Exception:
        pass
    return labels, outline


def pdf_page_objects(path: Path, index: int):
    """Count image and path objects on a page; used to decide whether to render it."""
    try:
        import pypdfium2 as pdfium
        import pypdfium2.raw as raw
    except ImportError:
        return {"images": 0, "paths": 0}
    page = pdfium.PdfDocument(str(path))[index]
    images = paths = 0
    for obj in page.get_objects():
        if obj.type == raw.FPDF_PAGEOBJ_IMAGE:
            images += 1
        elif obj.type == raw.FPDF_PAGEOBJ_PATH:
            paths += 1
    return {"images": images, "paths": paths}


def pdf_render(path: Path, index: int, dpi: int = 110, bbox=None):
    """Render one page (or a PDF-point bbox x0,y0,x1,y1 with origin bottom-left) to a PIL image."""
    try:
        import pypdfium2 as pdfium
        page = pdfium.PdfDocument(str(path))[index]
        scale = dpi / 72
        img = page.render(scale=scale).to_pil()
        if bbox:
            w, h = page.get_size()
            x0, y0, x1, y1 = bbox
            img = img.crop((int(x0 * scale), int((h - y1) * scale), int(x1 * scale), int((h - y0) * scale)))
        return img
    except ImportError:
        pass
    if shutil.which("pdftoppm"):
        import tempfile
        from PIL import Image
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(index + 1), "-l", str(index + 1), "-png",
                            str(path), f"{td}/p"], check=True)
            png = sorted(Path(td).glob("p*.png"))[0]
            img = Image.open(png)
            img.load()
            if bbox:
                s = dpi / 72
                x0, y0, x1, y1 = bbox
                img = img.crop((int(x0 * s), int(img.height - y1 * s), int(x1 * s), int(img.height - y0 * s)))
            return img
    raise SystemExit("No PDF renderer found. Install pypdfium2 or poppler-utils (pdftoppm).")


def ocr_image(img, langs="eng+kor"):
    try:
        import pytesseract
    except ImportError:
        return None
    try:
        have = set(pytesseract.get_languages(config=""))
        use = "+".join(x for x in langs.split("+") if x in have) or "eng"
        return pytesseract.image_to_string(img, lang=use)
    except Exception:
        return None


def read_pdf(path: Path, ocr=False):
    texts = pdf_page_texts(path)
    labels, outline = pdf_labels_and_outline(path, len(texts))
    starts = sorted(outline, key=lambda x: (x[2], x[0]))
    out = []
    for i, t in enumerate(texts):
        heads = [title for (lvl, title, pg) in starts if pg is not None and pg <= i]
        heading = heads[-1] if heads else ""
        needs_ocr = len(t.strip()) < 20
        if needs_ocr and ocr:
            got = ocr_image(pdf_render(path, i, dpi=200))
            if got and got.strip():
                t, needs_ocr = got, False
        out.append(seg(f"pages={i + 1}", t, heading=heading, page=i + 1, label=labels[i],
                       needs_ocr=needs_ocr,
                       starts_section=any(pg == i for (_, _, pg) in starts)))
    return out


# ---------- HTML-like ----------

class _Blocks(HTMLParser):
    BLOCK = {"p", "li", "pre", "blockquote", "td", "th", "dd", "dt", "figcaption", "div", "section", "tr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items, self.buf, self.tag_stack, self.skip = [], [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "nav", "noscript"}:
            self.skip += 1
        if re.fullmatch(r"h[1-6]", tag) or tag in self.BLOCK:
            self._flush()
        self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if tag in {"script", "style", "nav", "noscript"}:
            self.skip = max(0, self.skip - 1)
        if re.fullmatch(r"h[1-6]", tag):
            text = " ".join("".join(self.buf).split())
            self.buf = []
            if text:
                self.items.append(("h", int(tag[1]), text))
        elif tag in self.BLOCK or tag == "br":
            self._flush()

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)

    def _flush(self):
        text = "".join(self.buf).strip()
        self.buf = []
        if text:
            self.items.append(("p", 0, re.sub(r"[ \t]+", " ", text)))

    def close(self):
        super().close()
        self._flush()


def html_sections(html_text: str, prefix: str):
    p = _Blocks()
    p.feed(html_text)
    p.close()
    sections, path, cur = [], [], {"heading": "", "paras": []}
    for kind, level, text in p.items:
        if kind == "h":
            if cur["paras"] or cur["heading"]:
                sections.append(cur)
            path = path[: level - 1] + [text]
            cur = {"heading": " > ".join(path), "title": text, "paras": []}
        else:
            cur["paras"].append(text)
    if cur["paras"] or cur["heading"]:
        sections.append(cur)
    return [seg(f'{prefix}heading="{s.get("title", "")}"' if s.get("title") else f"{prefix}start",
                "\n\n".join(s["paras"]), heading=s["heading"]) for s in sections]


def read_html(path: Path):
    return html_sections(path.read_text(encoding="utf-8", errors="replace"), "")


def read_epub(path: Path):
    z = zipfile.ZipFile(path)
    container = ET.fromstring(z.read("META-INF/container.xml"))
    opf_path = container.find(".//{*}rootfile").get("full-path")
    opf = ET.fromstring(z.read(opf_path))
    base = str(Path(opf_path).parent).replace(".", "") if "/" in opf_path else ""
    manifest = {it.get("id"): it.get("href") for it in opf.find("{*}manifest")}
    out = []
    for n, ref in enumerate(opf.find("{*}spine"), 1):
        href = manifest.get(ref.get("idref"))
        if not href:
            continue
        name = f"{base}/{href}" if base else href
        try:
            html_text = z.read(name).decode("utf-8", errors="replace")
        except KeyError:
            continue
        for s in html_sections(html_text, f"chapter={href};"):
            s["chapter"] = n
            out.append(s)
    return out


# ---------- Office ----------

def read_docx(path: Path):
    z = zipfile.ZipFile(path)
    root = ET.fromstring(z.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    sections, path_h, cur = [], [], {"heading": "", "title": "", "paras": []}
    for p in root.iter(f"{{{ns['w']}}}p"):
        style = p.find("w:pPr/w:pStyle", ns)
        sval = style.get(f"{{{ns['w']}}}val") if style is not None else ""
        text = "".join(t.text or "" for t in p.iter(f"{{{ns['w']}}}t")).strip()
        m = re.match(r"(?i)heading\s?(\d)|title", sval or "")
        if m and text:
            level = int(m.group(1)) if m.group(1) else 1
            if cur["paras"] or cur["title"]:
                sections.append(cur)
            path_h = path_h[: level - 1] + [text]
            cur = {"heading": " > ".join(path_h), "title": text, "paras": []}
        elif text:
            cur["paras"].append(text)
    if cur["paras"] or cur["title"]:
        sections.append(cur)
    return [seg(f'heading="{s["title"]}"' if s["title"] else "start", "\n\n".join(s["paras"]), heading=s["heading"])
            for s in sections]


def read_pptx(path: Path):
    z = zipfile.ZipFile(path)
    names = sorted((n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                   key=lambda n: int(re.search(r"(\d+)", n.rsplit("/", 1)[1]).group(1)))
    out = []
    for n in names:
        num = int(re.search(r"slide(\d+)\.xml", n).group(1))
        root = ET.fromstring(z.read(n))
        paras = []
        for p in root.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}p"):
            t = "".join(x.text or "" for x in p.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t")).strip()
            if t:
                paras.append(t)
        notes_name = f"ppt/notesSlides/notesSlide{num}.xml"
        notes = ""
        if notes_name in z.namelist():
            nroot = ET.fromstring(z.read(notes_name))
            notes = " ".join(x.text or "" for x in nroot.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t")).strip()
        text = "\n".join(paras) + (f"\n\n[Speaker notes] {notes}" if notes else "")
        out.append(seg(f"slides={num}", text, heading=paras[0] if paras else f"Slide {num}", slide=num))
    return out


# ---------- Markdown, text, code ----------

def read_md(path: Path):
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    out, path_h, start, title, buf, fence = [], [], 1, "", [], False

    def flush(end):
        if any(x.strip() for x in buf) or title:
            out.append(seg(f'heading="{title}";lines={start}-{end}' if title else f"lines={start}-{end}",
                           "\n".join(buf).strip(), heading=" > ".join(path_h), start=start, end=end))

    for i, line in enumerate(lines, 1):
        if line.strip().startswith(("```", "~~~")):
            fence = not fence
        m = None if fence else re.match(r"(#{1,6})\s+(.*)", line)
        if m:
            flush(i - 1)
            level = len(m.group(1))
            title = m.group(2).strip().rstrip("#").strip()
            path_h = path_h[: level - 1] + [title]
            start, buf = i, []
            continue
        buf.append(line)
    flush(len(lines))
    return out


def read_text(path: Path):
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    out, buf, start = [], [], 1
    for i, line in enumerate(lines + [""], 1):
        if line.strip():
            if not buf:
                start = i
            buf.append(line)
        elif buf:
            out.append(seg(f"lines={start}-{i - 1}", "\n".join(buf), start=start, end=i - 1))
            buf = []
    return out


def read_code(path: Path, window=160):
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    out, start = [], 1
    while start <= len(lines):
        end = min(len(lines), start + window - 1)
        j = end
        while j > start + window // 2 and lines[j - 1].strip() and end < len(lines):
            j -= 1
        end = j if j > start + window // 2 else end
        out.append(seg(f"lines={start}-{end}", "\n".join(lines[start - 1: end]), start=start, end=end))
        start = end + 1
    return out


# ---------- transcripts ----------

def _secs(stamp: str) -> float:
    stamp = stamp.strip("[] ").replace(",", ".")
    parts = [float(x) for x in stamp.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def hms(sec: float) -> str:
    sec = int(round(sec))
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def transcript_cues(path: Path):
    """Return cues [(start_sec, end_sec, speaker, text)] for vtt, srt, json and stamped txt."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    cues = []
    if path.suffix.lower() == ".json":
        for s in json.loads(raw)["segments"]:
            cues.append((float(s.get("start", 0)), float(s.get("end", s.get("start", 0))),
                         s.get("speaker", ""), str(s.get("text", "")).strip()))
        return cues
    if path.suffix.lower() in {".vtt", ".srt"}:
        for block in re.split(r"\n\s*\n", raw.replace("\r\n", "\n")):
            m = re.search(r"([\d:.,]+)\s*-->\s*([\d:.,]+)", block)
            if not m:
                continue
            body = block[m.end():].strip()
            speaker = ""
            v = re.match(r"<v\s+([^>]+)>", body)
            if v:
                speaker = v.group(1).strip()
            body = re.sub(r"<[^>]+>", "", body)
            sp = re.match(r"([^:\n]{1,40}):\s+", body)
            if not speaker and sp:
                speaker, body = sp.group(1).strip(), body[sp.end():]
            cues.append((_secs(m.group(1)), _secs(m.group(2)), speaker, " ".join(body.split())))
        return cues
    last = 0.0
    for line in raw.split("\n"):
        m = re.match(r"\s*\[?((?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.,]\d+)?)\]?\s*(?:-\s*)?(?:([^:]{1,40}):\s*)?(.*)", line)
        if m and m.group(3).strip():
            last = _secs(m.group(1))
            cues.append((last, last, (m.group(2) or "").strip(), m.group(3).strip()))
        elif line.strip() and cues:
            s, e, spk, t = cues[-1]
            cues[-1] = (s, e, spk, f"{t} {line.strip()}")
    for i in range(len(cues) - 1):
        s, e, spk, t = cues[i]
        if e <= s:
            cues[i] = (s, cues[i + 1][0], spk, t)
    return cues


def read_transcript(path: Path):
    turns = []
    for s, e, spk, t in transcript_cues(path):
        if turns and turns[-1]["speaker"] == spk and s - turns[-1]["end"] < 8:
            turns[-1]["end"] = max(turns[-1]["end"], e)
            turns[-1]["text"] += " " + t
        else:
            turns.append({"start": s, "end": max(e, s), "speaker": spk, "text": t})
    return [seg(f"time={hms(t['start'])}-{hms(t['end'])}", (f"{t['speaker']}: " if t["speaker"] else "") + t["text"],
                heading=t["speaker"], start=t["start"], end=t["end"], speaker=t["speaker"]) for t in turns]


READERS = {"pdf": read_pdf, "epub": read_epub, "docx": read_docx, "pptx": read_pptx, "md": read_md,
           "html": read_html, "text": read_text, "code": read_code, "transcript": read_transcript}


def segments(path, ocr=False):
    path = Path(path)
    kind = kind_of(path)
    if kind == "unknown":
        raise SystemExit(f"Unsupported format: {path.name}. Convert it to PDF, Markdown or text first.")
    if kind == "pdf":
        return kind, read_pdf(path, ocr=ocr)
    return kind, READERS[kind](path)


def available():
    rows = []
    for mod in ("pypdfium2", "pypdf", "pytesseract", "PIL"):
        try:
            __import__(mod)
            rows.append((mod, "yes"))
        except ImportError:
            rows.append((mod, "no"))
    for cmd in ("pdftotext", "pdftoppm", "tesseract"):
        rows.append((cmd, "yes" if shutil.which(cmd) else "no"))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("formats", help="list formats and available readers")
    s = sub.add_parser("segments", help="print the segments of one file")
    s.add_argument("file")
    s.add_argument("--ocr", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "formats":
        print("formats: pdf, epub, docx, pptx, md, html, text/notes, transcript (vtt, srt, json, stamped txt), code")
        for name, ok in available():
            print(f"  {name:<12} {ok}")
        return 0
    kind, segs = segments(args.file, ocr=args.ocr)
    for s_ in segs:
        print(f"[{kind}] {s_['locator']}  ({len(s_['text'])} chars)  {s_.get('heading', '')[:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
