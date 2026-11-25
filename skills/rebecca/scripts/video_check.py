#!/usr/bin/env python3
"""video_check: verify an exported video before anyone sees it. Free; needs ffmpeg + ffprobe.

  python scripts/video_check.py out/launch.mp4                         # encode report: codec, pix_fmt, fps, faststart, audio
  python scripts/video_check.py out/loop.mp4 --loop                    # first and last frame must match for a seamless loop
  python scripts/video_check.py out/reel.mp4 --sheet 8                 # contact sheet of 8 evenly spaced frames to look at
  python scripts/video_check.py out/reel.mp4 --safe reels --at 4.5     # frame with platform safe-zone overlay
  python scripts/video_check.py in.mov --encode out/final.mp4          # web/social-safe H.264 re-encode, then check it

Delivery target: H.264 high, yuv420p, BT.709 tags, +faststart, AAC 128k (a silent track if there is no sound;
some platforms reject video without audio). Exit 1 if a required check fails.
"""
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path

SAFE = {
    "reels": {"size": (1080, 1920), "keep": (60, 360, 900, 1060), "note": "Instagram Reels/TikTok: keep content in y 360-1420; UI covers the bottom 500px and right 120px"},
    "shorts": {"size": (1080, 1920), "keep": (60, 290, 900, 1080), "note": "YouTube Shorts: title/buttons cover bottom ~550px and right ~120px"},
    "story": {"size": (1080, 1920), "keep": (60, 250, 960, 1420), "note": "Stories: keep 250px clear top and bottom"},
    "feed45": {"size": (1080, 1350), "keep": (60, 60, 960, 1230), "note": "4:5 feed post: 60px margins"},
    "landscape": {"size": (1920, 1080), "keep": (96, 54, 1728, 972), "note": "16:9: title-safe 90%"},
}


def need(tool):
    if not shutil.which(tool):
        sys.exit(f"{tool} not found on PATH")


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr.strip())
    return json.loads(r.stdout)


def faststart(path):
    with open(path, "rb") as f:
        head = f.read(1 << 16)
    m, d = head.find(b"moov"), head.find(b"mdat")
    return m != -1 and (d == -1 or m < d)


def frame(path, t, dest):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1", str(dest)], check=True)
    return dest


def report(path):
    info = probe(path)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"].get("duration", 0))
    checks = []
    if not v:
        return dur, [("video stream", False, "none")]
    num, den = (int(x) for x in v.get("avg_frame_rate", "0/1").split("/"))
    fps = num / den if den else 0
    checks.append(("codec h264", v.get("codec_name") == "h264", v.get("codec_name")))
    checks.append(("pix_fmt yuv420p", v.get("pix_fmt") == "yuv420p", v.get("pix_fmt")))
    checks.append(("even dimensions", v["width"] % 2 == 0 and v["height"] % 2 == 0, f"{v['width']}x{v['height']}"))
    checks.append(("bt709 tagged", v.get("color_primaries") == "bt709" or v.get("color_space") == "bt709", v.get("color_primaries", "untagged")))
    checks.append(("faststart", faststart(path) if path.suffix.lower() in (".mp4", ".m4v", ".mov") else True, "moov before mdat"))
    checks.append(("audio track", a is not None, a.get("codec_name") if a else "none"))
    checks.append(("fps 24-60", 23.9 <= fps <= 60.1, f"{fps:.2f}"))
    return dur, checks


def encode(src, dst):
    has_audio = any(s["codec_type"] == "audio" for s in probe(src)["streams"])
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src)]
    if not has_audio:
        cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", "-shortest"]
    cmd += ["-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-color_range", "tv", "-colorspace", "bt709",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst)]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--loop-tolerance", type=float, default=2.0, help="mean abs pixel difference (0-255) allowed")
    ap.add_argument("--sheet", type=int)
    ap.add_argument("--safe", choices=list(SAFE))
    ap.add_argument("--at", type=float)
    ap.add_argument("--encode")
    ap.add_argument("--out", default=".design/review")
    a = ap.parse_args()
    need("ffmpeg"); need("ffprobe")
    path = Path(a.video)
    if a.encode:
        encode(path, Path(a.encode)); path = Path(a.encode); print(f"encoded: {path}")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    dur, checks = report(path)
    failed = False
    print(f"{path}  {dur:.2f}s")
    for name, ok, val in checks:
        print(f"  {'ok  ' if ok else 'FAIL'} {name:16} {val}")
        failed |= not ok
    from PIL import Image, ImageChops, ImageDraw, ImageStat
    with tempfile.TemporaryDirectory() as td:
        if a.loop:
            info = probe(path)
            v = next(s for s in info["streams"] if s["codec_type"] == "video")
            n, d = (int(x) for x in v["avg_frame_rate"].split("/"))
            last = max(0.0, dur - (d / n if n else 0.04) * 1.5)
            f0 = Image.open(frame(path, 0, Path(td) / "a.png")).convert("RGB")
            f1 = Image.open(frame(path, last, Path(td) / "b.png")).convert("RGB")
            diff = sum(ImageStat.Stat(ImageChops.difference(f0, f1)).mean) / 3
            ok = diff <= a.loop_tolerance
            failed |= not ok
            print(f"  {'ok  ' if ok else 'FAIL'} loop seam       first vs last frame differ by {diff:.2f} (<= {a.loop_tolerance})")
        if a.sheet:
            ts = [dur * (i + 0.5) / a.sheet for i in range(a.sheet)]
            ims = [Image.open(frame(path, t, Path(td) / f"s{i}.png")).convert("RGB") for i, t in enumerate(ts)]
            tw = 360; th = int(ims[0].height * tw / ims[0].width)
            cols = min(4, len(ims)); rows = -(-len(ims) // cols)
            sheet = Image.new("RGB", (cols * tw, rows * (th + 20)), (250, 250, 248))
            dr = ImageDraw.Draw(sheet)
            for i, (im, t) in enumerate(zip(ims, ts)):
                x, y = (i % cols) * tw, (i // cols) * (th + 20)
                sheet.paste(im.resize((tw, th)), (x, y + 20)); dr.text((x + 6, y + 4), f"{t:.2f}s", fill=(30, 30, 30))
            dest = out / f"{path.stem}-sheet.png"; sheet.save(dest)
            print(f"  sheet: {dest}  (check every frame: cut-off text, overlaps, text unreadable at phone size)")
        if a.safe:
            z = SAFE[a.safe]
            im = Image.open(frame(path, a.at if a.at is not None else dur / 2, Path(td) / "z.png")).convert("RGBA")
            sx, sy = im.width / z["size"][0], im.height / z["size"][1]
            x, y, w, h = z["keep"]
            shade = Image.new("RGBA", im.size, (255, 0, 80, 90))
            ImageDraw.Draw(shade).rectangle([x * sx, y * sy, (x + w) * sx, (y + h) * sy], fill=(0, 0, 0, 0))
            dest = out / f"{path.stem}-safe-{a.safe}.png"
            Image.alpha_composite(im, shade).convert("RGB").save(dest)
            print(f"  safe zone: {dest}  ({z['note']}; nothing important in the tinted area)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
