#!/usr/bin/env python3
"""coverage_check: prove that nothing in the sources disappeared silently.

The rule it enforces: every ledger entry is cited in the document or listed in the exclusion log
with a reason, every chunk was read, and every ID the document cites exists in the ledger (a
citation to a missing ID usually means an invented fact).

Ledger (ledger.jsonl), one JSON object per line:
  {"id": "S01-C003-07", "source": "S01", "chunk": "S01-C003", "locator": "pages=19", "cite": "p. 9",
   "kind": "fact|definition|claim|number|example|decision|procedure|question|quote",
   "text": "short restatement", "section": "planned section", "status": "ok|conflict|superseded",
   "conflicts_with": ["S02-C001-03"]}
IDs are <chunk id>-<two or more digits>, so parallel readers never collide.

Exclusion log (exclusions.md): table rows "| ID | Reason |". A chunk ID (S01-C004) excludes a whole
chunk, for example blank pages or an index. Reasons must say why: "duplicate of S01-C002-04",
"off-topic for this audience: ...", "superseded by S03-C001-02 (newer)".

Citations in documents: any ledger ID written in the text, a data-ledger="..." attribute, or an
HTML comment (<!-- S01-C003-07 -->). Put the ID next to the claim it supports.

Usage
  python scripts/coverage_check.py check --work DIR DOC... [--json]
  python scripts/coverage_check.py report --work DIR DOC... --out ledger-report.md|.html
Exit code 1 when any FAIL remains.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import signal
import sys
from pathlib import Path

ID = re.compile(r"\bS\d{2,}-C\d{3,}-\d{2,}\b")
CHUNK = re.compile(r"^S\d{2,}-C\d{3,}$")
VAGUE = re.compile(r"^(n/?a|none|not needed|irrelevant|skip(ped)?|unused|-|—)\.?$", re.I)


def load_jsonl(path: Path):
    if not path.exists():
        return []
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{n}: not valid JSON ({exc})")
    return rows


def load_exclusions(path: Path):
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if len(cells) >= 2 and (ID.fullmatch(cells[0]) or CHUNK.match(cells[0])):
            out[cells[0]] = cells[1]
    return out


def citations(docs):
    found = {}
    for d in docs:
        text = Path(d).read_text(encoding="utf-8")
        heading = "(top)"
        for line in text.split("\n"):
            h = re.match(r"\s*(#{1,6})\s+(.*)|.*<h[1-6][^>]*>(.*?)</h[1-6]>", line)
            if h:
                heading = re.sub(r"<[^>]+>", "", h.group(2) or h.group(3) or "").strip()[:60]
            for m in ID.finditer(line):
                found.setdefault(m.group(0), []).append(f"{Path(d).name} › {heading}")
    return found


def analyse(work: Path, docs):
    ledger = load_jsonl(work / "ledger.jsonl")
    manifest = load_jsonl(work / "chunks" / "manifest.jsonl")
    sources = load_jsonl(work / "sources.jsonl")
    excl = load_exclusions(work / "exclusions.md")
    cited = citations(docs)
    ids = {e["id"] for e in ledger}
    findings = []
    dupes = {i for i in ids if sum(1 for e in ledger if e["id"] == i) > 1}
    for i in sorted(dupes):
        findings.append(("FAIL", i, "ID used for two ledger entries"))
    for e in ledger:
        i = e["id"]
        if not ID.fullmatch(i):
            findings.append(("FAIL", i, "ID does not follow <chunk>-NN"))
        in_doc, in_ex = i in cited, i in excl
        if not in_doc and not in_ex:
            findings.append(("FAIL", i, f"neither cited nor excluded: {e.get('text', '')[:70]}"))
        if in_doc and in_ex:
            findings.append(("WARN", i, "cited and excluded at once; pick one"))
        if not e.get("locator") and not e.get("cite"):
            findings.append(("WARN", i, "no precise location (page, section, timestamp, file:line)"))
        if e.get("status") == "conflict" and in_doc:
            near = any("conflict" in w.lower() or "충돌" in w for w in cited.get(i, []))
            if not near and not any(c in cited for c in e.get("conflicts_with", [])):
                findings.append(("WARN", i, "conflicting entry cited without its counterpart; show both sides"))
    for i, reason in excl.items():
        if VAGUE.match(reason.strip()) or len(reason.strip()) < 8:
            findings.append(("FAIL", i, f"exclusion reason too vague: {reason!r}"))
        m = re.search(r"duplicate of (S\d{2,}-C\d{3,}-\d{2,})", reason)
        if m and m.group(1) not in ids:
            findings.append(("FAIL", i, f"says duplicate of {m.group(1)}, which is not in the ledger"))
        if ID.fullmatch(i) and i not in ids:
            findings.append(("WARN", i, "excluded ID is not in the ledger"))
    for i in sorted(set(cited) - ids):
        findings.append(("FAIL", i, f"cited in {cited[i][0]} but not in the ledger (invented or mistyped)"))
    entries_by_chunk = {}
    for e in ledger:
        entries_by_chunk.setdefault(e.get("chunk") or "-".join(e["id"].split("-")[:2]), []).append(e)
    for m in manifest:
        if m["id"] not in entries_by_chunk and m["id"] not in excl:
            findings.append(("FAIL", m["id"], f"chunk never read into the ledger ({m['first']} … {m['last']})"))
    for s in sources:
        if not any(e.get("source", e["id"][:3]) == s["id"] for e in ledger) and not any(k.startswith(s["id"] + "-") for k in excl):
            findings.append(("WARN", s["id"], f"source has no ledger entries: {s.get('title', s.get('path'))}"))
    gaps = sum(len(re.findall(r"\[SOURCE NEEDED", Path(d).read_text(encoding="utf-8"))) for d in docs)
    summary = {"ledger": len(ledger), "cited": len(ids & set(cited)), "excluded": len(ids & set(excl)),
               "chunks": len(manifest), "chunks_read": sum(1 for m in manifest if m["id"] in entries_by_chunk or m["id"] in excl),
               "source_needed_tags": gaps}
    return ledger, excl, cited, findings, summary


def report(work: Path, docs, out: Path):
    ledger, excl, cited, findings, summary = analyse(work, docs)
    sources = {s["id"]: s for s in load_jsonl(work / "sources.jsonl")}
    rows = []
    for e in sorted(ledger, key=lambda x: x["id"]):
        where = "; ".join(sorted(set(cited.get(e["id"], [])))) or ""
        rows.append((e["id"], sources.get(e.get("source", ""), {}).get("title", e.get("source", "")), e.get("cite") or e.get("locator", ""),
                     e.get("kind", ""), e.get("text", ""), where or f"Excluded: {excl.get(e['id'], '')}"))
    head = ("ID", "Source", "Location", "Kind", "Entry", "Used in / excluded because")
    if out.suffix in {".html", ".htm"}:
        body = "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in r) + "</tr>\n" for r in rows)
        out.write_text(f"<table class=\"ledger\"><thead><tr>{''.join(f'<th>{h}</th>' for h in head)}</tr></thead>"
                       f"<tbody>\n{body}</tbody></table>\n", encoding="utf-8")
    else:
        esc = lambda c: str(c).replace("|", "\\|").replace("\n", " ")
        lines = [f"# Source ledger\n\n{summary['ledger']} entries: {summary['cited']} used, {summary['excluded']} excluded. "
                 f"{summary['chunks_read']}/{summary['chunks']} chunks read.\n",
                 "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        lines += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]
        whole = [f"| {k} | {v} |" for k, v in excl.items() if CHUNK.match(k)]
        if whole:
            lines += ["\n## Whole chunks excluded\n", "| Chunk | Reason |", "|---|---|"] + whole
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "report"):
        p = sub.add_parser(name)
        p.add_argument("--work", required=True)
        p.add_argument("docs", nargs="+")
        if name == "check":
            p.add_argument("--json", action="store_true")
        else:
            p.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    work = Path(args.work)
    if args.cmd == "report":
        report(work, args.docs, Path(args.out))
        return 0
    _, _, _, findings, summary = analyse(work, args.docs)
    if args.json:
        print(json.dumps({"summary": summary, "findings": [dict(zip(("level", "id", "message"), f)) for f in findings]},
                         ensure_ascii=False, indent=2))
    else:
        fails = sum(1 for f in findings if f[0] == "FAIL")
        print(f"coverage: {summary['cited']} cited + {summary['excluded']} excluded of {summary['ledger']} ledger entries; "
              f"{summary['chunks_read']}/{summary['chunks']} chunks read; {summary['source_needed_tags']} [SOURCE NEEDED] tags; "
              f"{fails} FAIL")
        for level, i, msg in findings:
            print(f"  {level:<4} {i}: {msg}")
    return 1 if any(f[0] == "FAIL" for f in findings) else 0


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    sys.exit(main())
