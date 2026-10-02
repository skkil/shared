#!/usr/bin/env python3
"""Voice-of-customer helper: deduplicate feedback and count words, phrases, and themes.

A starting point for clustering, not a substitute for reading. Works with Korean and English text.
  python voc.py reviews.csv --text-col text [--id-col id] [--group-col source] [--themes themes.json] [--top 25]
themes.json maps theme names to keyword lists, e.g. {"sync failures": ["sync", "동기화", "lost"], ...};
each row counts once per theme it matches. Output: duplicates removed, top terms and bigrams, theme counts with
denominators and up to 3 short sample quotes per theme (trimmed; anonymize before sharing).
"""
import argparse, collections, csv, json, re

STOP_EN = set("""a an the and or but if then so to of in on at for with from by is are was were be been it its this that
these those i me my we our you your they them their he she his her not no do does did have has had can could would
should will just very really also too app it's i'm im dont don't get got use using used one all when what""".split())
PARTICLES = ("에서는", "으로는", "에서", "으로", "에게", "까지", "부터", "하고", "이랑", "은", "는", "이", "가", "을", "를",
             "에", "의", "도", "로", "와", "과", "만", "요")
STOP_KO = set("그리고 그런데 하지만 너무 정말 진짜 좀 그냥 이거 저거 그거 이게 있어요 없어요 해요 했어요 합니다 있습니다 같아요".split())


def tokens(text):
    out = []
    for t in re.findall(r"[A-Za-z][A-Za-z'\-]+|[가-힣]+|\d+", text.lower()):
        if re.match(r"[가-힣]", t):
            for p in PARTICLES:
                if len(t) > len(p) + 1 and t.endswith(p):
                    t = t[: -len(p)]
                    break
            if t in STOP_KO or len(t) < 2:
                continue
        elif t in STOP_EN or len(t) < 3:
            continue
        out.append(t)
    return out


def norm(text):
    return re.sub(r"[\W_]+", " ", text.lower()).strip()


def jaccard(a, b):
    return len(a & b) / max(1, len(a | b))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file"); ap.add_argument("--text-col", default="text"); ap.add_argument("--id-col")
    ap.add_argument("--group-col"); ap.add_argument("--themes"); ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--near", type=float, default=0.8, help="Jaccard threshold for near-duplicates")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.file, newline="", encoding="utf-8-sig")))
    if rows and a.text_col not in rows[0]:
        raise SystemExit(f"Column '{a.text_col}' not found; columns: {list(rows[0])}")
    seen, kept, dupes = {}, [], 0
    sets = []
    for i, r in enumerate(rows):
        t = (r.get(a.text_col) or "").strip()
        if not t:
            continue
        n = norm(t)
        if n in seen:
            dupes += 1; continue
        s = set(tokens(t))
        if len(s) >= 4 and len(kept) <= 3000 and any(jaccard(s, o) >= a.near for o in sets):
            dupes += 1; continue
        seen[n] = True; sets.append(s)
        kept.append((r.get(a.id_col) if a.id_col else f"row{i + 2}", t, r.get(a.group_col, "") if a.group_col else "", s))
    print(f"# VOC summary: {len(kept)} unique items ({dupes} duplicates or near-duplicates removed from {len(rows)})\n")
    if a.group_col:
        c = collections.Counter(g for _, _, g, _ in kept)
        print("## By " + a.group_col + "\n" + "\n".join(f"- {g or '(blank)'}: {n}" for g, n in c.most_common()) + "\n")
    df = collections.Counter(); bi = collections.Counter()
    for _, t, _, s in kept:
        df.update(s)
        tk = tokens(t)
        bi.update(set(zip(tk, tk[1:])))
    print(f"## Top terms (number of items mentioning each, of {len(kept)})")
    print(", ".join(f"{w} ({n})" for w, n in df.most_common(a.top)) + "\n")
    print("## Top phrases")
    print(", ".join(f"{x} {y} ({n})" for (x, y), n in bi.most_common(a.top) if n > 1) + "\n")
    if a.themes:
        themes = json.load(open(a.themes, encoding="utf-8"))
        print(f"## Themes (items matching any keyword; denominator {len(kept)})\n")
        unmatched = 0
        hits_any = set()
        for name, kws in themes.items():
            kws = [k.lower() for k in kws]
            hits = [(i, t) for i, t, _, _ in kept if any(k in t.lower() for k in kws)]
            hits_any.update(i for i, _ in hits)
            print(f"### {name}: {len(hits)} of {len(kept)} ({len(hits) / max(1, len(kept)):.0%})")
            for i, t in hits[:3]:
                print(f"- {i}: \"{t[:120]}{'...' if len(t) > 120 else ''}\"")
            print()
        unmatched = len(kept) - len(hits_any)
        print(f"Unmatched by any theme: {unmatched}. Read these; new themes hide there.")


if __name__ == "__main__":
    main()
