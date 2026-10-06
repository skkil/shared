import json

import coverage_check as cc


def setup_work(tmp_path, exclusions="", doc=""):
    work = tmp_path / "w"
    (work / "chunks").mkdir(parents=True)
    ledger = [{"id": "S01-C001-01", "source": "S01", "chunk": "S01-C001", "locator": "pages=1", "text": "a"},
              {"id": "S01-C001-02", "source": "S01", "chunk": "S01-C001", "locator": "pages=1", "text": "b"}]
    (work / "ledger.jsonl").write_text("".join(json.dumps(x) + "\n" for x in ledger), encoding="utf-8")
    (work / "chunks" / "manifest.jsonl").write_text(json.dumps({"id": "S01-C001", "source": "S01", "first": "pages=1", "last": "pages=1"}) + "\n" +
                                                    json.dumps({"id": "S01-C002", "source": "S01", "first": "pages=2", "last": "pages=2"}) + "\n")
    (work / "exclusions.md").write_text(exclusions, encoding="utf-8")
    d = tmp_path / "doc.md"
    d.write_text(doc, encoding="utf-8")
    return work, d


def test_missing_entry_and_unread_chunk_fail(tmp_path):
    work, doc = setup_work(tmp_path, doc="# A\n\nClaim [S01-C001-01].\n")
    _, _, _, findings, _ = cc.analyse(work, [doc])
    msgs = " ".join(m for _, _, m in findings)
    assert "neither cited nor excluded" in msgs and "never read" in msgs


def test_full_coverage_passes(tmp_path):
    work, doc = setup_work(tmp_path, exclusions="| S01-C001-02 | duplicate of S01-C001-01 |\n| S01-C002 | blank page |\n",
                           doc="# A\n\nClaim [S01-C001-01].\n")
    assert cc.main(["check", "--work", str(work), str(doc)]) == 0


def test_invented_citation_and_vague_reason_fail(tmp_path):
    work, doc = setup_work(tmp_path, exclusions="| S01-C001-02 | n/a |\n| S01-C002 | blank page |\n",
                           doc="# A\n\nClaim [S01-C001-01] and [S09-C001-01].\n")
    _, _, _, findings, _ = cc.analyse(work, [doc])
    fails = [i for lvl, i, _ in findings if lvl == "FAIL"]
    assert "S09-C001-01" in fails and "S01-C001-02" in fails
