#!/usr/bin/env python3
"""capture: screenshots for the critic loop (desktop + mobile, full page, settled motion).

  python scripts/capture.py http://localhost:5173 [--out .design/review] [--widths 1440,390] [--wait 1200]
  python scripts/capture.py file:///abs/path/index.html --frames 0,400,1200   # motion keyframes of the first viewport

Uses Python Playwright if installed, else `npx playwright screenshot`. Install once with:
  pip install playwright && python -m playwright install chromium     (or: npx playwright install chromium)
Captures are evidence only if valid: open each file and confirm it shows what its name claims
(no blank regions, no half-loaded fonts, no element hidden mid-animation).
"""
import argparse, shutil, subprocess, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url"); ap.add_argument("--out", default=".design/review")
    ap.add_argument("--widths", default="1440,390"); ap.add_argument("--wait", type=int, default=1200)
    ap.add_argument("--frames", help="ms offsets for first-viewport motion frames, e.g. 0,300,900")
    ap.add_argument("--reduced-motion", action="store_true")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    widths = [int(w) for w in a.widths.split(",")]
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        if not shutil.which("npx"):
            sys.exit("Playwright not available. pip install playwright && python -m playwright install chromium")
        for w in widths:
            h = 900 if w > 700 else 844
            f = out / f"{'desktop' if w > 700 else 'mobile'}-{w}.png"
            subprocess.run(["npx", "-y", "playwright", "screenshot", "--full-page", f"--viewport-size={w},{h}",
                            f"--wait-for-timeout={a.wait}", a.url, str(f)], check=False)
            print(f)
        return
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w in widths:
            h = 900 if w > 700 else 844
            ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2 if w <= 700 else 1,
                                reduced_motion="reduce" if a.reduced_motion else "no-preference")
            pg = ctx.new_page()
            pg.goto(a.url, wait_until="networkidle")
            tag = ("desktop" if w > 700 else "mobile") + f"-{w}" + ("-rm" if a.reduced_motion else "")
            if a.frames:
                for t in [int(x) for x in a.frames.split(",")]:
                    pg.reload(wait_until="domcontentloaded"); pg.wait_for_timeout(t)
                    f = out / f"{tag}-t{t}.png"; pg.screenshot(path=str(f)); print(f)
            pg.wait_for_timeout(a.wait)
            pg.evaluate("document.fonts && document.fonts.ready")
            f = out / f"{tag}.png"; pg.screenshot(path=str(f), full_page=True); print(f)
            ctx.close()
        b.close()

if __name__ == "__main__":
    main()
