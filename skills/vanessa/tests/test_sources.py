import importlib.util
import json
import zipfile

import pytest

import chunk_source
import extract_excerpts as ex
import sourcelib
from conftest import make_pdf

HAS_PDF = importlib.util.find_spec("pypdf") or importlib.util.find_spec("pypdfium2")


def test_markdown_heading_excerpt(tmp_path):
    f = tmp_path / "notes.md"
    f.write_text("# Intro\n\nHello.\n\n## Refunds\n\nRefunds take five days.\nThey need a receipt.\n\n## Other\n\nSkip.\n")
    text, _ = ex.resolve(f, {"locator": 'heading="Refunds"'})
    assert "five days" in text and "Skip" not in text


def test_transcript_time_excerpt(tmp_path):
    f = tmp_path / "m.vtt"
    f.write_text("WEBVTT\n\n00:00:01.000 --> 00:00:04.000\n<v Minji>We cap retries at three.\n\n"
                 "00:00:05.000 --> 00:00:08.000\n<v Joon>Agreed.\n\n00:01:00.000 --> 00:01:02.000\n<v Minji>Next topic.\n")
    text, _ = ex.resolve(f, {"locator": "time=00:00:00-00:00:09"})
    assert "Minji: We cap retries" in text and "Next topic" not in text
    segs = sourcelib.read_transcript(f)
    assert segs[0]["speaker"] == "Minji"


def test_docx_sections(tmp_path):
    f = tmp_path / "d.docx"
    w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    body = (f'<w:document xmlns:w="{w}"><w:body>'
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Scope</w:t></w:r></w:p>'
            '<w:p><w:r><w:t>Applies to all staff.</w:t></w:r></w:p></w:body></w:document>')
    with zipfile.ZipFile(f, "w") as z:
        z.writestr("word/document.xml", body)
    segs = sourcelib.read_docx(f)
    assert segs[0]["heading"] == "Scope" and "all staff" in segs[0]["text"]


def test_anchor_not_found_raises(tmp_path):
    f = tmp_path / "n.md"
    f.write_text("Some text here.\n")
    with pytest.raises(ex.LocatorError):
        ex.resolve(f, {"locator": "lines=1-1", "from": "missing words"})


@pytest.mark.skipif(not HAS_PDF, reason="no PDF library")
def test_pdf_chunk_and_excerpt(tmp_path):
    pdf = tmp_path / "book.pdf"
    make_pdf(pdf, ["Chapter one\nCompound interest is added to the principal each period.", "Chapter two\nSimple interest is not."])
    work = tmp_path / "w"
    rows, manifest = chunk_source.chunk([str(pdf)], work, 6000, False)
    assert rows[0]["pages"] == 2 and manifest
    text, pages = ex.resolve(pdf, {"locator": "pages=1", "from": "Compound interest", "to": "each period."})
    assert text.startswith("Compound interest") and pages == [1]
    status = chunk_source.progress(work)
    assert status and not status[0]["done"]
    (work / "ledger.jsonl").write_text(json.dumps({"id": status[0]["id"] + "-01", "chunk": status[0]["id"]}) + "\n")
    assert chunk_source.progress(work)[0]["done"]
