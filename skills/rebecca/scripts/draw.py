#!/usr/bin/env python3
"""draw: paint illustrations and generative art with code. Seeded, free, no image model.

  python scripts/draw.py ink      --seed 7 --size 1600x1000 --palette "#1c1a17,#f2ece0" --out hero.png
  python scripts/draw.py flow     --seed 3 --size 1600x1000 --palette "#14213d,#f4efe4,#e05a2b" --lines 1800
  python scripts/draw.py contour  --seed 9 --size 1200x1200 --palette "#2a2a28,#efe9dc" --levels 28
  python scripts/draw.py hatch    --from photo.png --palette "#1d1b19,#f1ebdf" --spacing 6   # engraving from any image
  python scripts/draw.py sheet    flow --seeds 1-12 --size 800x500 --palette "..."           # contact sheet of seeds
  python scripts/draw.py flow ... --stages .design/review/flow-stages                          # frames for draw-on video

Palette order: ink (first), paper (second), accents (rest, used sparingly). Same seed + args = same image.
Render, open the PNG, judge it against the failure list in references/generative-art.md, change one parameter,
re-render. Import the functions (noise2, fbm2, fbm1, flow_lines, iso_lines, hatch_from) for custom scenes.
"""
import argparse, math, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def hexrgb(h):
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def noise2(rng, w, h, cell):
    gx, gy = int(w / cell) + 2, int(h / cell) + 2
    g = rng.random((gy, gx))
    x = np.arange(w) / cell
    y = np.arange(h) / cell
    xi, yi = x.astype(int), y.astype(int)
    xf, yf = x - xi, y - yi
    sx, sy = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
    a = g[np.ix_(yi, xi)]; b = g[np.ix_(yi, xi + 1)]
    c = g[np.ix_(yi + 1, xi)]; d = g[np.ix_(yi + 1, xi + 1)]
    top = a + (b - a) * sx; bot = c + (d - c) * sx
    return top + (bot - top) * sy[:, None]


def fbm2(rng, w, h, cell, octaves=5, gain=0.5):
    out, amp, tot = np.zeros((h, w)), 1.0, 0.0
    for o in range(octaves):
        out += amp * noise2(rng, w, h, max(cell / 2 ** o, 1.5)); tot += amp; amp *= gain
    return out / tot


def fbm1(rng, n, cell, octaves=6, gain=0.5):
    return fbm2(rng, n, 1, cell, octaves, gain)[0]


def paper(rng, w, h, rgb, tooth=0.035):
    base = np.ones((h, w, 3)) * np.array(rgb) / 255
    t = fbm2(rng, w, h, 3, 3) - 0.5
    fib = fbm2(rng, w, h, 60, 4) - 0.5
    return np.clip(base * (1 + tooth * t[..., None] + tooth * 0.8 * fib[..., None]), 0, 1)


def blend(canvas, mask, rgb, alpha=1.0):
    m = np.clip(mask * alpha, 0, 1)[..., None]
    return canvas * (1 - m) + (np.array(rgb) / 255) * m


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def ink(rng, w, h, pal, layers=5, stages=None):
    inkc, pap = pal[0], pal[1]
    accent = pal[2] if len(pal) > 2 else None
    c = paper(rng, w, h, pap)
    ys = np.arange(h)[:, None]
    snap(stages, c, "paper")
    for i in range(layers):
        depth = i / max(layers - 1, 1)
        base = h * (0.38 + 0.42 * depth)
        amp = h * (0.30 - 0.16 * depth)
        ridge = base - amp * (fbm1(rng, w, w * (0.35 - 0.15 * depth)) - 0.35) * 2
        dist = ys - ridge[None, :]
        wash = np.where(dist > 0, np.exp(-dist / (h * (0.10 + 0.08 * depth))), 0)
        tex = 0.75 + 0.5 * fbm2(rng, w, h, 18, 3)
        strength = 0.25 + 0.6 * depth
        c = blend(c, wash * tex, inkc, strength)
        edge = np.exp(-np.abs(dist) / (1.2 + 1.5 * depth)) * (0.6 + 0.6 * fbm2(rng, w, h, 40, 2))
        c = blend(c, edge, inkc, 0.35 + 0.5 * depth)
        mist_y = base + h * 0.06
        mist = np.exp(-((ys - mist_y) / (h * 0.05)) ** 2) * (0.5 + fbm2(rng, w, h, 120, 3))
        c = blend(c, np.broadcast_to(mist, (h, w)), pap, 0.55 * (1 - depth))
        snap(stages, c, f"layer-{i}")
    if accent:
        cx, cy, r = w * rng.uniform(0.65, 0.85), h * rng.uniform(0.12, 0.22), min(w, h) * 0.035
        yy, xx = np.mgrid[0:h, 0:w]
        disc = np.clip(r - np.hypot(xx - cx, yy - cy), 0, 1)
        c = blend(c, disc, accent, 0.9)
    return c


def flow_lines(rng, w, h, n, steps, step, cell, curl=2.2):
    ang = fbm2(rng, w, h, cell, 4) * math.tau * curl
    lines = []
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        pts = [(x, y)]
        for _ in range(steps):
            a = ang[int(y), int(x)]
            x += math.cos(a) * step; y += math.sin(a) * step
            if not (0 <= x < w and 0 <= y < h):
                break
            pts.append((x, y))
        if len(pts) > 4:
            lines.append(pts)
    return lines


def flow(rng, w, h, pal, n=1500, stages=None):
    ss = 2
    base = to_img(paper(rng, w, h, pal[1])).resize((w * ss, h * ss))
    d = ImageDraw.Draw(base)
    lines = flow_lines(rng, w, h, n, steps=int(rng.integers(60, 140)), step=2.0, cell=min(w, h) * 0.45)
    accents = pal[2:]
    for k, pts in enumerate(lines):
        col = accents[k % len(accents)] if accents and rng.random() < 0.04 else pal[0]
        d.line([(x * ss, y * ss) for x, y in pts], fill=col, width=max(1, int(ss * rng.uniform(0.6, 1.4))))
        if stages and k % max(1, len(lines) // 12) == 0:
            snap(stages, np.asarray(base.resize((w, h), Image.LANCZOS)) / 255, f"lines-{k:05d}")
    return np.asarray(base.resize((w, h), Image.LANCZOS)) / 255


def iso_lines(field, levels, width=1.0):
    gy, gx = np.gradient(field)
    frac = (field * levels) % 1.0
    px = np.minimum(frac, 1 - frac) / (np.hypot(gx, gy) * levels + 1e-6)
    return np.clip(1 - px / width, 0, 1)


def contour(rng, w, h, pal, levels=24, stages=None):
    c = paper(rng, w, h, pal[1])
    field = fbm2(rng, w, h, min(w, h) * 0.6, 5)
    lines = iso_lines(field, levels, 0.9)
    c = blend(c, lines, pal[0], 0.9)
    if len(pal) > 2:
        peak = field > np.quantile(field, 0.985)
        c = blend(c, peak.astype(float), pal[2], 0.85)
    snap(stages, c, "contour")
    return c


def hatch_from(lum, spacing=6, angles=(45, -45, 0, 90), thresholds=(0.75, 0.55, 0.35, 0.18), width=0.9):
    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w]
    out = np.zeros((h, w))
    for ang, th in zip(angles, thresholds):
        a = math.radians(ang)
        u = xx * math.cos(a) + yy * math.sin(a)
        stripe = np.clip(1 - np.abs((u % spacing) - spacing / 2) / width, 0, 1)
        out = np.maximum(out, stripe * (lum < th))
    return out


def hatch(rng, w, h, pal, src=None, spacing=6, stages=None):
    if src:
        im = Image.open(src).convert("L")
        if w and h:
            im = im.resize((w, h), Image.LANCZOS)
        w, h = im.size
        lum = np.asarray(im.filter(ImageFilter.GaussianBlur(1.2))) / 255
        lo, hi = np.percentile(lum, (2, 98))
        lum = np.clip((lum - lo) / max(hi - lo, 1e-3), 0, 1)
    else:
        lum = fbm2(rng, w, h, min(w, h) * 0.5, 4)
    c = paper(rng, w, h, pal[1])
    c = blend(c, hatch_from(lum, spacing), pal[0], 0.92)
    snap(stages, c, "hatch")
    return c


def snap(stages, arr, name):
    if stages:
        Path(stages).mkdir(parents=True, exist_ok=True)
        n = len(list(Path(stages).glob("*.png")))
        to_img(arr).save(Path(stages) / f"{n:03d}-{name}.png")


def render(kind, seed, w, h, pal, a):
    rng = np.random.default_rng(seed)
    if kind == "ink":
        return ink(rng, w, h, pal, a.layers, a.stages)
    if kind == "flow":
        return flow(rng, w, h, pal, a.lines, a.stages)
    if kind == "contour":
        return contour(rng, w, h, pal, a.levels, a.stages)
    return hatch(rng, w, h, pal, a.src, a.spacing, a.stages)


def seeds(spec):
    if "-" in spec:
        lo, hi = spec.split("-"); return list(range(int(lo), int(hi) + 1))
    return [int(s) for s in spec.split(",")]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["ink", "flow", "contour", "hatch", "sheet"])
    ap.add_argument("sheet_kind", nargs="?", choices=["ink", "flow", "contour", "hatch"])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--seeds", default="1-9")
    ap.add_argument("--size", default="1600x1000")
    ap.add_argument("--palette", default="#1c1a17,#f2ece0")
    ap.add_argument("--out")
    ap.add_argument("--stages")
    ap.add_argument("--layers", type=int, default=5)
    ap.add_argument("--lines", type=int, default=1500)
    ap.add_argument("--levels", type=int, default=24)
    ap.add_argument("--spacing", type=int, default=6)
    ap.add_argument("--from", dest="src")
    a = ap.parse_args()
    w, h = (int(v) for v in a.size.lower().split("x"))
    pal = [hexrgb(p) for p in a.palette.split(",")]
    if len(pal) < 2:
        sys.exit("--palette needs at least ink and paper")
    if a.kind == "sheet":
        if not a.sheet_kind:
            sys.exit("sheet needs a kind: draw.py sheet flow --seeds 1-12")
        ss = seeds(a.seeds)
        a.stages = None
        tiles = [to_img(render(a.sheet_kind, s, w, h, pal, a)) for s in ss]
        cols = math.ceil(math.sqrt(len(tiles)))
        rows = math.ceil(len(tiles) / cols)
        sheet = Image.new("RGB", (cols * w, rows * (h + 24)), (250, 250, 248))
        d = ImageDraw.Draw(sheet)
        for i, (t, s) in enumerate(zip(tiles, ss)):
            x, y = (i % cols) * w, (i // cols) * (h + 24)
            sheet.paste(t, (x, y + 24)); d.text((x + 8, y + 6), f"seed {s}", fill=(30, 30, 30))
        out = a.out or f".design/review/{a.sheet_kind}-sheet.png"
    else:
        sheet = to_img(render(a.kind, a.seed, w, h, pal, a))
        out = a.out or f".design/assets/{a.kind}-s{a.seed}.png"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
