#!/usr/bin/env python3
"""Non-AI post-processing: salvage flawed generations and finish good ones. Costs nothing.

Every output is registered in the library with `derived_from` + the op, so lineage is never lost.
INPUT is an asset id (A-0007) or a file path.

Salvage / cleanup
  trim        crop to visible (non-transparent) content + padding
  crop        --box x,y,w,h | --aspect 16:9 [--focus 0.5,0.4]   rescue a good region of a bad frame
  key         remove a flat background (auto-detected from edges), flood-filled from the border
  resize      --w/--h [--fit contain|cover|stretch] [--nearest]
  upscale     --factor N [--nearest]
  flip        --axis h|v
  mask        --shape circle|rounded|squircle [--radius 48]
  flatten     --color "#hex"   put transparency on a solid ground (social exports, app icons)

Bring onto the brand (kills the generic "AI color grade")
  palette-map --palette "#hex,#hex,..." [--dither]    snap every pixel to the brand palette
  duotone     --dark "#hex" --light "#hex"
  grade       [--hue deg] [--sat x] [--contrast x] [--bright x] [--temp -1..1]
  posterize   --levels N
  extract-palette [--n 6]                             print dominant colors (no file written)

Tactile finishing (adds the imperfection AI images lack)
  grain       [--amount 0.06] [--mono]
  halftone    [--cell 8] [--ink "#hex"] [--paper "#hex"]
  riso        --inks "#hexA,#hexB" [--offset 3] [--paper "#hex"]
  vignette    [--strength 0.35]

Sprites and pixel art
  pixelate    --px 64 [--colors 16 | --palette ...] [--outline "#hex"] [--scale 8]
  outline     --color "#hex" [--width 2]            sticker / sprite outline from alpha
  shadow      [--dx 0 --dy 8 --blur 12 --color "#000" --opacity 0.35]
  slice       --grid 4x2 | --size 64x64               sprite sheet -> frames (each registered)
  sheet       --inputs A,B,C... [--cols 4]            frames -> sprite sheet
  gif         --inputs A,B,C... | --from-sheet ID --grid 4x1 ; [--fps 10] [--holds "0:3,5:2"] [--scale 4]
  composite   --over ID [--at x,y] [--scale 1.0] [--opacity 1.0] [--blend normal|multiply|screen]
  tile        --w 2048 --h 2048                       mirror-tile a texture patch seamlessly
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import designlib as dl  # noqa: E402


# ------------------------------------------------------------------ helpers

def hex2rgb(h: str) -> tuple[int, int, int]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def parse_palette(s: str) -> np.ndarray:
    return np.array([hex2rgb(x) for x in s.split(",") if x.strip()], dtype=np.float64)


def srgb_to_oklab(rgb: np.ndarray) -> np.ndarray:
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    l = 0.4122214708 * c[..., 0] + 0.5363325363 * c[..., 1] + 0.0514459929 * c[..., 2]
    m = 0.2119034982 * c[..., 0] + 0.6806995451 * c[..., 1] + 0.1073969566 * c[..., 2]
    s = 0.0883024619 * c[..., 0] + 0.2817188376 * c[..., 1] + 0.6299787005 * c[..., 2]
    l_, m_, s_ = np.cbrt(l), np.cbrt(m), np.cbrt(s)
    return np.stack([0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
                     1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
                     0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_], axis=-1)


def nearest_palette(rgb: np.ndarray, pal: np.ndarray) -> np.ndarray:
    a = srgb_to_oklab(rgb.reshape(-1, 3).astype(np.float64))
    b = srgb_to_oklab(pal)
    idx = ((a[:, None, :] - b[None, :, :]) ** 2).sum(-1).argmin(1)
    return pal[idx].reshape(rgb.shape).astype(np.uint8)


def oklab_kmeans(rgb_px: np.ndarray, k: int, iters: int = 12, seed: int = 3) -> np.ndarray:
    """Perceptual palette from opaque pixels (N,3 uint8) -> (k,3) uint8. Keeps small accents like eye whites."""
    uniq = np.unique(rgb_px.reshape(-1, 3), axis=0)
    if len(uniq) <= k:
        return uniq.astype(np.uint8)
    lab = srgb_to_oklab(rgb_px.astype(np.float64))
    rng = np.random.default_rng(seed)
    cent = [lab[rng.integers(len(lab))]]
    for _ in range(1, k):  # k-means++ init: favors distinct colors
        d = np.min(((lab[:, None, :] - np.array(cent)[None]) ** 2).sum(-1), axis=1)
        cent.append(lab[rng.choice(len(lab), p=d / d.sum())] if d.sum() > 0 else lab[rng.integers(len(lab))])
    cent = np.array(cent)
    for _ in range(iters):
        lbl = ((lab[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)
        for j in range(k):
            if np.any(lbl == j):
                cent[j] = lab[lbl == j].mean(0)
    lbl = ((lab[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)
    # representative = the actual pixel color nearest each centroid (no muddy averages)
    out = []
    for j in range(k):
        m = lbl == j
        if np.any(m):
            sub = rgb_px[m]
            out.append(sub[((lab[m] - cent[j]) ** 2).sum(-1).argmin()])
    return np.array(out, dtype=np.uint8)


def load(r: Path, ref: str):
    rec, p = dl.find_asset(r, ref)
    if not p.exists():
        dl.die(f"input not found: {ref}")
    im = Image.open(p)
    return rec, p, im


def rgba(im: Image.Image) -> Image.Image:
    im.seek(0) if hasattr(im, "seek") else None
    return im.convert("RGBA")


def save(r: Path, out_img: Image.Image, args, src_rec, src_path: Path, op: str, extra_tags=None, suffix=".png",
         sources=None):
    out = Path(args.out) if getattr(args, "out", None) else None
    if out is None:
        d = r / "assets" / "derived"
        d.mkdir(parents=True, exist_ok=True)
        base = (src_rec["id"] if src_rec else src_path.stem)
        i = 1
        while True:
            out = d / f"{base}-{op}{'' if i == 1 else '-' + str(i)}{suffix}"
            if not out.exists():
                break
            i += 1
    out.parent.mkdir(parents=True, exist_ok=True)
    if suffix == ".gif":
        out_img[0].save(out, save_all=True, append_images=out_img[1], **out_img[2])
    else:
        out_img.save(out)
    parents = sources if sources is not None else ([src_rec["id"]] if src_rec else [])
    tags = (src_rec.get("tags", []) if src_rec else []) + (extra_tags or []) + (getattr(args, "tag", None) or [])
    rec = dl.register(r, out, kind="animation" if suffix == ".gif" else "image", source="derived",
                      prompt=(src_rec or {}).get("prompt", ""), model=(src_rec or {}).get("model", ""),
                      derived_from=parents, op=f"{op} {getattr(args, 'opdesc', '')}".strip(), tags=tags)
    print(f"{rec['id']}  {out}")
    return rec


# -------------------------------------------------------------------- ops

def op_trim(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    bbox = im.getchannel("A").point(lambda v: 255 if v > a.threshold else 0).getbbox()
    if not bbox:
        dl.die("image is fully transparent")
    x0, y0, x1, y1 = bbox
    pad = a.pad
    out = Image.new("RGBA", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    out.paste(im.crop(bbox), (pad, pad))
    save(r, out, a, rec, p, "trim")


def op_crop(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    W, H = im.size
    if a.box:
        x, y, w, h = [int(v) for v in a.box.split(",")]
    elif a.aspect:
        aw, ah = [float(v) for v in a.aspect.split(":")]
        if W / H > aw / ah:
            h, w = H, int(H * aw / ah)
        else:
            w, h = W, int(W * ah / aw)
        fx, fy = [float(v) for v in a.focus.split(",")]
        x = int(min(max(fx * W - w / 2, 0), W - w))
        y = int(min(max(fy * H - h / 2, 0), H - h))
    else:
        dl.die("crop needs --box or --aspect")
    save(r, im.crop((x, y, x + w, y + h)), a, rec, p, "crop")


def op_key(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    rgb = im.convert("RGB")
    W, H = rgb.size
    if a.color:
        bg = hex2rgb(a.color)
    else:
        arr = np.asarray(rgb)
        edge = np.concatenate([arr[0], arr[-1], arr[:, 0], arr[:, -1]])
        bg = tuple(int(v) for v in np.median(edge, axis=0))
    work = rgb.copy()
    sentinel = (1, 254, 3)
    seeds = [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1), (W // 2, 0), (W // 2, H - 1), (0, H // 2), (W - 1, H // 2)]
    arr0 = np.asarray(rgb).astype(int)
    for sx, sy in seeds:
        if np.abs(arr0[sy, sx] - np.array(bg)).sum() <= a.tolerance * 3:
            ImageDraw.floodfill(work, (sx, sy), sentinel, thresh=a.tolerance)
    w = np.asarray(work)
    if not a.flood:  # global key: every pixel near bg color, not just border-connected
        mask_bg = (np.abs(arr0 - np.array(bg)).sum(-1) <= a.tolerance * 3)
    else:
        mask_bg = np.all(w == np.array(sentinel), axis=-1)
    alpha = np.where(mask_bg, 0, np.asarray(im.getchannel("A"))).astype(np.uint8)
    am = Image.fromarray(alpha)
    if a.erode:
        am = am.filter(ImageFilter.MinFilter(a.erode * 2 + 1))
    if a.feather:
        am = am.filter(ImageFilter.GaussianBlur(a.feather))
    al = np.asarray(am).astype(np.float64) / 255.0
    px = np.asarray(im.convert("RGB")).astype(np.float64)
    semi = (al > 0.02) & (al < 0.98)
    bgv = np.array(bg, dtype=np.float64)
    un = (px - bgv * (1 - al[..., None])) / np.maximum(al[..., None], 0.02)  # remove bg color bleed at edges
    px = np.where(semi[..., None], un.clip(0, 255), px)
    px[al <= 0.02] = 0  # fully transparent pixels carry no stray color into later resizes
    out = Image.fromarray(px.astype(np.uint8)).convert("RGBA")
    out.putalpha(am)
    a.opdesc = f"bg={'#%02x%02x%02x' % bg} tol={a.tolerance}"
    save(r, out, a, rec, p, "key", ["cutout"])


def op_resize(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    res = Image.NEAREST if a.nearest else Image.LANCZOS
    W, H = im.size
    tw = a.w or int(W * (a.h / H))
    th = a.h or int(H * (a.w / W))
    if a.fit == "stretch":
        out = im.resize((tw, th), res)
    elif a.fit == "cover":
        out = ImageOps.fit(im, (tw, th), res)
    else:
        out = im.copy()
        out.thumbnail((tw, th), res)
        canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        canvas.paste(out, ((tw - out.width) // 2, (th - out.height) // 2))
        out = canvas
    save(r, out, a, rec, p, f"resize{tw}x{th}")


def op_upscale(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    out = im.resize((im.width * a.factor, im.height * a.factor), Image.NEAREST if a.nearest else Image.LANCZOS)
    save(r, out, a, rec, p, f"x{a.factor}")


def op_flip(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    save(r, ImageOps.mirror(im) if a.axis == "h" else ImageOps.flip(im), a, rec, p, f"flip{a.axis}")


def op_mask(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    W, H = im.size
    m = Image.new("L", (W * 4, H * 4), 0)
    d = ImageDraw.Draw(m)
    if a.shape == "circle":
        s = min(W, H) * 4
        d.ellipse([(W * 4 - s) // 2, (H * 4 - s) // 2, (W * 4 + s) // 2, (H * 4 + s) // 2], fill=255)
    elif a.shape == "rounded":
        d.rounded_rectangle([0, 0, W * 4 - 1, H * 4 - 1], radius=a.radius * 4, fill=255)
    else:  # squircle (superellipse n=5)
        yy, xx = np.mgrid[0:H * 4, 0:W * 4]
        nx, ny = (xx / (W * 4 - 1)) * 2 - 1, (yy / (H * 4 - 1)) * 2 - 1
        m = Image.fromarray(((np.abs(nx) ** 5 + np.abs(ny) ** 5) <= 1).astype(np.uint8) * 255)
    m = m.resize((W, H), Image.LANCZOS)
    alpha = Image.fromarray(np.minimum(np.asarray(m), np.asarray(im.getchannel("A"))))
    out = im.copy()
    out.putalpha(alpha)
    save(r, out, a, rec, p, f"mask-{a.shape}")


def op_flatten(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    bg = Image.new("RGBA", im.size, hex2rgb(a.color) + (255,))
    bg.alpha_composite(im)
    save(r, bg.convert("RGB"), a, rec, p, "flatten")


def op_palette_map(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    pal = parse_palette(a.palette)
    alpha = im.getchannel("A")
    if a.dither:
        pimg = Image.new("P", (1, 1))
        flat = [int(v) for c in pal for v in c]
        pimg.putpalette(flat + flat[:3] * (256 - len(pal)))
        out = im.convert("RGB").quantize(palette=pimg, dither=Image.Dither.FLOYDSTEINBERG).convert("RGBA")
    else:
        out = Image.fromarray(nearest_palette(np.asarray(im.convert("RGB")), pal)).convert("RGBA")
    out.putalpha(alpha)
    a.opdesc = f"{len(pal)} colors"
    save(r, out, a, rec, p, "palette", ["on-palette"])


def op_duotone(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    g = np.asarray(im.convert("L")).astype(np.float64)[..., None] / 255.0
    dk, lt = np.array(hex2rgb(a.dark)), np.array(hex2rgb(a.light))
    out = Image.fromarray((dk + (lt - dk) * g).clip(0, 255).astype(np.uint8)).convert("RGBA")
    out.putalpha(im.getchannel("A"))
    save(r, out, a, rec, p, "duotone", ["on-palette"])


def op_grade(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    alpha = im.getchannel("A")
    hsv = np.asarray(im.convert("RGB").convert("HSV")).astype(np.float64)
    hsv[..., 0] = (hsv[..., 0] + a.hue / 360 * 255) % 255
    hsv[..., 1] = (hsv[..., 1] * a.sat).clip(0, 255)
    rgb = np.asarray(Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB")).astype(np.float64)
    rgb = (rgb - 128) * a.contrast + 128
    rgb = rgb * a.bright
    rgb[..., 0] += 18 * a.temp
    rgb[..., 2] -= 18 * a.temp
    out = Image.fromarray(rgb.clip(0, 255).astype(np.uint8)).convert("RGBA")
    out.putalpha(alpha)
    save(r, out, a, rec, p, "grade")


def op_posterize(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    out = ImageOps.posterize(im.convert("RGB"), max(1, min(8, a.levels))).convert("RGBA")
    out.putalpha(im.getchannel("A"))
    save(r, out, a, rec, p, f"posterize{a.levels}")


def op_extract_palette(r, a):
    _, _, im = load(r, a.input)
    im = rgba(im)
    arr = np.asarray(im)
    px = arr[arr[..., 3] > 16][:, :3]
    if len(px) == 0:
        dl.die("no opaque pixels")
    q = Image.fromarray(px.reshape(-1, 1, 3).astype(np.uint8)).quantize(colors=a.n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[: a.n * 3]
    counts = sorted(q.getcolors(), reverse=True)
    for cnt, idx in counts:
        c = pal[idx * 3: idx * 3 + 3]
        print(f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}  {100 * cnt / len(px):5.1f}%")


def op_grain(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    arr = np.asarray(im).astype(np.float64)
    rng = np.random.default_rng(a.seed)
    shape = arr.shape[:2] + ((1,) if a.mono else (3,))
    noise = rng.normal(0, 255 * a.amount, shape)
    if a.size > 1:
        small = rng.normal(0, 255 * a.amount, (arr.shape[0] // a.size + 1, arr.shape[1] // a.size + 1) + shape[2:])
        noise = np.kron(small, np.ones((a.size, a.size) + ((1,) * (len(shape) - 2))))[: arr.shape[0], : arr.shape[1]]
    arr[..., :3] = (arr[..., :3] + noise).clip(0, 255)
    save(r, Image.fromarray(arr.astype(np.uint8), "RGBA"), a, rec, p, "grain", ["textured"])


def op_halftone(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    g = np.asarray(im.convert("L")).astype(np.float64) / 255.0
    W, H = im.size
    ss = 4
    out = Image.new("RGB", (W * ss, H * ss), hex2rgb(a.paper))
    d = ImageDraw.Draw(out)
    c = a.cell
    for y in range(0, H, c):
        for x in range(0, W, c):
            dark = 1 - g[y:y + c, x:x + c].mean()
            rad = (c * ss / 2) * np.sqrt(dark) * 1.15
            if rad > 0.4:
                cx, cy = (x + c / 2) * ss, (y + c / 2) * ss
                d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=hex2rgb(a.ink))
    out = out.resize((W, H), Image.LANCZOS).convert("RGBA")
    out.putalpha(im.getchannel("A"))
    save(r, out, a, rec, p, "halftone", ["textured"])


def op_riso(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    inks = [hex2rgb(x) for x in a.inks.split(",")][:2]
    g = 1 - np.asarray(im.convert("L")).astype(np.float64) / 255.0
    paper = np.ones(g.shape + (3,)) * np.array(hex2rgb(a.paper)) / 255.0
    layers = [np.clip((g - 0.15) * 1.3, 0, 1), np.clip((g - 0.55) * 2.2, 0, 1)]
    rng = np.random.default_rng(7)
    out = paper
    for i, (ink, cov) in enumerate(zip(inks, layers)):
        shift = a.offset * (1 if i else -1)
        cov = np.roll(np.roll(cov, shift, 0), -shift, 1)
        cov = np.clip(cov + rng.normal(0, 0.05, cov.shape), 0, 1)
        inkc = np.array(ink) / 255.0
        out = out * (1 - cov[..., None] * (1 - inkc))  # multiply ink onto paper
    res = Image.fromarray((out * 255).astype(np.uint8)).convert("RGBA")
    res.putalpha(im.getchannel("A"))
    save(r, res, a, rec, p, "riso", ["textured", "on-palette"])


def op_vignette(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    W, H = im.size
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    f = 1 - a.strength * np.clip(d, 0, 1) ** 2
    arr = np.asarray(im).astype(np.float64)
    arr[..., :3] *= f[..., None]
    save(r, Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA"), a, rec, p, "vignette")


def _outline_img(im: Image.Image, color, width: int) -> Image.Image:
    alpha = im.getchannel("A").point(lambda v: 255 if v > 32 else 0)
    grown = alpha.filter(ImageFilter.MaxFilter(width * 2 + 1))
    base = Image.new("RGBA", im.size, color + (0,))
    base.putalpha(grown)
    base.alpha_composite(im)
    return base


def op_pixelate(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    W, H = im.size
    s = a.px / max(W, H)
    small = im.convert("RGBa").resize((max(1, round(W * s)), max(1, round(H * s))), Image.BOX).convert("RGBA")
    alpha = small.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    rgb = small.convert("RGB")
    if a.palette:
        pal = parse_palette(a.palette)
    else:
        arr = np.asarray(rgb)
        opaque = arr[np.asarray(alpha) > 0]
        pal = oklab_kmeans(opaque if len(opaque) else arr.reshape(-1, 3), a.colors).astype(np.float64)
    rgb = Image.fromarray(nearest_palette(np.asarray(rgb), pal))
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    if a.outline:
        pad = Image.new("RGBA", (out.width + 2, out.height + 2), (0, 0, 0, 0))
        pad.paste(out, (1, 1))
        out = _outline_img(pad, hex2rgb(a.outline), 1)
    if a.scale > 1:
        out = out.resize((out.width * a.scale, out.height * a.scale), Image.NEAREST)
    a.opdesc = f"{a.px}px"
    save(r, out, a, rec, p, "pixel", ["pixel-art"])


def op_outline(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    w = a.width
    pad = Image.new("RGBA", (im.width + 2 * w, im.height + 2 * w), (0, 0, 0, 0))
    pad.paste(im, (w, w))
    save(r, _outline_img(pad, hex2rgb(a.color), w), a, rec, p, "outline", ["sticker"])


def op_shadow(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    m = a.blur * 2 + max(abs(a.dx), abs(a.dy))
    canvas = Image.new("RGBA", (im.width + 2 * m, im.height + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, hex2rgb(a.color) + (0,))
    sh.putalpha(im.getchannel("A").point(lambda v: int(v * a.opacity)))
    canvas.paste(sh, (m + a.dx, m + a.dy), sh)
    canvas = canvas.filter(ImageFilter.GaussianBlur(a.blur))
    canvas.alpha_composite(im, (m, m))
    save(r, canvas, a, rec, p, "shadow")


def _grid(spec: str):
    c, rr = spec.lower().split("x")
    return int(c), int(rr)


def op_slice(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    if a.grid:
        cols, rows = _grid(a.grid)
        fw, fh = im.width // cols, im.height // rows
    else:
        fw, fh = [int(v) for v in a.size.lower().split("x")]
        cols, rows = im.width // fw, im.height // fh
    n = 0
    for y in range(rows):
        for x in range(cols):
            fr = im.crop((x * fw, y * fh, (x + 1) * fw, (y + 1) * fh))
            if fr.getchannel("A").getbbox() is None:
                continue
            a.out = None
            n += 1
            save(r, fr, a, rec, p, f"frame{n:02d}", ["frame"])


def _gather(r, ids: str):
    recs, frames = [], []
    for ref in ids.split(","):
        rec, p, im = load(r, ref.strip())
        recs.append(rec)
        frames.append(rgba(im))
    return recs, frames


def op_sheet(r, a):
    recs, frames = _gather(r, a.inputs)
    fw, fh = max(f.width for f in frames), max(f.height for f in frames)
    cols = a.cols or len(frames)
    rows = (len(frames) + cols - 1) // cols
    out = Image.new("RGBA", (cols * fw, rows * fh), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        out.paste(f, ((i % cols) * fw + (fw - f.width) // 2, (i // cols) * fh + (fh - f.height) // 2))
    save(r, out, a, recs[0], Path(a.inputs.split(",")[0]), "sheet", ["spritesheet"],
         sources=[x["id"] for x in recs if x])


def op_gif(r, a):
    if a.from_sheet:
        rec, p, im = load(r, a.from_sheet)
        im = rgba(im)
        cols, rows = _grid(a.grid)
        fw, fh = im.width // cols, im.height // rows
        frames = [im.crop((x * fw, y * fh, (x + 1) * fw, (y + 1) * fh)) for y in range(rows) for x in range(cols)]
        recs = [rec]
    else:
        recs, frames = _gather(r, a.inputs)
        rec, p = recs[0], Path(a.inputs.split(",")[0])
    if a.scale > 1:
        frames = [f.resize((f.width * a.scale, f.height * a.scale), Image.NEAREST) for f in frames]
    base = int(1000 / a.fps)
    holds = {}
    if a.holds:  # per-frame hold multipliers give animation rhythm (anticipation, impact, rest)
        for part in a.holds.split(","):
            k, v = part.split(":")
            holds[int(k)] = float(v)
    durations = [int(base * holds.get(i, 1)) for i in range(len(frames))]
    W = max(f.width for f in frames)
    H = max(f.height for f in frames)
    pframes = []
    for f in frames:
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        canvas.alpha_composite(f, ((W - f.width) // 2, (H - f.height) // 2))
        q = canvas.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        idx = np.asarray(q).copy()
        idx[np.asarray(canvas.getchannel("A")) < 128] = 255  # reserved transparent index
        pf = Image.fromarray(idx.astype(np.uint8), "P")
        pal = q.getpalette()[: 255 * 3]
        pf.putpalette(pal + [0] * (768 - len(pal)))
        pframes.append(pf)
    opts = dict(duration=durations, loop=0, disposal=2, transparency=255, optimize=False)
    save(r, (pframes[0], pframes[1:], opts), a, rec, p, "anim", ["animation"],
         suffix=".gif", sources=[x["id"] for x in recs if x])


def op_composite(r, a):
    rec, p, base = load(r, a.input)
    base = rgba(base)
    orec, op_, over = load(r, a.over)
    over = rgba(over)
    if a.scale != 1.0:
        over = over.resize((int(over.width * a.scale), int(over.height * a.scale)), Image.LANCZOS)
    if a.opacity < 1:
        over.putalpha(over.getchannel("A").point(lambda v: int(v * a.opacity)))
    x, y = [int(v) for v in a.at.split(",")]
    if a.blend == "normal":
        base.alpha_composite(over, (x, y))
        out = base
    else:
        layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        layer.alpha_composite(over, (x, y))
        b = np.asarray(base).astype(np.float64) / 255
        o = np.asarray(layer).astype(np.float64) / 255
        mix = b[..., :3] * o[..., :3] if a.blend == "multiply" else 1 - (1 - b[..., :3]) * (1 - o[..., :3])
        res = b.copy()
        res[..., :3] = b[..., :3] * (1 - o[..., 3:]) + mix * o[..., 3:]
        out = Image.fromarray((res * 255).astype(np.uint8), "RGBA")
    save(r, out, a, rec, p, "composite", sources=[x["id"] for x in (rec, orec) if x])


def op_tile(r, a):
    rec, p, im = load(r, a.input)
    im = rgba(im)
    quad = Image.new("RGBA", (im.width * 2, im.height * 2))
    quad.paste(im, (0, 0))
    quad.paste(ImageOps.mirror(im), (im.width, 0))
    quad.paste(ImageOps.flip(im), (0, im.height))
    quad.paste(ImageOps.flip(ImageOps.mirror(im)), (im.width, im.height))
    out = Image.new("RGBA", (a.w, a.h))
    for y in range(0, a.h, quad.height):
        for x in range(0, a.w, quad.width):
            out.paste(quad, (x, y))
    save(r, out, a, rec, p, "tile", ["texture"])


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--out")
    common.add_argument("--tag", action="append")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    sp = ap.add_subparsers(dest="op", required=True)

    def add(name, needs_input=True):
        p = sp.add_parser(name, parents=[common])
        if needs_input:
            p.add_argument("input")
        return p

    p = add("trim"); p.add_argument("--pad", type=int, default=8); p.add_argument("--threshold", type=int, default=8)
    p = add("crop"); p.add_argument("--box"); p.add_argument("--aspect"); p.add_argument("--focus", default="0.5,0.5")
    p = add("key"); p.add_argument("--color"); p.add_argument("--tolerance", type=int, default=28)
    p.add_argument("--no-flood", dest="flood", action="store_false"); p.add_argument("--feather", type=float, default=0.6)
    p.add_argument("--erode", type=int, default=0)
    p = add("resize"); p.add_argument("--w", type=int); p.add_argument("--h", type=int)
    p.add_argument("--fit", default="contain", choices=["contain", "cover", "stretch"]); p.add_argument("--nearest", action="store_true")
    p = add("upscale"); p.add_argument("--factor", type=int, default=2); p.add_argument("--nearest", action="store_true")
    p = add("flip"); p.add_argument("--axis", default="h", choices=["h", "v"])
    p = add("mask"); p.add_argument("--shape", default="rounded", choices=["circle", "rounded", "squircle"])
    p.add_argument("--radius", type=int, default=48)
    p = add("flatten"); p.add_argument("--color", default="#ffffff")
    p = add("palette-map"); p.add_argument("--palette", required=True); p.add_argument("--dither", action="store_true")
    p = add("duotone"); p.add_argument("--dark", required=True); p.add_argument("--light", required=True)
    p = add("grade"); p.add_argument("--hue", type=float, default=0); p.add_argument("--sat", type=float, default=1)
    p.add_argument("--contrast", type=float, default=1); p.add_argument("--bright", type=float, default=1)
    p.add_argument("--temp", type=float, default=0)
    p = add("posterize"); p.add_argument("--levels", type=int, default=4)
    p = add("extract-palette"); p.add_argument("--n", type=int, default=6)
    p = add("grain"); p.add_argument("--amount", type=float, default=0.06); p.add_argument("--mono", action="store_true")
    p.add_argument("--size", type=int, default=1); p.add_argument("--seed", type=int, default=11)
    p = add("halftone"); p.add_argument("--cell", type=int, default=8); p.add_argument("--ink", default="#1b1b1b")
    p.add_argument("--paper", default="#f2efe6")
    p = add("riso"); p.add_argument("--inks", required=True); p.add_argument("--offset", type=int, default=3)
    p.add_argument("--paper", default="#f4f1ea")
    p = add("vignette"); p.add_argument("--strength", type=float, default=0.35)
    p = add("pixelate"); p.add_argument("--px", type=int, default=64); p.add_argument("--colors", type=int, default=16)
    p.add_argument("--palette"); p.add_argument("--outline"); p.add_argument("--scale", type=int, default=1)
    p = add("outline"); p.add_argument("--color", default="#ffffff"); p.add_argument("--width", type=int, default=6)
    p = add("shadow"); p.add_argument("--dx", type=int, default=0); p.add_argument("--dy", type=int, default=8)
    p.add_argument("--blur", type=int, default=12); p.add_argument("--color", default="#000000")
    p.add_argument("--opacity", type=float, default=0.35)
    p = add("slice"); p.add_argument("--grid"); p.add_argument("--size")
    p = add("sheet", needs_input=False); p.add_argument("--inputs", required=True); p.add_argument("--cols", type=int)
    p = add("gif", needs_input=False); p.add_argument("--inputs"); p.add_argument("--from-sheet"); p.add_argument("--grid", default="4x1")
    p.add_argument("--fps", type=float, default=10); p.add_argument("--holds"); p.add_argument("--scale", type=int, default=1)
    p = add("composite"); p.add_argument("--over", required=True); p.add_argument("--at", default="0,0")
    p.add_argument("--scale", type=float, default=1.0); p.add_argument("--opacity", type=float, default=1.0)
    p.add_argument("--blend", default="normal", choices=["normal", "multiply", "screen"])
    p = add("tile"); p.add_argument("--w", type=int, required=True); p.add_argument("--h", type=int, required=True)

    a = ap.parse_args()
    a.opdesc = ""
    r = dl.root(a.root)
    globals()["op_" + a.op.replace("-", "_")](r, a)


if __name__ == "__main__":
    main()
