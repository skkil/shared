#!/usr/bin/env python3
"""palette: build perceptual tonal ramps and check contrast before any color ships.

  python scripts/palette.py ramp "#2B59C3" --name brand          # 50..950 OKLCH ramp + contrast vs white/black
  python scripts/palette.py check "#1d1d1f" "#f5f0e6"            # WCAG 2 ratio, AA/AAA verdicts
  python scripts/palette.py matrix "#0e2a47,#f2efe6,#ff5a36,#7a8c99"   # every fg/bg pair
  python scripts/palette.py css "#2B59C3" --name brand           # ramp as CSS custom properties
  python scripts/palette.py roles "#2B59C3" --mode light --harmony split   # solve bg/text/primary/accent against contrast floors
  python scripts/palette.py cvd "#0e2a47,#ff5a36,#3c8d5a"         # simulate color blindness, flag pairs that collapse
Roles are solved, not checked afterwards: each role's lightness is searched until it clears its floor.
Targets: body text >= 4.5:1, large text (>=24px or >=19px bold) >= 3:1, UI components/icons >= 3:1.
"""
import argparse, math

def hex2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3: h = "".join(c*2 for c in h)
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

def rgb2hex(c):
    return "#" + "".join(f"{max(0, min(255, round(v*255))):02x}" for v in c)

def lin(c): return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def delin(c): return 12.92*c if c <= 0.0031308 else 1.055*c**(1/2.4)-0.055

def to_oklch(rgb):
    r, g, b = (lin(v) for v in rgb)
    l = 0.4122214708*r+0.5363325363*g+0.0514459929*b
    m = 0.2119034982*r+0.6806995451*g+0.1073969566*b
    s = 0.0883024619*r+0.2817188376*g+0.6299787005*b
    l_, m_, s_ = (math.copysign(abs(x)**(1/3), x) for x in (l, m, s))
    L = 0.2104542553*l_+0.7936177850*m_-0.0040720468*s_
    A = 1.9779984951*l_-2.4285922050*m_+0.4505937099*s_
    B = 0.0259040371*l_+0.7827717662*m_-0.8086757660*s_
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360

def from_oklch(L, C, H):
    A, B = C*math.cos(math.radians(H)), C*math.sin(math.radians(H))
    l_ = L+0.3963377774*A+0.2158037573*B; m_ = L-0.1055613458*A-0.0638541728*B; s_ = L-0.0894841775*A-1.2914855480*B
    l, m, s = l_**3, m_**3, s_**3
    r = 4.0767416621*l-3.3077115913*m+0.2309699292*s
    g = -1.2684380046*l+2.6097574011*m-0.3413193965*s
    b = -0.0041960863*l-0.7034186147*m+1.7076147010*s
    return tuple(delin(v) for v in (r, g, b))

def in_gamut(rgb): return all(-1e-4 <= v <= 1+1e-4 for v in rgb)

def fit(L, C, H):
    lo, hi = 0.0, C  # reduce chroma until it fits sRGB (keeps hue and lightness)
    if in_gamut(from_oklch(L, C, H)): return from_oklch(L, C, H)
    for _ in range(30):
        mid = (lo+hi)/2
        if in_gamut(from_oklch(L, mid, H)): lo = mid
        else: hi = mid
    return from_oklch(L, lo, H)

def lum(rgb): r, g, b = (lin(v) for v in rgb); return 0.2126*r+0.7152*g+0.0722*b

def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la+0.05)/(lb+0.05)

def verdict(r):
    return ("AAA" if r >= 7 else "AA" if r >= 4.5 else "AA-large/UI" if r >= 3 else "FAIL")

STEPS = [(50, .975), (100, .955), (200, .91), (300, .85), (400, .76), (500, .67), (600, .58), (700, .49), (800, .40), (900, .31), (950, .24)]

def ramp(hexc):
    L0, C0, H = to_oklch(hex2rgb(hexc))
    out = []
    for name, L in STEPS:
        taper = 1 - abs(L - 0.62) * 0.9  # chroma peaks mid-ramp, tapers at the ends
        out.append((name, rgb2hex(fit(L, max(0.0, C0*max(0.25, taper)), H))))
    return out

def oklab(rgb):
    L, C, H = to_oklch(rgb)
    return L, C * math.cos(math.radians(H)), C * math.sin(math.radians(H))

def solve_L(C, H, against, floor, start, direction):
    L = start
    while 0.02 <= L <= 0.99:
        rgb = fit(L, C, H)
        if ratio(rgb, against) >= floor:
            return rgb
        L += 0.01 * direction
    return fit(max(0.02, min(0.99, L)), C, H)

HARMONY = {"mono": 0, "analogous": 32, "complementary": 180, "split": 150, "triadic": 120}

def roles(key, mode, harmony):
    L0, C0, H = to_oklch(hex2rgb(key))
    dark = mode == "dark"
    bg = fit(0.17 if dark else 0.975, 0.012, H)
    surface = fit(0.21 if dark else 0.945, 0.014, H)
    d = 1 if dark else -1
    text = solve_L(0.012, H, bg, 8.0, 0.80 if dark else 0.35, d)
    muted = solve_L(0.02, H, bg, 4.5, 0.60 if dark else 0.62, d)
    border = solve_L(0.02, H, bg, 1.6, 0.30 if dark else 0.88, d)
    control = solve_L(0.03, H, bg, 3.0, 0.40 if dark else 0.75, d)
    C = C0
    for _ in range(8):
        primary = solve_L(C, H, bg, 3.0, L0, d)
        label = max([(1, 1, 1), (0.08, 0.08, 0.08), text], key=lambda c: ratio(c, primary))
        if ratio(label, primary) >= 4.5:
            break
        C *= 0.85
    accent = solve_L(max(C0, 0.10), (H + HARMONY[harmony]) % 360, bg, 4.5, L0, d)
    return {"bg": bg, "surface": surface, "text": text, "muted": muted, "border": border, "control-border": control,
            "primary": primary, "on-primary": label, "accent": accent}

CVD = {
    "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}

def simulate(rgb, kind):
    l = [lin(v) for v in rgb]
    m = CVD[kind]
    return tuple(delin(max(0.0, min(1.0, sum(m[i][j] * l[j] for j in range(3))))) for i in range(3))

def dist(a, b):
    return math.dist(oklab(a), oklab(b))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("ramp"); p.add_argument("color"); p.add_argument("--name", default="brand")
    p = sp.add_parser("css"); p.add_argument("color"); p.add_argument("--name", default="brand")
    p = sp.add_parser("check"); p.add_argument("fg"); p.add_argument("bg")
    p = sp.add_parser("matrix"); p.add_argument("colors")
    p = sp.add_parser("roles"); p.add_argument("color"); p.add_argument("--mode", choices=["light", "dark"], default="light")
    p.add_argument("--harmony", choices=list(HARMONY), default="split"); p.add_argument("--css", action="store_true")
    p = sp.add_parser("cvd"); p.add_argument("colors"); p.add_argument("--min-distance", type=float, default=0.07)
    a = ap.parse_args()
    if a.cmd in ("ramp", "css"):
        L, C, H = to_oklch(hex2rgb(a.color))
        if a.cmd == "ramp":
            print(f"source {a.color}: oklch({L:.3f} {C:.3f} {H:.1f})")
        for n, hx in ramp(a.color):
            c = hex2rgb(hx)
            if a.cmd == "css":
                print(f"  --{a.name}-{n}: {hx};")
            else:
                print(f"{a.name}-{n:<4} {hx}  on white {ratio(c,(1,1,1)):5.2f} {verdict(ratio(c,(1,1,1))):11} on black {ratio(c,(0,0,0)):5.2f} {verdict(ratio(c,(0,0,0)))}")
    elif a.cmd == "roles":
        r = roles(a.color, a.mode, a.harmony)
        bg = r["bg"]
        for k, v in r.items():
            if a.css:
                print(f"  --{k}: {rgb2hex(v)};")
            else:
                vs = r["primary"] if k == "on-primary" else bg
                print(f"{k:15} {rgb2hex(v)}  {ratio(v, vs):5.2f}:1 vs {'primary' if k == 'on-primary' else 'bg'}")
    elif a.cmd == "cvd":
        cs = [c.strip() for c in a.colors.split(",")]
        bad = 0
        for kind in CVD:
            sims = [simulate(hex2rgb(c), kind) for c in cs]
            print(f"{kind}: " + "  ".join(f"{c}->{rgb2hex(s)}" for c, s in zip(cs, sims)))
            for i in range(len(cs)):
                for j in range(i + 1, len(cs)):
                    if dist(hex2rgb(cs[i]), hex2rgb(cs[j])) >= a.min_distance > dist(sims[i], sims[j]):
                        bad += 1
                        print(f"  COLLAPSE {cs[i]} vs {cs[j]}: {dist(sims[i], sims[j]):.3f} apart for {kind} (add a shape, label or lightness gap)")
        print("cvd: OK" if not bad else f"cvd: {bad} pair(s) collapse; never let color be the only signal")
    elif a.cmd == "check":
        r = ratio(hex2rgb(a.fg), hex2rgb(a.bg)); print(f"{a.fg} on {a.bg}: {r:.2f}:1  {verdict(r)}")
    else:
        cs = [c.strip() for c in a.colors.split(",")]
        print("fg \\ bg      " + "  ".join(f"{c:>9}" for c in cs))
        for f in cs:
            print(f"{f:>9}    " + "  ".join(("    -    " if f == b else f"{ratio(hex2rgb(f), hex2rgb(b)):5.2f} {verdict(ratio(hex2rgb(f), hex2rgb(b)))[:4]:4}") for b in cs))

if __name__ == "__main__":
    main()
