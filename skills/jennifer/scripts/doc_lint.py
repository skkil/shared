#!/usr/bin/env python3
"""Lint product documents: specs, claims, and prose (Korean and English).

Usage:
  python doc_lint.py spec FILE      vague words, ownerless TBDs, missing PRD sections, requirements without AC
  python doc_lint.py claims FILE    numbers without an evidence label or source; vague attributions
  python doc_lint.py prose FILE     AI-writing tells, hedge stacking, em-dash and bold density, emoji
  python doc_lint.py all FILE       everything
Options: --json for machine-readable output. Exit code 1 if any error-level finding.

Findings are prompts for judgment, not verdicts: fix them or keep them deliberately.
"""
import argparse, json, re, sys

VAGUE_EN = [r"fast(er)?", r"quick(ly)?", r"easy", r"easily", r"simple", r"simply", r"user[- ]friendly",
            r"intuitive(ly)?", r"seamless(ly)?", r"appropriate(ly)?", r"as needed", r"etc\.?", r"and so on",
            r"robust", r"efficient(ly)?", r"flexible", r"scalable", r"as soon as possible", r"asap",
            r"if possible", r"where possible", r"reasonable", r"sufficient", r"adequate", r"optimi[sz]ed?",
            r"nice to have"]
VAGUE_AC_EXTRA = [r"better", r"improved?", r"enhanced?", r"properly", r"correctly", r"works?"]
VAGUE_KO = [r"빠르게", r"빠른", r"신속하게", r"쉽게", r"쉬운", r"간편하게", r"간단하게", r"편리하게", r"직관적(으로|인)?",
            r"적절히", r"적절한", r"원활하게", r"원활한", r"효율적(으로|인)?", r"필요\s?시", r"가능한 한", r"최대한",
            r"사용자 친화적(인)?", r"깔끔하게", r"자연스럽게", r"개선된", r"향상된"]
KO_DEUNG = r"(?:(?<=\s)|(?<=,))등(?:을|의|이|과|에|으로)?(?=[\s.,)\]]|$)"

TBD = re.compile(r"\b(TBD|TBC|TODO|FIXME|XXX)\b|미정|추후\s?(결정|논의|확정)|확인\s?필요", re.I)
OWNER = re.compile(r"(owner|담당|@\w+|\(\s*[A-Z][a-z]+\s*[,)])", re.I)
DATE = re.compile(r"(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}|\d{1,2}월\s?\d{1,2}일|\d{4}\.\s?\d{1,2}\.\s?\d{1,2})")

LABEL = re.compile(r"\[(measured|primary|simulated|secondary|anecdote|estimate|assumption)[^\]]*\]", re.I)
CITE = re.compile(r"(https?://|\(source:|source:|출처|\[\^?\d+\]|\[S\d+\])", re.I)
NUMERIC = re.compile(
    r"(\d[\d,]*(\.\d+)?\s?%|[$₩€£]\s?\d|\d[\d,]*(\.\d+)?\s?(원|만원|억|조|KRW|USD|million|billion|trillion|[MBK]\b)"
    r"|\b\d+(\.\d+)?x\b|\b\d{1,3}(,\d{3})+\b|\b\d+(\.\d+)?\s?(users|downloads|customers|명|건|개사))", re.I)
TARGETISH = re.compile(r"(target|goal|slo|threshold|budget|limit|max|min|≤|≥|<=|>=|<|>|shall|should|must|"
                       r"\bAC-|given|when|then|목표|기준|이하|이상|최대|최소|한도|example|e\.g\.|예:|예시)", re.I)
VAGUE_ATTR = re.compile(r"(studies show|research shows|experts (say|agree)|according to experts|it is widely (known|believed)|"
                        r"many (users|people) (say|feel|believe)|연구에 따르면|전문가들은|업계에서는)", re.I)

AI_WORDS = ["delve", "delves", "tapestry", "testament", "pivotal", "realm", "multifaceted", "seamless", "seamlessly",
            "robust", "leverage", "leverages", "leveraging", "utilize", "utilizes", "utilizing", "holistic", "synergy",
            "paradigm", "foster", "fosters", "fostering", "crucial", "vital", "boasts", "intricate", "myriad",
            "ever-evolving", "game-changer", "game-changing", "cutting-edge", "unlock", "unlocks", "empower",
            "empowers", "underscore", "underscores", "showcase", "showcases", "navigate", "navigating", "elevate",
            "streamline", "revolutionize", "groundbreaking", "transformative", "bustling", "vibrant", "nestled"]
AI_PHRASES = [r"it'?s not just\b", r"not only\b.*\bbut also", r"\bin conclusion\b", r"\bin summary\b", r"^\s*overall,",
              r"great question", r"^\s*certainly!", r"i hope this helps", r"plays? an? (crucial|vital|pivotal|key|important) role",
              r"stands? as an?\b", r"a testament to", r",\s*(highlighting|underscoring|emphasizing|showcasing|reflecting) (the|its|their)",
              r"in today'?s .{0,30}(landscape|world|era)", r"\bat the end of the day\b", r"rich (cultural )?heritage",
              r"중요한 역할을 (합니다|한다|함)", r"중요성을 (보여줍니다|보여준다|시사)", r"혁신적인", r"획기적인", r"결론적으로",
              r"다양한 측면에서", r"시사하는 바가 크다", r"한 단계 도약", r"새로운 지평"]
HEDGES = re.compile(r"\b(may|might|could|possibly|potentially|perhaps|somewhat|arguably|likely)\b[^.]{0,25}\b"
                    r"(may|might|could|possibly|potentially|perhaps|somewhat|suggest|indicate)\b", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")


def load_lines(path):
    text = open(path, encoding="utf-8").read()
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    out, in_code = [], False
    for i, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append((i, ""))
            continue
        out.append((i, "" if in_code else line))
    return out, text


def add(findings, check, level, line, msg, snippet=""):
    findings.append({"check": check, "level": level, "line": line, "message": msg, "snippet": snippet.strip()[:140]})


def lint_spec(lines, text, f):
    vague = re.compile(r"(?<![\w-])(" + "|".join(VAGUE_EN) + r")(?![\w-])", re.I)
    vague_ko = re.compile("(" + "|".join(VAGUE_KO) + ")")
    deung = re.compile(KO_DEUNG)
    for n, line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        for m in vague.finditer(line):
            add(f, "spec", "warn", n, f"vague word '{m.group(0)}': replace with a measurable criterion", line)
        for m in vague_ko.finditer(line):
            add(f, "spec", "warn", n, f"모호한 표현 '{m.group(0)}': 측정 가능한 기준으로 바꾸세요", line)
        if deung.search(line):
            add(f, "spec", "warn", n, "'등' leaves the list open: list every item or state the rule", line)
        if TBD.search(line) and not (OWNER.search(line) and DATE.search(line)):
            add(f, "spec", "error", n, "TBD/미정 without an owner and a due date: make it an open question (OQ-n, owner, date)", line)
    lower = text.lower()
    is_prd = bool(re.search(r"^#+.*(requirement|요구사항|prd|기획서)", text, re.I | re.M))
    if is_prd:
        checks = {
            "non-goals": r"non-goals?|out of scope|비목표|범위 제외|제외 범위|하지 않을 것",
            "success metrics": r"metric|success criteria|지표|성공 기준|kpi",
            "acceptance criteria": r"acceptance criteria|\bac-\d|given\b|인수 조건|수용 기준|완료 조건",
            "open questions": r"open questions?|미결|열린 질문|\boq-\d",
            "change history": r"change history|변경 이력|\|\s*version\s*\|",
        }
        for name, pat in checks.items():
            if not re.search(pat, lower, re.I):
                add(f, "spec", "warn", 0, f"PRD-like document has no {name} section")
    # requirement tables: rows with empty acceptance-criteria cell
    header_idx = None
    for idx, (n, line) in enumerate(lines):
        if line.strip().startswith("|"):
            cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
            if header_idx is None and any(("requirement" in c or "요구사항" in c) for c in cells):
                ac_cols = [i for i, c in enumerate(cells) if ("acceptance" in c or c in ("ac", "ac ids") or "인수" in c or "수용" in c)]
                header_idx = (ac_cols[0] if ac_cols else None)
                continue
            if header_idx is not None and not set(line.replace("|", "").strip()) <= set("-: "):
                raw = [c.strip() for c in line.strip().strip("|").split("|")]
                if header_idx < len(raw) and raw[0] and not raw[header_idx]:
                    add(f, "spec", "error", n, "requirement row has no acceptance criteria", line)
        else:
            header_idx = None


def lint_claims(lines, text, f):
    for n, line in lines:
        s = line.strip()
        if not s or s.startswith("#") or set(s) <= set("|-: "):
            continue
        if VAGUE_ATTR.search(line) and not CITE.search(line):
            add(f, "claims", "warn", n, "vague attribution without a named source", line)
        for m in re.finditer(r"\[secondary(:[^\]]*)?\]", line, re.I):
            if not DATE.search(m.group(0)) and not re.search(r"\b(19|20)\d{2}\b", m.group(0)):
                add(f, "claims", "warn", n, "[secondary] label without a date", line)
        if NUMERIC.search(line) and not LABEL.search(line) and not CITE.search(line) and not TARGETISH.search(line):
            add(f, "claims", "error", n, "number without an evidence label or source", line)


def lint_prose(lines, text, f):
    words_re = re.compile(r"(?<![\w-])(" + "|".join(re.escape(w) for w in AI_WORDS) + r")(?![\w-])", re.I)
    phrases = [re.compile(p, re.I) for p in AI_PHRASES]
    for n, line in lines:
        if not line.strip():
            continue
        for m in words_re.finditer(line):
            add(f, "prose", "warn", n, f"AI-typical word '{m.group(0)}': say the specific thing instead", line)
        for p in phrases:
            if p.search(line):
                add(f, "prose", "warn", n, f"AI-typical pattern /{p.pattern}/", line)
        if HEDGES.search(line):
            add(f, "prose", "warn", n, "stacked hedges: use one calibrated likelihood term", line)
        if EMOJI.search(line):
            add(f, "prose", "info", n, "emoji in a document: remove unless the audience expects it", line)
    body = " ".join(l for _, l in lines)
    nwords = max(1, len(re.findall(r"[\w가-힣]+", body)))
    dashes = body.count("—")
    bolds = len(re.findall(r"\*\*[^*]+\*\*", body))
    if dashes * 100 / nwords > 1.0:
        add(f, "prose", "warn", 0, f"em-dash density {dashes} in {nwords} words: prefer commas, colons, or two sentences")
    if bolds * 100 / nwords > 3.0:
        add(f, "prose", "warn", 0, f"bold density {bolds} in {nwords} words: bold only what a skimmer must see")
    add(f, "prose", "info", 0, f"{nwords} words, about {max(1, round(nwords / 230))} min to read; check against the length budget")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["spec", "claims", "prose", "all"])
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    lines, text = load_lines(a.file)
    f = []
    if a.mode in ("spec", "all"):
        lint_spec(lines, text, f)
    if a.mode in ("claims", "all"):
        lint_claims(lines, text, f)
    if a.mode in ("prose", "all"):
        lint_prose(lines, text, f)
    errors = sum(1 for x in f if x["level"] == "error")
    warns = sum(1 for x in f if x["level"] == "warn")
    if a.json:
        print(json.dumps({"errors": errors, "warnings": warns, "findings": f}, ensure_ascii=False, indent=2))
    else:
        for x in sorted(f, key=lambda x: (x["check"], x["line"])):
            loc = f"L{x['line']}" if x["line"] else "doc"
            print(f"[{x['level'].upper():5}] {x['check']:6} {loc:>5}  {x['message']}" + (f"\n                    > {x['snippet']}" if x["snippet"] else ""))
        print(f"\n{errors} error(s), {warns} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
