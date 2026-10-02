#!/usr/bin/env python3
"""Check issue drafts against the definition of ready, and render them for creation.

Input: a JSON file, either a list of issues or {"repo": "org/name", "issues": [...]}.
Issue fields: id, title, type (bug|feature|improvement|chore|spike|docs), priority (P0-P3), severity (S1-S4, bugs),
size (S|M|L), labels [..], milestone, context, problem, steps [..], expected, actual, environment, frequency,
acceptance [..], out_of_scope [..], tech_notes, sources [..], links [..], depends_on [ids], needs [..],
timebox and expected_output (spikes).

Usage:
  python issues.py check issues.json                 readiness report; exit 1 if any issue is not ready
  python issues.py render issues.json --out issues/ [--repo org/name] [--include-unready]
      writes <id>.md bodies, summary.md, and create_issues.sh (gh commands). Run the script only after approval.
"""
import argparse, json, os, re, shlex, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doc_lint import VAGUE_EN, VAGUE_KO, VAGUE_AC_EXTRA  # noqa: E402

VAGUE = re.compile(r"(?<![\w-])(" + "|".join(VAGUE_EN + VAGUE_KO) + r")(?![\w-])", re.I)
VAGUE_AC = re.compile(r"(?<![\w-])(" + "|".join(VAGUE_EN + VAGUE_KO + VAGUE_AC_EXTRA) + r")(?![\w-])", re.I)
WEAK_TITLE = re.compile(r"^(fix|bug|issue|problem|update|improve|change|misc|todo|버그|수정|개선|문제)\b[\s:]*\S{0,12}$", re.I)
TYPES = {"bug", "feature", "improvement", "chore", "spike", "docs"}


def load(path):
    data = json.load(open(path, encoding="utf-8"))
    if isinstance(data, dict):
        return data.get("repo"), data.get("issues", [])
    return None, data


def check_issue(i, ids):
    p, w = [], []
    t = i.get("type", "")
    title = i.get("title", "").strip()
    if t not in TYPES:
        p.append(f"type must be one of {sorted(TYPES)}")
    if not title:
        p.append("missing title")
    else:
        if len(title) < 12 or WEAK_TITLE.match(title):
            p.append("title too vague: state the outcome or the failure")
        if len(title) > 90:
            w.append("title longer than 90 characters")
        if VAGUE.search(title):
            w.append(f"vague word in title: '{VAGUE.search(title).group(0)}'")
    if not i.get("priority"):
        p.append("missing priority (P0-P3) with a reason")
    if not (i.get("context") or i.get("problem")):
        p.append("missing context/problem: who is affected, how often, evidence")
    if not i.get("sources"):
        w.append("no source feedback IDs: the loop can't be closed")
    if t == "bug":
        for k in ("steps", "expected", "actual", "environment"):
            if not i.get(k):
                p.append(f"bug missing '{k}'")
        if not i.get("severity"):
            w.append("bug without severity (S1-S4)")
    if t == "spike":
        if not i.get("timebox"):
            p.append("spike missing timebox")
        if not i.get("expected_output"):
            p.append("spike missing expected output (a decision or a ready issue)")
    elif t in ("feature", "improvement", "bug", "chore"):
        ac = i.get("acceptance") or []
        if not ac:
            p.append("no acceptance criteria")
        for c in ac:
            m = VAGUE_AC.search(c)
            if m:
                p.append(f"untestable acceptance criterion (vague '{m.group(0)}'): {c[:60]}")
    if t in ("feature", "improvement") and not i.get("out_of_scope"):
        w.append("no out-of-scope list")
    if str(i.get("size", "")).upper() == "L":
        w.append("size L: consider splitting into vertical slices")
    for need in i.get("needs", []) or []:
        p.append(f"needs {need}: not ready until resolved")
    for d in i.get("depends_on", []) or []:
        if d not in ids:
            w.append(f"depends on unknown id '{d}'")
    return p, w


def body(i):
    L = []
    meta = [f"**Type:** {i.get('type','')}", f"**Priority:** {i.get('priority','')}"]
    if i.get("severity"):
        meta.append(f"**Severity:** {i['severity']}")
    if i.get("size"):
        meta.append(f"**Size guess:** {i['size']}")
    L.append(" · ".join(meta) + "\n")
    if i.get("context"):
        L.append("### Context\n" + i["context"] + "\n")
    if i.get("sources"):
        L.append("Sources: " + ", ".join(i["sources"]) + "\n")
    if i.get("problem"):
        L.append("### Problem\n" + i["problem"] + "\n")
    if i.get("type") == "bug":
        L.append("### Steps to reproduce\n" + "\n".join(f"{n}. {s}" for n, s in enumerate(i.get("steps", []), 1)) + "\n")
        L.append(f"**Expected:** {i.get('expected','')}\n\n**Actual:** {i.get('actual','')}\n\n**Environment:** {i.get('environment','')}\n")
        if i.get("frequency"):
            L.append(f"**Frequency:** {i['frequency']}\n")
    elif i.get("expected"):
        L.append("### Expected behavior\n" + i["expected"] + "\n")
    if i.get("type") == "spike":
        L.append(f"### Spike\n**Timebox:** {i.get('timebox','')}\n\n**Expected output:** {i.get('expected_output','')}\n")
    if i.get("acceptance"):
        L.append("### Acceptance criteria\n" + "\n".join(f"- [ ] {c}" for c in i["acceptance"]) + "\n")
    if i.get("out_of_scope"):
        L.append("### Out of scope\n" + "\n".join(f"- {c}" for c in i["out_of_scope"]) + "\n")
    if i.get("tech_notes"):
        L.append("### Technical pointers (not a design)\n" + i["tech_notes"] + "\n")
    if i.get("depends_on"):
        L.append("Depends on: " + ", ".join(i["depends_on"]) + "\n")
    if i.get("links"):
        L.append("### Links\n" + "\n".join(f"- {x}" for x in i["links"]) + "\n")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["check", "render"])
    ap.add_argument("file")
    ap.add_argument("--out", default="issues")
    ap.add_argument("--repo")
    ap.add_argument("--include-unready", action="store_true")
    a = ap.parse_args()
    repo, issues = load(a.file)
    repo = a.repo or repo
    ids = {i.get("id") for i in issues}
    titles = {}
    results = []
    for i in issues:
        p, w = check_issue(i, ids)
        key = i.get("title", "").strip().lower()
        if key in titles:
            w.append(f"duplicate title of {titles[key]}")
        titles[key] = i.get("id")
        results.append((i, p, w))
    ready = [r for r in results if not r[1]]
    if a.cmd == "check":
        print("| ID | Title | Type | Priority | Ready | Problems / warnings |\n|---|---|---|---|---|---|")
        for i, p, w in results:
            notes = "; ".join(p + [f"(warn) {x}" for x in w]) or "-"
            print(f"| {i.get('id','?')} | {i.get('title','')[:60]} | {i.get('type','')} | {i.get('priority','')} | {'yes' if not p else 'NO'} | {notes} |")
        print(f"\n{len(ready)} of {len(results)} issues ready.")
        sys.exit(0 if len(ready) == len(results) else 1)
    os.makedirs(a.out, exist_ok=True)
    chosen = results if a.include_unready else ready
    lines = ["#!/usr/bin/env bash", "# Generated by Jennifer. RUN ONLY AFTER THE HUMAN HAS APPROVED THIS BATCH.", "set -euo pipefail", ""]
    summary = ["| ID | Title | Type | Priority | Size | Sources |", "|---|---|---|---|---|---|"]
    for i, p, w in chosen:
        fn = os.path.join(a.out, f"{i['id']}.md")
        open(fn, "w", encoding="utf-8").write(body(i))
        labels = list(i.get("labels", []))
        for k, pre in (("type", "type:"), ("priority", "priority:"), ("severity", "severity:"), ("size", "size:")):
            if i.get(k) and not any(l.startswith(pre) for l in labels):
                labels.append(pre + str(i[k]))
        cmd = ["gh", "issue", "create", "--title", i["title"], "--body-file", fn]
        if repo:
            cmd += ["--repo", repo]
        for l in labels:
            cmd += ["--label", l]
        if i.get("milestone"):
            cmd += ["--milestone", i["milestone"]]
        lines.append(" ".join(shlex.quote(c) for c in cmd))
        summary.append(f"| {i['id']} | {i['title']} | {i.get('type','')} | {i.get('priority','')} | {i.get('size','')} | {len(i.get('sources', []))} |")
    skipped = [r for r in results if r[1]] if not a.include_unready else []
    if skipped:
        summary.append("\nNot ready (not rendered): " + ", ".join(f"{i.get('id')} ({'; '.join(p)})" for i, p, w in skipped))
    open(os.path.join(a.out, "create_issues.sh"), "w").write("\n".join(lines) + "\n")
    open(os.path.join(a.out, "summary.md"), "w", encoding="utf-8").write("\n".join(summary) + "\n")
    print(f"Rendered {len(chosen)} issue(s) to {a.out}/ ; {len(skipped)} not ready. Labels must exist in the repo (gh label create).")


if __name__ == "__main__":
    main()
