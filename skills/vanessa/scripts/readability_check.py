#!/usr/bin/env python3
"""readability_check: Vanessa's "understood the first time" gate for English and Korean text.

The score is a signal, not the goal. A passing report with a confusing structure still fails
the standard; read the draft as its reader would after the script is quiet.

Usage
  python scripts/readability_check.py check FILE [--lang auto|en|ko] [--audience A] [--profile P]
                                        [--voice .vanessa/voice.md] [--glossary .vanessa/glossary.md] [--json]
  python scripts/readability_check.py check - < draft.md          read stdin
  python scripts/readability_check.py limits FILE [--limits limits.json] [--json]
  python scripts/readability_check.py stats FILE... [--lang ko]   sentence-length distribution, for calibration

Audiences: end-user | marketing | internal | developer      (sets the English grade target)
Profiles:  doc | ui | marketing | slides                     (turns profile-specific checks on or off)

check reads Markdown, HTML or plain text. It skips code, block quotes, source-excerpt dropdowns
(<details>), HTML comments and regions between <!-- vanessa-ignore --> and <!-- /vanessa-ignore -->.
Add <!-- vanessa-allow: RULE_ID --> on a line to accept one finding there on purpose.

limits checks every string against a character limit. FILE is JSON ({"id": "text"}, nested i18n
JSON, or a list of {"id","text","limit","unit"}), an Apple .strings file or an Android strings.xml.
Store fields with known ids (ios.name, ios.subtitle, ios.promo, ios.keywords, ios.description,
play.title, play.short, play.full) need no limit file.

Rule tables live in references/banned-en.md and references/banned-ko.md, so writers and the script
read the same list. Targets come from the vanessa-config block in the voice guide when one exists.

Exit code 1 when any FAIL finding remains.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import signal
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
REFS = HERE.parent / "references"

DEFAULTS = {
    "en": {
        "sentence_words_warn": 25,
        "paragraph_sentences_warn": 4,
        "grade_targets": {"end-user": 8, "marketing": 8, "internal": 10, "developer": None},
        "em_dash_per_100_words": 0.7,
        "passive_ratio_warn": 0.25,
        "negative_contractions": "allow",
        "triads_per_300_words": 1.0,
    },
    "ko": {
        "sentence_eojeol_warn": 17,
        "sentence_chars_warn": 90,
        "paragraph_sentences_warn": 4,
        "commas_per_sentence_warn": 0.8,
        "register_consistency_min": 0.85,
        "jeok_per_sentence_warn": 3,
    },
    "acronym_allowlist": ["OK", "I", "A", "AM", "PM", "TV", "PC", "KB", "MB", "GB", "TB"],
    "extra_banned": [],
}

STORE_LIMITS = {
    "ios.name": (30, "chars"), "ios.subtitle": (30, "chars"), "ios.promo": (170, "chars"),
    "ios.keywords": (100, "chars+bytes"), "ios.description": (4000, "chars"),
    "play.title": (30, "chars"), "play.short": (80, "chars"), "play.full": (4000, "chars"),
}

HANGUL = re.compile(r"[\uac00-\ud7a3]")
LATIN = re.compile(r"[A-Za-z]")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U0001F000-\U0001F2FF\u2600-\u26FF]")
ACRONYM = re.compile(r"(?<![A-Za-z0-9_/.\-])([A-Z]{2}[A-Z0-9]{0,6})(s?)(?![A-Za-z0-9_/\-]|\.[A-Za-z0-9])")
EN_ABBR = re.compile(r"\b(e\.g|i\.e|etc|vs|Dr|Mr|Ms|Mrs|St|No|Fig|Eq|approx|cf|al)\.$", re.I)
PASSIVE = re.compile(
    r"\b(?:is|are|was|were|be|been|being|gets|got)\s+(?:\w+ly\s+)?"
    r"(\w+(?:ed|en)|built|done|made|kept|left|lost|paid|sent|set|shown|sold|told|run|put|read|held|"
    r"found|given|taken|written|known|seen|chosen|driven|thrown)\b", re.I)
NOMINAL = re.compile(r"\b\w{4,}(?:tion|sion|ment)s?\b", re.I)
TRIAD = re.compile(r"(?<!, )\b([\w-]+), ([\w-]+),? and ([\w-]+)\b")
WEAK_OPENER = re.compile(r"^(there (?:is|are|was|were)|it is \w+ (?:that|to))\b", re.I)
SELF_INTRO = re.compile(
    r"^(this (?:document|guide|page|section|article|report|deck) (?:describes|explains|covers|provides|outlines|will)"
    r"|in this (?:guide|document|article|section|report),|이 (?:문서|가이드|글)(?:에서는|은|는) )", re.I)
NEG_CONTRACTION = re.compile(r"\b\w+n['’]t\b", re.I)
KO_ENDINGS = [
    ("합니다체", re.compile(r"(?:니다|니까)[.!?]?$")),
    ("해요체", re.compile(r"요[.!?]?$")),
    ("해라체", re.compile(r"[다라][.!?]?$")),
    ("개조식", re.compile(r"(?:[음함임됨짐봄둠움]|필요|예정|완료|가능|불가)[.]?$")),
]
JEOK = re.compile(r"[\uac00-\ud7a3]+적(?:인|으로|이다|이고|이며)?(?=\s|$|[.,])")


def load_rule_table(path: Path):
    """Parse | `regex` | LEVEL | why | instead | [profiles] | rows; ids are file#row."""
    rules = []
    if not path.exists():
        return rules
    row = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or set(line.strip()) <= set("|-: "):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if len(cells) < 4:
            continue
        m = re.fullmatch(r"`(.+)`", cells[0])
        if not m or cells[1].upper() not in {"FAIL", "WARN", "INFO"}:
            continue
        row += 1
        profiles = {x.strip() for x in cells[4].split(",")} if len(cells) > 4 and cells[4] else {"all"}
        try:
            rx = re.compile(m.group(1).replace("\\|", "|"), re.I | re.M)
        except re.error as exc:
            sys.stderr.write(f"bad pattern in {path.name}: {cells[0]} ({exc})\n")
            continue
        rules.append({"rx": rx, "level": cells[1].upper(), "why": cells[2], "instead": cells[3],
                      "id": f"{path.stem}#{row}", "profiles": profiles})
    return rules


def load_voice_config(path):
    cfg = json.loads(json.dumps(DEFAULTS))
    if not path or not Path(path).exists():
        return cfg
    m = re.search(r"```vanessa-config\s*\n(.*?)```", Path(path).read_text(encoding="utf-8"), re.S)
    if not m:
        return cfg
    try:
        user = json.loads(m.group(1))
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"vanessa-config block in {path} is not valid JSON: {exc}\n")
        return cfg
    for key, val in user.items():
        if isinstance(val, dict) and isinstance(cfg.get(key), dict):
            for k2, v2 in val.items():
                if isinstance(v2, dict) and isinstance(cfg[key].get(k2), dict):
                    cfg[key][k2].update(v2)
                else:
                    cfg[key][k2] = v2
        else:
            cfg[key] = val
    return cfg


def load_glossary(path):
    """Return (avoid terms, known acronyms) from a Markdown glossary table with an Avoid column."""
    avoid, known = [], set()
    if not path or not Path(path).exists():
        return avoid, known
    header = None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            if line.strip():
                header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        low = [c.lower() for c in cells]
        if header is None and any("avoid" in c for c in low):
            header = low
            continue
        if header is None:
            continue
        row = dict(zip(header, cells))
        pref = next((v for k, v in row.items() if k.startswith("english")), cells[0])
        pref_ko = next((v for k, v in row.items() if k.startswith("korean")), "")
        for col, val in row.items():
            if "avoid" in col and val and val not in {"-", "—"}:
                for term in re.split(r"[,;/]", val):
                    term = term.strip().strip("`")
                    if term:
                        avoid.append((term, pref, pref_ko))
        for val in (pref, pref_ko):
            m = re.match(r"([A-Z][A-Z0-9]{1,7})\b", val or "")
            if m:
                known.add(m.group(1))
    return avoid, known


def strip_markup(raw: str, is_html: bool):
    """Return text lines with code, quotes, excerpts and ignored regions blanked, line numbers preserved."""
    keep_lines = lambda m: "\n" * m.group(0).count("\n")
    text = re.sub(r"<!--\s*vanessa-ignore\s*-->.*?<!--\s*/vanessa-ignore\s*-->", keep_lines, raw, flags=re.S)
    text = re.sub(r"<details\b.*?</details>", keep_lines, text, flags=re.S | re.I)
    if is_html:
        text = re.sub(r"<(script|style|pre|code|blockquote|svg|math|aside)\b.*?</\1>", keep_lines, text, flags=re.S | re.I)
        text = re.sub(r"<!--(?!\s*vanessa-allow).*?-->", keep_lines, text, flags=re.S)
        text = re.sub(r"<h([1-6])[^>]*>", lambda m: "#" * int(m.group(1)) + " ", text, flags=re.I)
        text = re.sub(r"<li[^>]*>", "- ", text, flags=re.I)
        text = re.sub(r"</(p|div|h[1-6]|li|tr|section|article|header|footer|figcaption)>", "\n", text, flags=re.I)
        text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
        text = re.sub(r"</?(strong|b)>", "**", text, flags=re.I)
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)
    out, fence = [], False
    for line in text.split("\n"):
        if re.match(r"\s*(```|~~~)", line):
            fence = not fence
            out.append("")
            continue
        if fence or line.lstrip().startswith(">"):
            out.append("")
            continue
        line = re.sub(r"<!--(?!\s*vanessa-allow).*?-->", "", line)
        line = re.sub(r"`[^`]*`", "CODE", line)
        line = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"https?://\S+", "URL", line)
        out.append(line)
    return out


def blocks_from_lines(lines):
    blocks, buf, start = [], [], 0

    def flush():
        nonlocal buf
        if buf:
            blocks.append({"kind": "para", "line": start, "text": " ".join(s.strip() for s in buf)})
            buf = []

    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or (s.startswith("---") and len(set(s)) == 1):
            flush()
            continue
        if re.match(r"#{1,6}\s", s):
            flush()
            blocks.append({"kind": "heading", "line": i, "level": len(s) - len(s.lstrip("#")),
                           "text": s.lstrip("#").strip()})
            continue
        if s.startswith("|"):
            flush()
            if not set(s) <= set("|-: "):
                blocks.append({"kind": "table", "line": i, "text": s})
            continue
        if re.match(r"([-*+]|\d+[.)]|[□○◦·•▪])\s", s):
            flush()
            blocks.append({"kind": "list", "line": i, "text": re.sub(r"^([-*+]|\d+[.)]|[□○◦·•▪])\s+", "", s)})
            continue
        if not buf:
            start = i
        buf.append(s)
    flush()
    return blocks


def detect_lang(text):
    h, lat = len(HANGUL.findall(text)), len(LATIN.findall(text))
    return "ko" if h and h >= 0.25 * (h + lat) else "en"


def split_sentences(text, lang):
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"([.!?…])((?:\*\*|[”’\"')\]])+)\s", r"\1 \2 ", text)
    if not text:
        return []
    parts, cur = [], ""
    for tok in re.split(r"(?<=[.!?…])\s+", text):
        cur = f"{cur} {tok}".strip() if cur else tok
        if lang == "en" and (EN_ABBR.search(cur) or re.search(r"\b[A-Z]\.$", cur)):
            continue
        parts.append(cur)
        cur = ""
    if cur:
        parts.append(cur)
    return [p for p in parts if re.search(r"\w", p)]


def words(sentence):
    return re.findall(r"[A-Za-z0-9\uac00-\ud7a3][\w'’\-\uac00-\ud7a3]*", sentence)


def syllables(word):
    w = word.lower().strip("'’")
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))


class Report:
    def __init__(self, raw_lines):
        self.findings, self.raw_lines, self.stats = [], raw_lines, {}

    def allowed(self, line_no, rule_id):
        if 0 < line_no <= len(self.raw_lines):
            m = re.search(r"vanessa-allow:\s*(.*?)\s*-->", self.raw_lines[line_no - 1])
            if m:
                ids = [x for x in re.split(r"[,\s]+", m.group(1)) if x]
                return any(x == "all" or rule_id.startswith(x) for x in ids)
        return False

    def add(self, level, rule, line, msg, snippet="", instead=""):
        if not self.allowed(line, rule):
            self.findings.append({"level": level, "rule": rule, "line": line, "message": msg,
                                  "snippet": snippet.strip()[:120], "instead": instead})

    def exit_code(self):
        return 1 if any(f["level"] == "FAIL" for f in self.findings) else 0


def check_banned(rep, blocks, rules, extra, profile):
    rules = [r for r in rules if "all" in r["profiles"] or profile in r["profiles"]]
    all_rules = rules + [{"rx": re.compile(r["pattern"], re.I), "level": r.get("level", "WARN"),
                          "why": r.get("why", "listed in the voice guide"), "instead": r.get("instead", ""),
                          "id": "voice#" + r["pattern"][:20]} for r in extra]
    for b in blocks:
        for r in all_rules:
            for m in r["rx"].finditer(b["text"]):
                rep.add(r["level"], r["id"], b["line"], r["why"], m.group(0), r["instead"])


MARKER = re.compile(r"\[(?:SOURCE NEEDED|CONFLICT|PENDING [A-Z]+)[^\]]*\]")


def check_acronyms(rep, blocks, allow, known):
    blocks = [dict(b, text=MARKER.sub("", b["text"])) for b in blocks]
    defined, first = set(), {}
    full = " ".join(b["text"] for b in blocks)
    for b in blocks:
        for m in ACRONYM.finditer(b["text"]):
            ac = m.group(1)
            if ac in allow or ac in known or ac in {"CODE", "URL"}:
                continue
            tail = b["text"][m.end(): m.end() + 2]
            head = b["text"][max(0, m.start() - 1): m.start()]
            if tail.startswith(("(", " (")) or head == "(":
                defined.add(ac)
            first.setdefault(ac, (b["line"], ac in defined))
    for ac, (line, at_first) in first.items():
        if ac in defined and not at_first:
            rep.add("WARN", "acronym-late", line, f"{ac} is used before it is defined", ac,
                    "define it at first use: Full Name (ACR), or ACR(풀이) in Korean")
        elif ac not in defined and not re.search(rf"\(\s*{ac}\s*\)", full):
            rep.add("WARN", "acronym-undefined", line, f"{ac} is never defined", ac,
                    "define it at first use, or mark it known in the glossary")


def check_glossary(rep, blocks, avoid):
    for term, pref, pref_ko in avoid:
        rx = re.compile(rf"(?<![A-Za-z0-9\uac00-\ud7a3]){re.escape(term)}(?![A-Za-z0-9])", re.I)
        for b in blocks:
            for m in rx.finditer(b["text"]):
                rep.add("WARN", "glossary-avoid", b["line"], f"'{term}' is on the glossary avoid list",
                        m.group(0), f"use '{pref}'" + (f" / '{pref_ko}'" if pref_ko else ""))


def check_headings(rep, blocks, profile):
    runs = {}
    for b in blocks:
        if b["kind"] != "heading":
            continue
        first = (words(b["text"]) or [""])[0].lower()
        word, count = runs.get(b["level"], ("", 0))
        count = count + 1 if first and first == word else 1
        runs[b["level"]] = (first, count)
        for deeper in [k for k in runs if k > b["level"]]:
            runs.pop(deeper)
        if count == 3:
            rep.add("WARN", "heading-same-opener", b["line"],
                    "three sibling headings in a row start with the same word; scanners skip repeated openers",
                    b["text"], "front-load the word that differs")
        if profile == "doc" and b["level"] >= 2 and len(words(b["text"])) <= 2 and not re.search(r"\d", b["text"]):
            rep.add("INFO", "heading-label", b["line"], "heading names a topic; does it state the point?",
                    b["text"], "e.g. 'Deploys fail without this key' rather than 'Configuration'")


def check_common(rep, blocks, cfg_lang, lang, profile):
    paras = [b for b in blocks if b["kind"] == "para"]
    for i, b in enumerate(paras):
        sents = split_sentences(b["text"], lang)
        if len(sents) > cfg_lang["paragraph_sentences_warn"]:
            rep.add("WARN", "paragraph-long", b["line"],
                    f"paragraph has {len(sents)} sentences (cap {cfg_lang['paragraph_sentences_warn']})",
                    b["text"][:80], "one idea per paragraph; split or cut")
        if i == 0 and sents and SELF_INTRO.search(sents[0]):
            rep.add("WARN", "intro-restates", b["line"], "opening sentence describes the document instead of making the point",
                    sents[0], "open with the answer, decision, or result")
    bold = sum(len(re.findall(r"\*\*[^*]+\*\*", b["text"])) for b in paras)
    if paras and bold / len(paras) > 1.0:
        rep.add("WARN", "bold-density", 0, f"{bold} bold spans in {len(paras)} paragraphs",
                "", "bold only what a scanner must not miss")
    for b in blocks:
        if profile in {"doc", "slides"} and EMOJI.search(b["text"]):
            rep.add("WARN", "emoji", b["line"], "emoji in a document", b["text"][:60], "remove unless the voice guide allows it")
        for m in re.finditer(r"\[SOURCE NEEDED[^\]]*\]", b["text"]):
            rep.add("INFO", "source-needed", b["line"], "open source gap", m.group(0))
        if re.search(r"\b(TODO|TBD|FIXME)\b|미정|추후 결정", b["text"]):
            rep.add("WARN", "placeholder", b["line"], "placeholder left in the draft", b["text"][:60])


def check_en(rep, blocks, cfg, audience, profile):
    c = cfg["en"]
    prose = [b for b in blocks if b["kind"] in {"para", "list"}]
    total_words = total_sents = total_syl = passive = dashes_total = 0
    openers = []
    for b in prose:
        for s in split_sentences(b["text"], "en"):
            w = words(s)
            total_words += len(w)
            total_sents += 1
            total_syl += sum(syllables(x) for x in w)
            if len(w) > c["sentence_words_warn"] and b["kind"] == "para":
                rep.add("WARN", "sentence-long", b["line"], f"{len(w)} words (cap {c['sentence_words_warn']})", s,
                        "split it, or move a clause into a list")
            if PASSIVE.search(s):
                passive += 1
            if WEAK_OPENER.search(s):
                rep.add("WARN", "weak-opener", b["line"], "opens with 'there is/are' or 'it is ... that'", s,
                        "start with the subject that acts")
            d = s.count("—") + s.count(" -- ")
            dashes_total += d
            if d >= 2:
                rep.add("WARN", "em-dash-sentence", b["line"], "two dashes in one sentence", s,
                        "use parentheses, a colon, or two sentences")
            if c.get("negative_contractions") == "avoid" and NEG_CONTRACTION.search(s):
                rep.add("WARN", "negative-contraction", b["line"], "negative contraction (voice guide says avoid)", s,
                        "write 'do not', 'cannot'")
            openers.append(((w or [""])[0].lower(), b["line"], s))
    for i in range(2, len(openers)):
        a, b2, c3 = openers[i - 2], openers[i - 1], openers[i]
        if a[0] and a[0] == b2[0] == c3[0] and a[0] not in {"the", "a", "you", "code"}:
            rep.add("WARN", "repeated-opener", c3[1], f"three sentences in a row start with '{a[0]}'", c3[2])
    if not total_sents:
        return
    grade = 0.39 * total_words / total_sents + 11.8 * total_syl / max(1, total_words) - 15.59
    rep.stats.update({"words": total_words, "sentences": total_sents,
                      "avg_sentence_words": round(total_words / total_sents, 1),
                      "fk_grade": round(grade, 1), "passive_ratio": round(passive / total_sents, 2)})
    target = c["grade_targets"].get(audience)
    if target is not None and grade > target + 0.5:
        rep.add("WARN", "grade", 0, f"Flesch-Kincaid grade {grade:.1f} is above the {audience} target {target}",
                "", "check structure first, then shorter sentences and plainer words")
    if passive / total_sents > c["passive_ratio_warn"]:
        rep.add("WARN", "passive-ratio", 0, f"{passive}/{total_sents} sentences look passive",
                "", "name the actor unless the outcome matters more than who acted")
    per100 = 100 * dashes_total / max(1, total_words)
    if per100 > c["em_dash_per_100_words"]:
        rep.add("WARN", "em-dash-density", 0, f"{dashes_total} dashes in {total_words} words ({per100:.2f} per 100)",
                "", "a dash now and then is fine; one in every paragraph reads as generated")
    joined = " ".join(b["text"] for b in prose)
    triads = len(TRIAD.findall(joined))
    if triads >= 2 and triads * 300 / max(1, total_words) > c["triads_per_300_words"]:
        rep.add("WARN", "triads", 0, f"{triads} 'X, Y, and Z' groups", "",
                "list the number of items that exist; two often beats three")
    nominal = len(NOMINAL.findall(joined))
    rep.stats["nominalizations_per_100"] = round(100 * nominal / max(1, total_words), 1)
    if profile != "ui" and nominal * 100 / max(1, total_words) > 6:
        rep.add("INFO", "nominalizations", 0, f"{nominal} -tion/-sion/-ment words", "",
                "turn hidden verbs back into verbs where it reads better")


def ko_register(sentence):
    t = re.sub(r"[\"'”’)\]]+$", "", sentence.strip())
    if re.search(r"(?:세요|십시오)[.!?]?$", t):
        return None
    for name, rx in KO_ENDINGS:
        if rx.search(t):
            return name
    return None


def check_ko(rep, blocks, cfg, profile):
    c = cfg["ko"]
    prose = [b for b in blocks if b["kind"] in {"para", "list"}]
    lens, chars, registers, commas, n = [], [], {}, 0, 0
    for b in prose:
        for s in split_sentences(b["text"], "ko"):
            n += 1
            ej = len(s.split())
            lens.append(ej)
            chars.append(len(s))
            commas += s.count(",")
            if b["kind"] == "para":
                if ej > c["sentence_eojeol_warn"]:
                    rep.add("WARN", "ko-sentence-long", b["line"], f"{ej}어절 (기준 {c['sentence_eojeol_warn']})", s,
                            "한 문장에 한 가지 내용만 담고, 나누거나 목록으로 바꾸세요")
                elif len(s) > c["sentence_chars_warn"]:
                    rep.add("INFO", "ko-sentence-chars", b["line"], f"{len(s)}자", s)
                if s.count(",") >= 3:
                    rep.add("WARN", "ko-commas", b["line"], f"쉼표 {s.count(',')}개", s,
                            "문장을 나누거나 연결 어미로 이으세요")
                reg = ko_register(s)
                if reg:
                    registers.setdefault(reg, []).append(b["line"])
            if len(JEOK.findall(s)) >= c["jeok_per_sentence_warn"]:
                rep.add("WARN", "ko-jeok-chain", b["line"], "'~적' 표현이 한 문장에 몰려 있음", s, "동사로 풀어 쓰세요")
            if profile == "ui" and "십시오" in s:
                rep.add("WARN", "ko-ui-sipsio", b["line"], "UI 문구에 '~십시오'", s, "'~세요' (약관·법률 문서는 예외)")
    if not n:
        return
    srt = sorted(lens)
    rep.stats.update({"sentences": n, "avg_eojeol": round(sum(lens) / n, 1), "p90_eojeol": srt[int(0.9 * (n - 1))],
                      "avg_chars": round(sum(chars) / n, 1), "commas_per_sentence": round(commas / n, 2),
                      "registers": {k: len(v) for k, v in registers.items()}})
    if commas / n > c["commas_per_sentence_warn"]:
        rep.add("WARN", "ko-comma-density", 0, f"문장당 쉼표 {commas / n:.2f}개", "",
                "생성된 한국어는 사람이 쓴 글보다 쉼표가 많습니다(KatFishNet, ACL 2025)")
    total = sum(len(v) for v in registers.values())
    if total >= 4:
        top = max(registers, key=lambda k: len(registers[k]))
        share = len(registers[top]) / total
        if share < c["register_consistency_min"]:
            others = {k: v[:3] for k, v in registers.items() if k != top}
            rep.add("WARN", "ko-register-mix", 0, f"문체 혼용: {top} {share:.0%}, 나머지 줄 {others}", "",
                    "문서 전체를 한 문체로 맞추세요")


def run_check(args):
    raw = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    is_html = args.file.endswith((".html", ".htm")) or bool(re.search(r"<(html|body|p|div|h1)\b", raw[:2000], re.I))
    lines = strip_markup(raw, is_html)
    blocks = blocks_from_lines(lines)
    lang = detect_lang(" ".join(b["text"] for b in blocks)) if args.lang == "auto" else args.lang
    cfg = load_voice_config(args.voice)
    avoid, known = load_glossary(args.glossary)
    rep = Report(raw.split("\n"))
    rules = load_rule_table(REFS / f"banned-{lang}.md")
    check_banned(rep, [b for b in blocks if b["kind"] != "table"], rules, cfg.get("extra_banned", []), args.profile)
    check_acronyms(rep, blocks, set(cfg["acronym_allowlist"]), known)
    check_glossary(rep, blocks, avoid)
    check_headings(rep, blocks, args.profile)
    check_common(rep, blocks, cfg[lang], lang, args.profile)
    (check_en(rep, blocks, cfg, args.audience, args.profile) if lang == "en" else check_ko(rep, blocks, cfg, args.profile))
    rep.stats = {"lang": lang, **rep.stats}
    emit(rep, args.json, args.file)
    return rep.exit_code()


def emit(rep, as_json, name):
    order = {"FAIL": 0, "WARN": 1, "INFO": 2}
    rep.findings.sort(key=lambda f: (order[f["level"]], f["line"]))
    if as_json:
        print(json.dumps({"file": name, "stats": rep.stats, "findings": rep.findings}, ensure_ascii=False, indent=2))
        return
    counts = {k: sum(1 for f in rep.findings if f["level"] == k) for k in order}
    print(f"{name}: {counts['FAIL']} FAIL, {counts['WARN']} WARN, {counts['INFO']} INFO | "
          + ", ".join(f"{k}={v}" for k, v in rep.stats.items()))
    for f in rep.findings:
        loc = f"L{f['line']}" if f["line"] else "doc"
        out = f"  {f['level']:<4} {loc:<6} {f['rule']}: {f['message']}"
        if f["snippet"]:
            out += f"  «{f['snippet']}»"
        if f["instead"]:
            out += f"  → {f['instead']}"
        print(out)


def read_strings(path):
    p = Path(path)
    txt = p.read_text(encoding="utf-8")
    if p.suffix == ".strings":
        return [{"id": k, "text": v.replace('\\"', '"')}
                for k, v in re.findall(r'"((?:[^"\\]|\\.)+)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', txt)]
    if p.suffix == ".xml":
        return [{"id": k, "text": html.unescape(re.sub(r"<[^>]+>", "", v)).replace("\\'", "'")}
                for k, v in re.findall(r'<string[^>]*name="([^"]+)"[^>]*>(.*?)</string>', txt, re.S)]
    data = json.loads(txt)
    if isinstance(data, list):
        return data
    flat = []

    def walk(prefix, node):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(f"{prefix}.{k}" if prefix else k, v)
        elif isinstance(node, str):
            flat.append({"id": prefix, "text": node})
    walk("", data)
    return flat


def run_limits(args):
    items = read_strings(args.file)
    limits = json.loads(Path(args.limits).read_text(encoding="utf-8")) if args.limits else {}
    rows, fail = [], False
    for it in items:
        lim, unit = it.get("limit"), it.get("unit", "chars")
        if lim is None and it["id"] in limits:
            spec = limits[it["id"]]
            lim, unit = (spec, "chars") if isinstance(spec, int) else (spec["limit"], spec.get("unit", "chars"))
        if lim is None and it["id"] in STORE_LIMITS:
            lim, unit = STORE_LIMITS[it["id"]]
        text = unicodedata.normalize("NFC", it["text"])
        n_chars, n_bytes = len(text), len(text.encode("utf-8"))
        status = "n/a"
        if lim is not None:
            over = n_chars > lim or ("bytes" in unit and n_bytes > lim)
            status = "FAIL" if over else "ok"
            fail |= over
        if it["id"] == "ios.keywords" and re.search(r",\s|\s,", text):
            status, fail = "FAIL", True
        rows.append({"id": it["id"], "chars": n_chars, "bytes": n_bytes, "limit": lim, "unit": unit, "status": status})
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            extra = f" ({r['bytes']} bytes)" if "bytes" in str(r["unit"]) else ""
            print(f"  {r['status']:<4} {r['id']}: {r['chars']}/{r['limit']} {r['unit']}{extra}")
        if any(r["id"] == "ios.keywords" for r in rows):
            print("  note: keywords are comma-separated with no spaces. Apple's page says 100 characters and some "
                  "guides say 100 bytes, so both are checked. Hangul takes 3 bytes per syllable.")
    return 1 if fail else 0


def run_stats(args):
    for f in args.files:
        raw = Path(f).read_text(encoding="utf-8")
        blocks = blocks_from_lines(strip_markup(raw, f.endswith((".html", ".htm"))))
        lang = args.lang if args.lang != "auto" else detect_lang(" ".join(b["text"] for b in blocks))
        lens = [len(s.split()) if lang == "ko" else len(words(s))
                for b in blocks if b["kind"] == "para" for s in split_sentences(b["text"], lang)]
        if not lens:
            print(f"{f}: no prose")
            continue
        lens.sort()
        q = lambda p: lens[int(p * (len(lens) - 1))]
        unit = "어절" if lang == "ko" else "words"
        print(f"{f}: lang={lang} n={len(lens)} mean={sum(lens) / len(lens):.1f} p50={q(.5)} p75={q(.75)} "
              f"p90={q(.9)} p95={q(.95)} max={lens[-1]} ({unit})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="check a draft against the standard")
    c.add_argument("file")
    c.add_argument("--lang", default="auto", choices=["auto", "en", "ko"])
    c.add_argument("--audience", default="internal", choices=["end-user", "marketing", "internal", "developer"])
    c.add_argument("--profile", default="doc", choices=["doc", "ui", "marketing", "slides"])
    c.add_argument("--voice", help="voice guide with a vanessa-config block (default: .vanessa/voice.md if present)")
    c.add_argument("--glossary", help="glossary with an Avoid column (default: .vanessa/glossary.md if present)")
    c.add_argument("--json", action="store_true")
    lp = sub.add_parser("limits", help="check strings against character limits")
    lp.add_argument("file")
    lp.add_argument("--limits")
    lp.add_argument("--json", action="store_true")
    sp = sub.add_parser("stats", help="sentence-length distribution, for calibrating targets")
    sp.add_argument("files", nargs="+")
    sp.add_argument("--lang", default="auto", choices=["auto", "en", "ko"])
    args = ap.parse_args(argv)
    if args.cmd == "check":
        args.voice = args.voice or (".vanessa/voice.md" if Path(".vanessa/voice.md").exists() else None)
        args.glossary = args.glossary or (".vanessa/glossary.md" if Path(".vanessa/glossary.md").exists() else None)
        return run_check(args)
    return run_limits(args) if args.cmd == "limits" else run_stats(args)


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    sys.exit(main())
