#!/usr/bin/env python3
"""slop_lint: a deterministic gate for AI-design tells. Run it, fix, re-run until it passes.

Why a script and not just rules in prose: measured runs show written anti-slop guidance alone can
score equal to or worse than no guidance (the model reads "be distinctive" as "add more"), while a
mechanical gate the agent must pass removes the known tells reliably. Rules here are the floor; taste
is still judged by the critic pass. Every finding carries a positive alternative ("instead"), because
banning a default without naming a replacement makes the model jump to the NEXT default.

Usage
  python scripts/slop_lint.py PATH [PATH...] [--json] [--allow RULE ...] [--warn-only]
Exit code 1 if any FAIL remains (after allowances).

Allowances (the brief wins): if the user/brief explicitly asked for something on this list, allow it
with a reason instead of fighting it:
  - inline:  <!-- slop-ok: rule-id (brief: "cream paper look") -->  or  // slop-ok: rule-id (...)
  - project: .design/slop-allow.json  {"rule-id": "reason quoted from the brief"}
"""
from __future__ import annotations

import argparse
import colorsys
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

EXTS = {".html", ".htm", ".css", ".scss", ".sass", ".less", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte",
        ".astro", ".md", ".mdx", ".dart", ".swift", ".kt", ".kts", ".xml", ".liquid", ".hbs", ".njk", ".erb"}
COPY_EXTS = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".md", ".mdx", ".dart", ".swift",
             ".kt", ".liquid", ".hbs", ".njk", ".erb", ".js", ".ts"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", ".svelte-kit", ".design", "vendor",
             "Pods", ".dart_tool", ".gradle", "out", "coverage", ".turbo", ".vercel", "DerivedData", ".remotion"}

OVERUSED_FONTS = ["inter", "roboto", "poppins", "montserrat", "open sans", "lato", "space grotesk", "space mono",
                  "plus jakarta sans", "dm sans", "dm serif display", "dm serif", "fraunces", "playfair display",
                  "cormorant", "cormorant garamond", "instrument serif", "instrument sans", "geist", "outfit",
                  "syne", "newsreader", "recoleta", "ibm plex sans", "ibm plex serif", "ibm plex mono", "manrope",
                  "sora", "lora", "crimson pro", "jetbrains mono"]

BUZZ = ["elevate", "seamless", "seamlessly", "unleash", "supercharge", "revolutioni[sz]e", "empower", "effortless",
        "effortlessly", "cutting-edge", "next-gen", "next-generation", "game-chang", "world-class", "leverage",
        "streamline", "unlock your", "unlock the power", "harness the", "synergy", "holistic", "state-of-the-art",
        "best-in-class", "enterprise-grade", "all-in-one", "delve", "in today's fast-paced", "take your .{1,20} to the next level",
        "transform the way", "reimagine", "redefine", "innovative solution", "robust solution", "tailored solutions",
        "boost your productivity", "lightning-fast", "blazing[- ]fast", "magic happens", "like never before",
        "your all-in-one", "built for the future", "the future of", "one-stop", "crafted with care", "meticulously",
        "pixel-perfect", "designed for humans", "at scale", "mission-critical", "frictionless"]

APHORISMS = [
    r"\bnot (just )?(a|an|another) [^.!?<]{2,40}[.!]\s+(a|an|it'?s|we'?re|this is|it is)\b",
    r"\bit'?s not (just )?(about )?[^,.<]{2,40}[,.;]\s*it'?s\b",
    r"\bno [a-z-]+\.\s+no [a-z-]+\.",
    r"\b(reimagined|redefined|reinvented|perfected)\.",
    r"\bwhere [a-z]+ meets [a-z]+\b",
    r"\bthe [a-z]+ you('ve| have) been waiting for\b",
    r"\bless [a-z]+\.\s*more [a-z]+\.",
    r"\b[a-z]+ theater\b",
]

PLACEHOLDER = r"\b(lorem ipsum|john doe|jane doe|acme( inc| corp)?|example corp|your company|company name|product name|foo@bar|john@example)\b"
PERFECT_NUM = r"(\b99(\.9+)?%|\b100%\s+(secure|uptime|satisfaction)|\b10x\b|\b10,?000\+|\b50k\+|\b1m\+ users|\b5,?000\+ (teams|companies))"
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")

TEMPLATE_COLORS = [  # untouched framework starter themes
    (r"ColorScheme\.fromSeed\(\s*seedColor:\s*Colors\.deepPurple", "Flutter starter theme (deepPurple seed)"),
    (r"Color\(0x[fF]{2}6650[aA]4\)|Color\(0x[fF]{2}[dD]0[bB][cC][fF][fF]\)|Color\(0x[fF]{2}625[bB]71\)", "Compose starter Purple40/Purple80"),
    (r"Color\(0x[fF]{2}6200[eE][eE]\)|#[fF]{2}6200[eE][eE]\b|@color/purple_(200|500|700)", "Android template purple_500/6200EE"),
]


class Rule:
    def __init__(self, rid, sev, why, instead):
        self.id, self.sev, self.why, self.instead = rid, sev, why, instead


R = {r.id: r for r in [
    Rule("ai-gradient", "fail", "purple/violet/indigo gradients (and indigo->pink/blue) are the most recognized AI fingerprint",
         "let ONE committed brand color own a whole region; use texture, imagery, or a flat field instead of a gradient wash"),
    Rule("gradient-text", "fail", "gradient-filled text is decorative emphasis with no meaning",
         "emphasis through size, weight or a solid accent color; keep gradients off type"),
    Rule("template-theme", "fail", "an untouched framework starter theme ships the framework's identity, not the product's",
         "define a product palette in DESIGN.md and theme the framework from those tokens"),
    Rule("glow", "warn", "colored zero-offset glows / halos on dark grounds are the dark-SaaS tell",
         "real elevation (offset + soft blur, neutral or hue-tinted dark) or no shadow; light comes from the scene, not the element"),
    Rule("gradient-orbs", "fail", "blurred gradient blobs floating behind a hero are filler, not art direction",
         "an authored asset (illustration, 3D render, photo, product UI) or an honest flat field"),
    Rule("decor-grid", "warn", "hairline grid / dot-field backgrounds drawn as decoration read as generated",
         "plain ground, a real texture asset, or a grid that actually organizes content"),
    Rule("side-tab", "fail", "thick colored border on one side of a card or callout is a top AI tell",
         "differentiate with spacing, a type change, an icon, or a full tinted surface"),
    Rule("thin-border-wide-shadow", "warn", "hairline border + wide diffuse shadow on the same element",
         "commit to one: a defined edge OR a soft elevation"),
    Rule("eyebrow", "warn", "tiny tracked uppercase label above a heading (repeated = template chrome)",
         "delete it and let the heading carry the meaning; if a category is needed, put it in plain sentence case"),
    Rule("eyebrow-repeated", "fail", "the same eyebrow chrome on several sections is the generated-page signature",
         "remove the labels; vary section openings by content (image-led, quote-led, data-led)"),
    Rule("decor-dot", "warn", "decorative colored / pulsing dots before labels simulate liveness",
         "only show a status dot for real, changing state; otherwise remove"),
    Rule("numbered-sections", "warn", "01 / 02 / 03 section numbering on content that is not a real sequence",
         "number only true sequences (steps, timeline); otherwise let headings stand alone"),
    Rule("icon-tile-cards", "fail", "rounded icon tile + heading + blurb repeated as cards is the universal AI feature section",
         "show the feature working (screenshot crop, live demo, illustration), or use a list/table with real detail"),
    Rule("three-up-grid", "warn", "a row of three equal cards is the default feature layout",
         "vary scale: one dominant item + supporting items, a 2-column zig-zag, a table, or a single demo"),
    Rule("glass-overuse", "warn", "glass/blur used as decoration on many surfaces",
         "reserve translucency for the control layer over content (platform convention), not content cards"),
    Rule("bounce-easing", "warn", "bounce/elastic easing on UI reads dated and toy-like (unless the brand is a toy)",
         "exponential ease-out for UI; springs with low bounce; save overshoot for character animation"),
    Rule("entrance-spam", "fail", "the same fade/slide-up entrance on many sections is scattered motion",
         "keep ONE orchestrated moment (page-load or hero reveal) + responsive feedback on interactions; content visible by default"),
    Rule("reduced-motion", "warn", "animations without a reduced-motion path",
         "gate non-essential motion behind prefers-reduced-motion / platform reduce-motion and render the end state"),
    Rule("marquee", "warn", "auto-scrolling logo/content marquees demand attention they have not earned",
         "a static, curated proof row with named customers and outcomes"),
    Rule("typewriter", "warn", "typing effects / blinking cursors fake activity",
         "show the real output or product state"),
    Rule("hover-image-scale", "warn", "scale-on-hover for images is a stock generated interaction",
         "let images sit still or reveal real detail (caption, alternate state) on hover"),
    Rule("overused-font", "warn", "a training-data default typeface; nobody chose it, the model did",
         "pick a face from the product's world (see references/visual-craft.md) or record a specific reason in DESIGN.md and allow it"),
    Rule("italic-serif-display", "warn", "oversized italic serif hero headline is the 2026 'tasteful AI' default",
         "match the face to the register; use italic only where the content earns emphasis"),
    Rule("mono-body", "warn", "monospace body text as a 'technical' costume",
         "monospace only for code, data, measurements"),
    Rule("cream-ground", "warn", "warm cream/beige page ground is the reflex 'tasteful' AI surface",
         "derive the ground from the use scene and brand materials; write the one-sentence scene in DESIGN.md"),
    Rule("terracotta-accent", "warn", "terracotta/clay accent (~#D97757) is a known AI default (and Anthropic's own accent)",
         "an accent from the product's world, tested for contrast"),
    Rule("safe-accent", "warn", "emerald/acid-green or default indigo/blue-600 as the accent: the next-safest default",
         "a deliberately chosen hue with a reason; run creative_roll.py for the palette axis if undecided"),
    Rule("uniform-radius", "warn", "one border-radius on everything flattens hierarchy",
         "a radius scale tied to element size/role (e.g. 4 / 10 / 20 / pill), or a committed sharp system"),
    Rule("same-shadow", "warn", "the same soft gray shadow under every element",
         "an elevation scale used only where layering is real"),
    Rule("placeholder-content", "fail", "placeholder names/companies/lorem ship as content",
         "real or realistic, locale-appropriate content; label demo data as sample"),
    Rule("perfect-numbers", "warn", "round, unsourced stats (99.9%, 10x, 10,000+) read as invented",
         "real, specific, sourced numbers, or a concrete outcome statement"),
    Rule("buzzword", "warn", "generic marketing verb/phrase that fits any product",
         "say what the product does, for whom, in its own vocabulary"),
    Rule("buzzword-saturated", "fail", "copy saturated with generic marketing phrases",
         "rewrite with concrete nouns and verbs from the product's domain"),
    Rule("aphorism", "warn", "manufactured-contrast aphorisms ('Not X. Y.', 'No A. No B.', 'X. Reimagined.')",
         "a plain claim the reader can verify"),
    Rule("em-dash", "warn", "em-dash cadence in UI/marketing copy is an AI-writing tell",
         "periods, commas, colons, or parentheses; short sentences"),
    Rule("em-dash-saturated", "fail", "em-dash saturation in UI/marketing copy", "restructure sentences without dashes"),
    Rule("arrow-cta", "warn", "an arrow glyph appended to every link/button label",
         "the label names the action; use an icon only where direction is meaningful"),
    Rule("middot-chain", "warn", "meta strings chained with middle dots (A · B · C)", "line breaks, columns, or a sentence"),
    Rule("scroll-cue", "warn", "'scroll to explore' cues", "make the first viewport complete; content below speaks for itself"),
    Rule("generic-cta", "warn", "CTA label that names no outcome (Get Started, Learn More, Submit)",
         "name what happens: 'Create your first board', 'See pricing', 'Save changes'"),
    Rule("emoji-ui", "warn", "emoji standing in for an icon system or decorating headings",
         "one consistent icon family (or authored glyphs); emoji only in a playful, social brand voice by choice"),
]}


def hex_to_hls(h: str):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) == 8:
        h = h[2:] if h[:2].lower() == "ff" else h[:6]
    if len(h) != 6:
        return None
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, l, s


def is_purpleish(hx):
    v = hex_to_hls(hx)
    return v and 235 <= v[0] <= 300 and v[2] > 0.3 and 0.2 < v[1] < 0.85


def is_cream(hx):
    v = hex_to_hls(hx)
    return v and 28 <= v[0] <= 60 and v[1] >= 0.88 and 0.15 <= v[2] <= 0.75


def is_terracotta(hx):
    v = hex_to_hls(hx)
    return v and 8 <= v[0] <= 24 and 0.5 <= v[1] <= 0.68 and 0.45 <= v[2] <= 0.75


SAFE_ACCENTS = {"10b981", "059669", "22c55e", "34d399", "a3e635", "84cc16", "4f46e5", "6366f1", "2563eb", "3b82f6", "7c3aed", "8b5cf6"}


class Linter:
    def __init__(self, allow: dict):
        self.allow = allow
        self.findings = []
        self.motion_files, self.reduce_motion_seen = [], False
        self.radius = Counter()
        self.shadow_count = 0

    def add(self, rid, path, line_no, snippet, lines=None):
        if rid in self.allow:
            return
        if lines is not None and line_no:
            ctx = " ".join(lines[max(0, line_no - 2): line_no])
            if re.search(r"slop-ok:\s*" + re.escape(rid) + r"\b", ctx):
                return
        self.findings.append({"rule": rid, "severity": R[rid].sev, "file": str(path), "line": line_no,
                              "snippet": snippet.strip()[:160]})

    def lint_file(self, path: Path):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return
        if len(text) > 2_000_000:
            return
        lines = text.splitlines()
        ext = path.suffix.lower()
        is_copy = ext in COPY_EXTS
        counts = Counter()
        firsts = {}

        def hit(rid, i, s, count_only=False):
            counts[rid] += 1
            firsts.setdefault(rid, (i, s))
            if not count_only:
                self.add(rid, path, i, s, lines)

        for i, ln in enumerate(lines, 1):
            low = ln.lower()
            # ---------- color & surface
            if re.search(r"(bg-(gradient|linear)-to|bg-linear-|linear-gradient|radial-gradient|conic-gradient|LinearGradient\(|Brush\.(linear|horizontal|vertical)Gradient)", ln):
                hexes = re.findall(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", ln) + re.findall(r"0x([0-9a-fA-F]{8})", ln)
                tw = re.findall(r"(from|via|to)-(purple|violet|indigo|fuchsia)-\d{2,3}", ln)
                swift = re.search(r"\[\s*\.(purple|indigo)\s*,\s*\.(blue|pink|purple|indigo|cyan)|\[\s*\.(blue|pink|cyan)\s*,\s*\.(purple|indigo)", ln)
                if tw or swift or sum(1 for h in hexes if is_purpleish(h)) >= 1 and len(hexes) >= 2 or \
                        re.search(r"Colors\.(deepPurple|purple|indigo|purpleAccent)", ln):
                    hit("ai-gradient", i, ln)
            if re.search(r"bg-clip-text|background-clip:\s*text|text-fill-color:\s*transparent|ShaderMask\(|TextStyle\([^)]*brush\s*=", ln) or \
                    (re.search(r"foregroundStyle\(", ln) and "Gradient" in ln and "Text(" in "".join(lines[max(0, i - 3):i])):
                hit("gradient-text", i, ln)
            for pat, label in TEMPLATE_COLORS:
                if re.search(pat, ln):
                    hit("template-theme", i, f"{label}: {ln}")
            if re.search(r"(box|text)-shadow:\s*0(px)?\s+0(px)?\s+\d+px[^;]*(#(?!000|111|222)[0-9a-f]{3,6}|rgba?\((?!0,\s*0,\s*0))", low) or \
                    re.search(r"\bshadow-(?!sm|md|lg|xl|2xl|none|inner)[a-z]+-\d{3}(/\d+)?\b|drop-shadow-\[0_0_|shadow-\[0_0_", ln) or \
                    re.search(r"BoxShadow\([^)]*color:\s*(?!Colors\.black|Color\(0x[0-9a-fA-F]{2}000000\))[^)]*offset:\s*Offset\.zero", ln):
                hit("glow", i, ln)
            if re.search(r"blur-(2xl|3xl|\[\d{2,3}px\])", ln) and "rounded-full" in ln:
                hit("gradient-orbs", i, ln, count_only=True)
            if re.search(r"(bg-\[linear-gradient|background-image:\s*linear-gradient)", ln) and re.search(r"(bg-\[size:|background-size:\s*\d+px\s+\d+px|\d+px_\d+px)", " ".join(lines[i - 1:i + 2])):
                hit("decor-grid", i, ln)
            if re.search(r"border-l-(2|4|8|\[\d+px\])\b.*border-[a-z]+-\d{3}|border-left:\s*[3-9]px\s+solid", ln):
                hit("side-tab", i, ln)
            if re.search(r"\bborder\b(?!-none)", ln) and re.search(r"\bshadow-(lg|xl|2xl)\b", ln):
                hit("thin-border-wide-shadow", i, ln)
            # ---------- type & chrome
            if (re.search(r"\buppercase\b", ln) and re.search(r"tracking-(wide|wider|widest|\[0?\.\d+em\])", ln) and re.search(r"text-(xs|sm|\[1[0-3]px\]|\[0?\.[67]\d*rem\])", ln)) or \
                    (re.search(r"\.textCase\(\.uppercase\)", ln) and re.search(r"\.(tracking|kerning)\(", ln)) or \
                    (re.search(r"toUpperCase\(\)", ln) and re.search(r"letterSpacing:\s*[1-9]", " ".join(lines[i - 1:i + 3]))):
                hit("eyebrow", i, ln, count_only=True)
            if re.search(r"rounded-full", ln) and re.search(r"\b(h|w|size)-(1|1\.5|2)\b", ln) and re.search(r"\bbg-", ln):
                hit("decor-dot", i, ln)
            elif re.search(r"animate-(pulse|ping)\b", ln):
                hit("decor-dot", i, ln)
            if re.search(r">\s*0[1-9]\s*(/|\.|—|<)|[\"']0[1-9]\s*/\s*0?\d[\"']|padStart\(2,\s*[\"']0[\"']\)", ln):
                hit("numbered-sections", i, ln)
            if re.search(r"rounded-(lg|xl|2xl|full)", ln) and re.search(r"\b(h|size)-(8|9|10|11|12|14)\b", ln) and \
                    re.search(r"items-center", ln) and re.search(r"justify-center", ln) and re.search(r"\bbg-", ln):
                hit("icon-tile-cards", i, ln, count_only=True)
            if re.search(r"(md:|lg:)?grid-cols-3\b|repeat\(\s*3\s*,\s*(1fr|minmax)", ln):
                hit("three-up-grid", i, ln)
            if re.search(r"backdrop-blur|backdrop-filter:\s*blur|\.ultraThinMaterial|\.thinMaterial|BackdropFilter\(|\.glassEffect\(", ln):
                hit("glass-overuse", i, ln, count_only=True)
            if re.search(r"animate-bounce|ease:\s*[\"'](bounce|elastic)|Curves\.(bounce|elastic)\w*|bounce:\s*0?\.[5-9]|\.(bouncy|snappy)\(extraBounce", ln):
                hit("bounce-easing", i, ln)
            if re.search(r"whileInView|initial=\{\{\s*opacity:\s*0|data-aos=|fade-?in-?up|fadeInUp|slide-?up|\.fadeIn\(|reveal-on-scroll|\.animate\(\)\.fade", ln, re.I):
                hit("entrance-spam", i, ln, count_only=True)
            if re.search(r"@keyframes|gsap\.|from ['\"]motion|framer-motion|whileHover|withAnimation|AnimationController|animateContentSize|AnimatedContainer|\.animation\(|animate-", ln):
                self.motion_files.append(str(path))
            if re.search(r"prefers-reduced-motion|useReducedMotion|reducedMotion|accessibilityReduceMotion|disableAnimations|isReduceMotionEnabled|ReduceMotion|MotionConfig", ln):
                self.reduce_motion_seen = True
            if re.search(r"animate-marquee|<marquee|\bmarquee\b", low):
                hit("marquee", i, ln)
            if re.search(r"typewriter|animate-blink|caret-blink|TypeAnimation|AnimatedTextKit|TypeIt", ln):
                hit("typewriter", i, ln)
            if re.search(r"(group-)?hover:scale-1(0[2-9]|10)\b", ln) and re.search(r"<img|Image\b|object-cover", ln):
                hit("hover-image-scale", i, ln)
            fonts = re.findall(r"font-family:\s*([^;}{]+)|family=([A-Za-z+]+)|GoogleFonts\.([a-zA-Z]+)|from ['\"]next/font/google['\"]|import\s*{\s*([A-Za-z_, ]+)\s*}\s*from ['\"]next/font/google|\.custom\(\"([^\"]+)\"|fontFamily:\s*\[?['\"]([^'\"]+)", ln)
            for grp in fonts:
                for f in grp:
                    if not f:
                        continue
                    for name in re.split(r"[,_+]", f):
                        n = re.sub(r"([a-z])([A-Z])", r"\1 \2", name).strip().strip("'\"").lower()
                        first = n.split(",")[0].strip()
                        if first in OVERUSED_FONTS:
                            hit("overused-font", i, f"{first}: {ln}")
            if re.search(r"<h1[^>]*\b(italic)\b|<h1[^>]*>.*<(em|i)>|\.font\(\.system\([^)]*design:\s*\.serif[^)]*\)\)\.italic\(\)", ln):
                hit("italic-serif-display", i, ln)
            if re.search(r"(<body|<p)[^>]*\bfont-mono\b", ln):
                hit("mono-body", i, ln)
            if re.search(r"(background(-color)?|bg|backgroundColor|scaffoldBackgroundColor|--(bg|background|surface|paper)[\w-]*)\s*[:=]\s*[\"']?#([0-9a-fA-F]{6})", ln):
                m = re.search(r"#([0-9a-fA-F]{6})", ln)
                if m and is_cream(m.group(1)):
                    hit("cream-ground", i, ln)
            for hx in re.findall(r"#([0-9a-fA-F]{6})\b", ln):
                if is_terracotta(hx) and re.search(r"(accent|primary|brand|cta|button|--)", low):
                    hit("terracotta-accent", i, ln)
                if hx.lower() in SAFE_ACCENTS and re.search(r"(accent|primary|brand|cta|--color-(primary|accent))", low):
                    hit("safe-accent", i, ln)
            if re.search(r"\bbg-(indigo|violet|emerald)-(500|600)\b", ln) and re.search(r"<(button|a)\b|Button", ln):
                hit("safe-accent", i, ln, count_only=True)
            for m in re.findall(r"\brounded-(sm|md|lg|xl|2xl|3xl|\[[^\]]+\])", ln):
                self.radius[m] += 1
            for m in re.findall(r"border-radius:\s*([\d.]+(px|rem|em))|BorderRadius\.circular\(([\d.]+)\)|cornerRadius:\s*([\d.]+)|RoundedCornerShape\(([\d.]+)", ln):
                v = next((x for x in m if x and x not in ("px", "rem", "em")), None)
                if v:
                    self.radius[v] += 1
            if re.search(r"rgba\(0,\s*0,\s*0,\s*0?\.1\)|\bshadow-(md|lg)\b|elevation:\s*[2-8]\b", ln):
                self.shadow_count += 1
            # ---------- copy
            if is_copy:
                if re.search(PLACEHOLDER, low) and not re.search(r"placeholder=|test|spec|mock", low):
                    hit("placeholder-content", i, ln)
                if re.search(PERFECT_NUM, low):
                    hit("perfect-numbers", i, ln)
                if not re.search(r"^\s*(//|#|\*|import|export|const|let|var)\b", ln):
                    found = [b for b in BUZZ if re.search(r"\b" + b, low)]
                    if found:
                        hit("buzzword", i, f"{', '.join(found[:4])}: {ln}")
                        for b in found:
                            counts["_buzz:" + b] += 1
                for a in APHORISMS:
                    if re.search(a, low):
                        hit("aphorism", i, ln)
                        break
                if "—" in ln:
                    counts["_emdash"] += ln.count("—")
                    if re.search(r"<(h[1-6]|button|a|label)\b", ln):
                        hit("em-dash", i, ln)
                if re.search(r"(→|&rarr;|->)\s*</(a|button)>|>\s*[A-Z][^<]{1,30}\s(→|&rarr;)\s*<", ln):
                    hit("arrow-cta", i, ln)
                if len(re.findall(r"\s·\s", ln)) >= 2:
                    hit("middot-chain", i, ln)
                if re.search(r"scroll (to|down to) (explore|discover|learn|see)|↓\s*scroll", low):
                    hit("scroll-cue", i, ln)
                if re.search(r">\s*(get started|learn more|submit|click here|read more)\s*<|Text\(\s*[\"'](Get Started|Learn More|Submit)[\"']", ln, re.I):
                    hit("generic-cta", i, ln)
                if EMOJI.search(ln) and re.search(r"<(h[1-6]|button|li|span|p)\b|Text\(|title:", ln):
                    hit("emoji-ui", i, ln)

        # ---------- file-level thresholds
        if counts["eyebrow"] >= 2:
            self.add("eyebrow-repeated", path, firsts["eyebrow"][0], f"{counts['eyebrow']} eyebrow labels in file", lines)
        elif counts["eyebrow"] == 1:
            self.add("eyebrow", path, *firsts["eyebrow"], lines)
        if counts["icon-tile-cards"] >= 3:
            self.add("icon-tile-cards", path, firsts["icon-tile-cards"][0], f"{counts['icon-tile-cards']} icon tiles", lines)
        if counts["gradient-orbs"] >= 1:
            self.add("gradient-orbs", path, firsts["gradient-orbs"][0], f"{counts['gradient-orbs']} blurred blob(s)", lines)
        if counts["glass-overuse"] >= 3:
            self.add("glass-overuse", path, firsts["glass-overuse"][0], f"{counts['glass-overuse']} glass/blur surfaces", lines)
        if counts["entrance-spam"] >= 4:
            self.add("entrance-spam", path, firsts["entrance-spam"][0], f"{counts['entrance-spam']} entrance animations", lines)
        if counts["safe-accent"] >= 2 and "safe-accent" not in [f["rule"] for f in self.findings if f["file"] == str(path)]:
            self.add("safe-accent", path, firsts["safe-accent"][0], "default indigo/emerald primary buttons", lines)
        distinct_buzz = len([k for k in counts if k.startswith("_buzz:")])
        if distinct_buzz >= 3:
            self.add("buzzword-saturated", path, 0, f"{distinct_buzz} distinct generic phrases", lines)
        if counts["_emdash"] >= 8:
            self.add("em-dash-saturated", path, 0, f"{counts['_emdash']} em-dashes in copy", lines)
        elif counts["_emdash"] >= 3:
            self.add("em-dash", path, 0, f"{counts['_emdash']} em-dashes in copy", lines)

    def finish(self):
        if self.motion_files and not self.reduce_motion_seen:
            self.add("reduced-motion", self.motion_files[0], 0, f"motion in {len(set(self.motion_files))} file(s), no reduce-motion handling found")
        total = sum(v for k, v in self.radius.items() if k != "full")
        if total >= 10:
            top, n = self.radius.most_common(1)[0]
            if n / total >= 0.85:
                self.add("uniform-radius", "(project)", 0, f"radius '{top}' used in {n}/{total} places")
        if self.shadow_count >= 8:
            self.add("same-shadow", "(project)", 0, f"{self.shadow_count} identical soft shadows")


def collect(paths):
    for p in paths:
        p = Path(p)
        if p.is_file():
            yield p
            continue
        for dp, dns, fns in os.walk(p):
            dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
            for fn in fns:
                if Path(fn).suffix.lower() in EXTS and not fn.endswith((".min.js", ".min.css", ".d.ts", ".map")):
                    yield Path(dp) / fn


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow", nargs="*", default=[], help="rule ids allowed by the brief")
    ap.add_argument("--warn-only", action="store_true", help="never exit non-zero")
    ap.add_argument("--rules", action="store_true", help="print the rule catalog and exit")
    a = ap.parse_args()
    if a.rules:
        for r in R.values():
            print(f"{r.sev.upper():4} {r.id:24} {r.why}\n      instead: {r.instead}")
        return
    allow = {k: "cli" for k in a.allow}
    for cand in [Path.cwd() / ".design" / "slop-allow.json", Path(a.paths[0]) / ".design" / "slop-allow.json"]:
        if cand.is_file():
            allow.update(json.loads(cand.read_text()))
    L = Linter(allow)
    n = 0
    for f in collect(a.paths):
        L.lint_file(f)
        n += 1
    L.finish()
    fails = [f for f in L.findings if f["severity"] == "fail"]
    warns = [f for f in L.findings if f["severity"] == "warn"]
    if a.json:
        print(json.dumps({"files": n, "fail": len(fails), "warn": len(warns), "findings": L.findings,
                          "allowed": allow}, indent=2))
    else:
        by = defaultdict(list)
        for f in L.findings:
            by[f["rule"]].append(f)
        order = sorted(by, key=lambda k: (R[k].sev != "fail", -len(by[k])))
        for rid in order:
            r = R[rid]
            print(f"\n{r.sev.upper()}  {rid}  ({len(by[rid])})  {r.why}")
            print(f"      instead: {r.instead}")
            for f in by[rid][:6]:
                loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
                print(f"      - {loc}  {f['snippet']}")
            if len(by[rid]) > 6:
                print(f"      ... {len(by[rid]) - 6} more")
        if allow:
            print("\nallowed by brief:", ", ".join(f"{k} ({v})" for k, v in allow.items()))
        print(f"\nslop_lint: {n} files, {len(fails)} FAIL, {len(warns)} WARN"
              + ("  -> PASS (review warnings)" if not fails else "  -> FIX the FAILs and re-run"))
    sys.exit(0 if (a.warn_only or not fails) else 1)


if __name__ == "__main__":
    main()
