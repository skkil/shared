# Source ledger and exclusion log: formats

The ledger lives in `.vanessa/work/<task>/`. `chunk_source.py` writes `sources.jsonl` and `chunks/`; Vanessa writes `ledger.jsonl` and `exclusions.md`; `coverage_check.py` checks them and renders a readable report for delivery.

## sources.jsonl (one JSON object per line)

```json
{"id": "S01", "title": "Payments API reference", "author": "Acme Inc.", "date": "2026-09-12", "kind": "html",
 "url": "https://docs.example.com/payments", "path": "", "tier": "primary",
 "credibility": "SIFT: vendor's own docs for its API; current version; authoritative for behavior, not for performance claims"}
```

## ledger.jsonl (one JSON object per line)

```json
{"id": "S01-C002-04", "source": "S01", "chunk": "S01-C002", "locator": "heading=\"Refunds\"", "cite": "Refunds section",
 "kind": "fact", "text": "Refunds can be issued up to 180 days after capture.", "section": "Refund window", "status": "ok"}
{"id": "S02-C001-03", "source": "S02", "chunk": "S02-C001", "locator": "time=00:41:12-00:43:05", "cite": "41:12, Minji",
 "kind": "decision", "text": "Team decided to cap retries at 3 (Minji, agreed by Joon).", "section": "Retry policy", "status": "conflict",
 "conflicts_with": ["S01-C004-02"]}
```

Kinds: fact, definition, claim, number, example, decision, procedure, question, quote.
Status: ok, conflict, superseded, inferred (mark anything you inferred rather than read).

## exclusions.md

```markdown
| ID | Reason |
|---|---|
| S01-C001 | front matter: title page, copyright, table of contents |
| S01-C003-11 | duplicate of S01-C002-04 |
| S02-C005-02 | off-topic for this audience: office move logistics |
| S03-C002-07 | superseded by S04-C001-02 (2026 runbook replaces the 2024 wiki page) |
```
A chunk ID excludes the whole chunk. Every reason says why; "not needed" fails the check.

## Citing in the draft

Put the ID next to the claim: `Refunds can be issued up to 180 days after capture [S01-C002-04].` In HTML, `data-ledger="S01-C002-04"` on the element or the visible citation link works too. Gaps: `[SOURCE NEEDED: refund limits for partial captures]`.
