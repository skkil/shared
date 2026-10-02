#!/usr/bin/env python3
"""Cost-gated media generation for fal.ai and Retro Diffusion.

Only `run` spends money, and it refuses unless ALL of these hold:
  1. the plan file exists and is byte-for-byte what was shown to the user (hash check);
  2. the approval code printed by `plan` is passed back with --approve;
  3. --user-said carries the user's own approving words (written to the ledger);
  4. every job has a cost estimate (unknown prices must be read via `schema` and filled in);
  5. the estimate fits the per-plan cap and the remaining total budget.

Free commands (never spend):  status, budget, schema, rd-balance, plan, show, ledger
Paid command:                 run

Spec format (JSON) for `plan`:
{
  "purpose": "Landing page hero + mascot pose sheet",
  "jobs": [
    {"id": "hero-draft", "provider": "fal", "endpoint": "openai/gpt-image-2",
     "why": "3 cheap drafts to pick a composition",
     "tags": ["hero", "mascot", "draft"],
     "input": {"prompt": "...", "image_size": "landscape_16_9", "quality": "low", "num_images": 3}},
    {"id": "walk-cycle", "provider": "retrodiffusion", "endpoint": "inferences",
     "input": {"prompt_style": "rd_advanced_animation__walking", "width": 64, "height": 64,
               "num_images": 1, "input_image": "asset:A-0007", "return_spritesheet": true}},
    {"id": "mascot-3d", "provider": "retrodiffusion", "endpoint": "lowpoly/generate",
     "input": {"prompt": "...", "size": "auto"}, "exports": ["web"]},
    {"id": "glass-loop", "provider": "fal", "endpoint": "fal-ai/kling-video/v3/pro/image-to-video",
     "input": {"prompt": "...", "image_url": "asset:A-0012", "duration": "5"},
     "est_cost_usd": 0.70, "est_source": "schema pricing: $0.14/s x 5s"}
  ]
}
File inputs: "asset:A-0007" (library id) or "file:relative/or/abs/path.png" are converted to
data URIs for fal and to raw base64 RGB for Retro Diffusion.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import designlib as dl  # noqa: E402

FAL_QUEUE = "https://queue.fal.run"
RD_API = "https://api.retrodiffusion.ai/v2"
DEFAULT_PER_PLAN_CAP = 3.00
UA = "lead-designer-skill/1.0"

# Conservative per-output estimates (USD). Prices change: `schema` prints live pricing.
# None => unknown => the plan cannot run until est_cost_usd is supplied from the live price.
FAL_TABLE = [
    (r"^openai/gpt-image-2(/edit)?$", "gpt_image"),
    (r"^fal-ai/nano-banana-2(/edit)?$", 0.08),
    (r"^fal-ai/nano-banana-pro(/edit)?$", 0.15),
    (r"^fal-ai/nano-banana(/edit)?$", 0.04),
    (r"^fal-ai/recraft", 0.05),
    (r"^fal-ai/flux-2-pro", 0.05),
    (r"^fal-ai/flux-pro/kontext", 0.04),
    (r"^fal-ai/flux/dev", 0.03),
    (r"^fal-ai/flux/schnell", 0.005),
    (r"^fal-ai/bytedance/seedream", 0.04),
    (r"^fal-ai/ideogram", 0.06),
    (r"^fal-ai/z-image", 0.01),
    (r"^fal-ai/(bria/background|birefnet|imageutils/rembg)", 0.02),
    (r"^fal-ai/(clarity-upscaler|topaz|recraft/upscale|esrgan|aura-sr)", 0.10),
    (r"^fal-ai/trellis-2$", 0.30),
    (r"^fal-ai/trellis(/multi)?$", 0.03),
    (r"^fal-ai/hunyuan3d/v2", 0.16),
]
GPT_IMAGE_PER_MP = {"low": 0.012, "medium": 0.06, "high": 0.22, "auto": 0.22}
SIZE_PRESETS = {"square_hd": (1024, 1024), "square": (512, 512), "portrait_4_3": (768, 1024),
                "portrait_16_9": (576, 1024), "landscape_4_3": (1024, 768),
                "landscape_16_9": (1024, 576), "auto": (1024, 1024)}
RD_TABLE = {"rd_pro": 0.18, "rd_plus": 0.06, "rd_fast": 0.03, "rd_mini": 0.03,
            "rd_advanced_animation": 0.25, "rd_animation": 0.25}
RD_LOWPOLY = {16: 0.25, 32: 0.50, 64: 0.85, 128: 1.20, 256: 3.00, "auto": 1.20}


# ----------------------------------------------------------------- http utils

def http_json(method: str, url: str, headers: dict, body=None, timeout: int = 120):
    data = json.dumps(body).encode() if body is not None else None
    h = {"User-Agent": UA, **headers}
    if body is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:800]
        raise RuntimeError(f"HTTP {e.code} from {url.split('?')[0]}: {detail}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Network error reaching {url.split('/')[2]}: {e.reason}. In a sandbox with a domain "
            "allowlist (e.g. Claude Chat), API calls are blocked: use the provider's MCP connector, "
            "or run this command on your own machine / in Claude Code.") from None


def http_text(url: str, timeout: int = 60) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def download(url: str, dest_noext: Path, content_type: str | None = None) -> Path:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = resp.read()
        ctype = content_type or resp.headers.get("Content-Type", "")
    ext = Path(urllib.parse.urlparse(url).path).suffix if "." in url.split("/")[-1] else ""
    if not ext:
        ext = mimetypes.guess_extension((ctype or "").split(";")[0].strip()) or ".bin"
    out = dest_noext.with_suffix(ext)
    out.write_bytes(data)
    return out


def sniff_ext(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return ".bin"


KIND_BY_EXT = {".png": "image", ".jpg": "image", ".jpeg": "image", ".webp": "image", ".gif": "animation",
               ".glb": "model3d", ".gltf": "model3d", ".obj": "model3d", ".zip": "other",
               ".mp4": "video", ".webm": "video", ".mov": "video", ".wav": "audio", ".mp3": "audio"}


# ------------------------------------------------------------ input handling

def _resolve_file(r: Path, ref: str) -> Path:
    if ref.startswith("asset:"):
        rec, p = dl.find_asset(r, ref.split(":", 1)[1])
        if not rec:
            dl.die(f"unknown asset {ref}")
        return p
    p = Path(ref.split(":", 1)[1])
    return p if p.is_absolute() else Path.cwd() / p


def materialize(r: Path, value, provider: str):
    """Replace asset:/file: references with data the provider accepts."""
    if isinstance(value, dict):
        return {k: materialize(r, v, provider) for k, v in value.items()}
    if isinstance(value, list):
        return [materialize(r, v, provider) for v in value]
    if isinstance(value, str) and (value.startswith("asset:") or value.startswith("file:")):
        p = _resolve_file(r, value)
        if provider == "retrodiffusion":
            from PIL import Image  # RD wants raw base64, RGB, no transparency
            im = Image.open(p)
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                bg = Image.new("RGB", im.size, (255, 255, 255))
                bg.paste(im, mask=im.split()[-1])
                im = bg
            buf = io.BytesIO()
            im.convert("RGB").save(buf, "PNG")
            return base64.b64encode(buf.getvalue()).decode()
        mime = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"
    return value


def strip_payload_for_display(value):
    if isinstance(value, dict):
        return {k: strip_payload_for_display(v) for k, v in value.items()}
    if isinstance(value, list):
        return [strip_payload_for_display(v) for v in value]
    if isinstance(value, str) and len(value) > 300:
        return value[:280] + f"...[{len(value)} chars]"
    return value


# --------------------------------------------------------------- estimation

def _megapixels(inp: dict) -> float:
    size = inp.get("image_size", "landscape_4_3")
    if isinstance(size, dict):
        w, h = size.get("width", 1024), size.get("height", 1024)
    else:
        w, h = SIZE_PRESETS.get(str(size), (1024, 1024))
    return (w * h) / 1_000_000


def estimate_fal(job: dict) -> tuple[float | None, str]:
    ep, inp = job["endpoint"], job.get("input", {})
    n = int(inp.get("num_images", 1) or 1)
    for pat, price in FAL_TABLE:
        if re.search(pat, ep):
            if price == "gpt_image":
                q = str(inp.get("quality", "high"))
                mp = max(0.6, _megapixels(inp))
                per = GPT_IMAGE_PER_MP.get(q, 0.22) * mp
                if ep.endswith("/edit"):
                    per += 0.01 * max(1, len(inp.get("image_urls", [])) or 1)
                return round(per * n, 3), f"table≈ gpt-image {q} {mp:.2f}MP x{n}"
            return round(price * n, 3), f"table≈ ${price}/output x{n}"
    return None, "UNKNOWN: run `media.py schema " + ep + "` and set est_cost_usd"


def estimate_rd(r: Path, job: dict, live: bool) -> tuple[float | None, str]:
    ep, inp = job["endpoint"], dict(job.get("input", {}))
    key = os.environ.get("RD_API_KEY")
    if live and key:
        try:
            hdr = {"X-RD-Token": key}
            if ep == "inferences":
                body = materialize(r, {**inp, "check_cost": True}, "retrodiffusion")
                res = http_json("POST", f"{RD_API}/inferences", hdr, body, timeout=60)
                if "task_id" in res and "balance_cost" not in res:
                    res = _rd_poll(f"{RD_API}/inferences/tasks/{res['task_id']}", hdr, 2, 60).get("result", {})
                if "balance_cost" in res:
                    return float(res["balance_cost"]), "rd check_cost (exact, free)"
            elif ep == "lowpoly/generate":
                res = http_json("POST", f"{RD_API}/lowpoly/estimate", hdr,
                                {"operation": "generate", "prompt": inp.get("prompt", ""),
                                 "size": inp.get("size", "auto"), **({"style": inp["style"]} if "style" in inp else {})})
                if "cost" in res:
                    return float(res["cost"]), f"rd estimate (exact, free) size={res.get('size')}"
        except Exception as e:  # fall back to table
            print(f"  (live estimate failed for {job['id']}: {e})", file=sys.stderr)
    if ep == "inferences":
        style = str(inp.get("prompt_style", "rd_plus__default"))
        fam = style.split("__")[0]
        per = RD_TABLE.get(fam, 0.18)
        n = int(inp.get("num_images", 1) or 1)
        return round(per * n, 3), f"table≈ {fam} ${per} x{n}"
    if ep.startswith("lowpoly/"):
        size = inp.get("size", "auto")
        base = RD_LOWPOLY.get(size if size == "auto" else int(size), 1.20)
        if "animate" in ep:
            base = round(base * 0.45, 2)
        if "revise" in ep:
            base = round(base * 0.75, 2)
        return base, f"table≈ lowpoly size={size}"
    return None, "UNKNOWN Retro Diffusion endpoint: set est_cost_usd"


# ------------------------------------------------------------------- plan

def cmd_plan(args, r: Path):
    spec = json.loads(Path(args.spec).read_text())
    jobs = spec.get("jobs") or dl.die("spec has no jobs")
    seen = set()
    rows = []
    total, unknown = 0.0, []
    for j in jobs:
        for k in ("id", "provider", "endpoint", "input"):
            if k not in j:
                dl.die(f"job missing '{k}': {j}")
        if j["id"] in seen:
            dl.die(f"duplicate job id {j['id']}")
        seen.add(j["id"])
        if j["provider"] not in ("fal", "retrodiffusion"):
            dl.die(f"provider must be fal or retrodiffusion: {j['id']}")
        if "est_cost_usd" in j and j["est_cost_usd"] is not None:
            est, src = float(j["est_cost_usd"]), "manual: " + j.get("est_source", "from live pricing")
        elif j["provider"] == "fal":
            est, src = estimate_fal(j)
        else:
            est, src = estimate_rd(r, j, live=not args.offline)
        j["est_cost_usd"], j["est_source"] = est, src
        j.setdefault("idempotency_key", str(uuid.uuid4()))
        if est is None:
            unknown.append(j["id"])
        else:
            total += est
        words = re.findall(r"[a-zA-Z]{4,}", json.dumps(j.get("input", {}).get("prompt", "")))
        reuse = dl.search(r, words[:25], j.get("tags"))[:4]
        j["reuse_candidates"] = [f"{a['id']}({a.get('rating')})" for a in reuse]
        rows.append(j)

    plan_id = "PLAN-" + time.strftime("%Y%m%d-%H%M%S")
    body = {"plan_id": plan_id, "purpose": spec.get("purpose", ""), "jobs": rows,
            "est_total_usd": round(total, 3), "unknown_cost_jobs": unknown,
            "status": "awaiting_approval", "created": dl.now()}
    canon = json.dumps({"jobs": rows, "purpose": body["purpose"]}, sort_keys=True)
    body["plan_hash"] = dl.sha_text(canon)
    body["approval_code"] = "go-" + body["plan_hash"][:6]
    (r / "plans" / f"{plan_id}.json").write_text(json.dumps(body, indent=2))
    print_plan(r, body)


def print_plan(r: Path, plan: dict):
    b = dl.budget(r)
    spent = dl.ledger_total(r)
    cap = b.get("cap_usd")
    per = b.get("per_plan_cap_usd") or DEFAULT_PER_PLAN_CAP
    print(f"\n## Generation plan {plan['plan_id']}  ({plan['status']})")
    if plan.get("purpose"):
        print(f"Purpose: {plan['purpose']}")
    print("\n| job | provider / model | what | outputs | est. cost | estimate source | reuse candidates |")
    print("|---|---|---|---|---|---|---|")
    for j in plan["jobs"]:
        inp = j.get("input", {})
        what = (j.get("why") or str(inp.get("prompt", ""))[:90]).replace("|", "/").replace("\n", " ")
        n = inp.get("num_images", 1)
        size = inp.get("image_size") or (f"{inp.get('width')}x{inp.get('height')}" if inp.get("width") else inp.get("size", ""))
        if isinstance(size, dict):
            size = f"{size.get('width')}x{size.get('height')}"
        est = "UNKNOWN" if j["est_cost_usd"] is None else f"${j['est_cost_usd']:.3f}"
        reuse = ", ".join(j.get("reuse_candidates") or []) or "none"
        print(f"| {j['id']} | {j['provider']} / {j['endpoint']} | {what} | {n} @ {size} | {est} | {j['est_source']} | {reuse} |")
    print(f"\nEstimated total: ${plan['est_total_usd']:.3f}   (spent so far: ${spent:.2f}"
          + (f" of ${cap:.2f} budget" if cap else ", no total budget set") + f"; per-plan cap ${per:.2f})")
    problems = []
    if plan.get("unknown_cost_jobs"):
        problems.append("unknown prices for: " + ", ".join(plan["unknown_cost_jobs"]))
    if plan["est_total_usd"] > per:
        problems.append(f"over per-plan cap (${per:.2f}); split the plan or ask the user to raise it")
    if cap is not None and spent + plan["est_total_usd"] > cap:
        problems.append(f"would exceed total budget (${cap:.2f})")
    if problems:
        print("\nBLOCKED: " + "; ".join(problems))
    else:
        print(f"\nApproval code: {plan['approval_code']}")
        print("Show this table to the user and wait for an explicit yes. Then run:")
        print(f"  python scripts/media.py run {plan['plan_id']} --approve {plan['approval_code']} "
              "--user-said \"<the user's approving words>\"")
    print("Prompts/params (truncated):")
    for j in plan["jobs"]:
        print(f"- {j['id']}: {json.dumps(strip_payload_for_display(j.get('input', {})), ensure_ascii=False)[:700]}")


def load_plan(r: Path, plan_id: str) -> tuple[dict, Path]:
    p = r / "plans" / f"{plan_id}.json"
    if not p.exists():
        dl.die(f"no such plan {plan_id}")
    return json.loads(p.read_text()), p


# -------------------------------------------------------------------- run

def _rd_poll(url: str, hdr: dict, every: int, max_wait: int) -> dict:
    t0 = time.time()
    while True:
        task = http_json("GET", url, hdr)
        st = task.get("status")
        if st == "succeeded":
            return task
        if st == "failed":
            raise RuntimeError(f"Retro Diffusion task failed (refunded): {task.get('error')}")
        if time.time() - t0 > max_wait:
            raise RuntimeError(f"timed out waiting for {url}; poll later, task may still finish")
        time.sleep(every)


def run_fal(r: Path, plan: dict, job: dict, outdir: Path) -> tuple[list[Path], float, str]:
    key = os.environ.get("FAL_KEY") or dl.die("FAL_KEY not set (put it in .env.design, never in code)")
    hdr = {"Authorization": f"Key {key}"}
    payload = materialize(r, job["input"], "fal")
    sub = http_json("POST", f"{FAL_QUEUE}/{job['endpoint']}", hdr, payload, timeout=180)
    status_url, response_url = sub.get("status_url"), sub.get("response_url")
    if not status_url:
        raise RuntimeError(f"unexpected fal submit response: {str(sub)[:300]}")
    t0, max_wait = time.time(), int(job.get("max_wait_s", 1500))
    while True:
        st = http_json("GET", status_url, hdr)
        if st.get("status") == "COMPLETED":
            break
        if time.time() - t0 > max_wait:
            raise RuntimeError(f"timeout; request {sub.get('request_id')} may still complete: {response_url}")
        time.sleep(3)
    result = http_json("GET", response_url, hdr, timeout=180)
    (outdir / f"{job['id']}.result.json").write_text(json.dumps(strip_payload_for_display(result), indent=2))
    urls = []

    def walk(x):
        if isinstance(x, dict):
            u = x.get("url")
            if isinstance(u, str) and u.startswith("http"):
                urls.append((u, x.get("content_type")))
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(result)
    files = [download(u, outdir / f"{job['id']}-{i + 1}", ct) for i, (u, ct) in enumerate(urls)]
    return files, float(job["est_cost_usd"] or 0), "estimated (fal bills per output; see dashboard)"


def run_rd(r: Path, plan: dict, job: dict, outdir: Path) -> tuple[list[Path], float, str]:
    key = os.environ.get("RD_API_KEY") or dl.die("RD_API_KEY not set (put it in .env.design)")
    hdr = {"X-RD-Token": key}
    ep = job["endpoint"]
    payload = materialize(r, job["input"], "retrodiffusion")
    paid = {**hdr, "Idempotency-Key": job["idempotency_key"]}  # same key on retry => never double-charged
    files: list[Path] = []
    if ep == "inferences":
        acc = http_json("POST", f"{RD_API}/inferences", paid, payload)
        task = _rd_poll(f"{RD_API}/inferences/tasks/{acc['task_id']}", hdr, 2, 900)
        res = task.get("result", {})
        for i, b64 in enumerate(res.get("base64_images", [])):
            data = base64.b64decode(b64)
            out = outdir / f"{job['id']}-{i + 1}{sniff_ext(data)}"
            out.write_bytes(data)
            files.append(out)
        for i, u in enumerate(res.get("output_urls", []) or []):
            files.append(download(u, outdir / f"{job['id']}-url{i + 1}"))
        return files, float(res.get("balance_cost", job["est_cost_usd"] or 0)), "actual (rd balance_cost)"
    if ep.startswith("lowpoly/"):
        acc = http_json("POST", f"{RD_API}/{ep}", paid, payload)
        task = _rd_poll(f"{RD_API}/lowpoly/tasks/{acc['task_id']}", hdr, 15, 1800)
        asset_id = (task.get("result") or {}).get("asset_id") or acc.get("asset_id")
        (outdir / f"{job['id']}.result.json").write_text(json.dumps(task, indent=2)[:20000])
        anim = task.get("animation")
        for target in job.get("exports", ["web"]):
            body = {"target": target}
            if target in ("mp4", "gif", "sheet") and anim:
                body["animation"] = anim
            ex = http_json("POST", f"{RD_API}/lowpoly/assets/{asset_id}/export", hdr, body, timeout=600)
            if ex.get("url"):
                files.append(download(ex["url"], outdir / f"{job['id']}-{target}", ex.get("content_type")))
        cost = float(acc.get("cost", job["est_cost_usd"] or 0))
        return files, cost, "actual (rd quoted cost)"
    raise RuntimeError(f"unsupported Retro Diffusion endpoint '{ep}'")


def cmd_run(args, r: Path):
    plan, path = load_plan(r, args.plan_id)
    canon = json.dumps({"jobs": plan["jobs"], "purpose": plan.get("purpose", "")}, sort_keys=True)
    if dl.sha_text(canon) != plan["plan_hash"]:
        dl.die("plan was modified after it was shown to the user. Re-run `plan` and get a fresh approval.")
    if plan["status"] not in ("awaiting_approval", "partial"):
        dl.die(f"plan status is '{plan['status']}', not runnable")
    if args.approve != plan["approval_code"]:
        dl.die("approval code mismatch. Show the plan to the user and wait for an explicit yes.")
    if not args.user_said or len(args.user_said.strip()) < 2:
        dl.die("--user-said must quote the user's approving message")
    if plan.get("unknown_cost_jobs"):
        dl.die("plan has unknown-cost jobs; fill est_cost_usd from live pricing and re-plan")
    b = dl.budget(r)
    per = b.get("per_plan_cap_usd") or DEFAULT_PER_PLAN_CAP
    jobs = [j for j in plan["jobs"] if not args.only or j["id"] in args.only.split(",")]
    jobs = [j for j in jobs if j["id"] not in plan.get("done_jobs", [])]
    est = sum(float(j["est_cost_usd"] or 0) for j in jobs)
    if est > per:
        dl.die(f"estimate ${est:.2f} exceeds per-plan cap ${per:.2f}")
    if b.get("cap_usd") is not None and dl.ledger_total(r) + est > b["cap_usd"]:
        dl.die(f"would exceed total budget ${b['cap_usd']:.2f}")
    outdir = r / "assets" / plan["plan_id"]
    outdir.mkdir(parents=True, exist_ok=True)
    plan.setdefault("done_jobs", [])
    failures = []
    for j in jobs:
        print(f"-> {j['id']} ({j['provider']} {j['endpoint']}) ...", flush=True)
        try:
            runner = run_fal if j["provider"] == "fal" else run_rd
            files, cost, cost_kind = runner(r, plan, j, outdir)
        except Exception as e:
            failures.append(j["id"])
            print(f"   FAILED: {e}")
            dl.ledger_append(r, {"plan_id": plan["plan_id"], "job": j["id"], "cost_usd": 0,
                                 "status": "failed", "error": str(e)[:500], "user_said": args.user_said})
            continue
        per_file = cost / max(1, len(files))
        ids = []
        for f in files:
            rec = dl.register(r, f, kind=KIND_BY_EXT.get(f.suffix.lower(), "other"), source=j["provider"],
                              prompt=str(j["input"].get("prompt", "")), model=j["endpoint"],
                              params=strip_payload_for_display({k: v for k, v in j["input"].items() if k != "prompt"}),
                              cost_usd=per_file, tags=j.get("tags", []), plan_id=plan["plan_id"], job_id=j["id"])
            ids.append(rec["id"])
        dl.ledger_append(r, {"plan_id": plan["plan_id"], "job": j["id"], "cost_usd": round(cost, 4),
                             "cost_kind": cost_kind, "status": "ok", "assets": ids, "user_said": args.user_said})
        plan["done_jobs"].append(j["id"])
        print(f"   ok: {', '.join(ids)}  (${cost:.3f}, {cost_kind})")
    plan["status"] = "done" if not failures and len(plan["done_jobs"]) == len(plan["jobs"]) else "partial"
    plan["approved_with"] = args.user_said
    path.write_text(json.dumps(plan, indent=2))
    print(f"\nPlan {plan['plan_id']}: {plan['status']}. Total spent to date: ${dl.ledger_total(r):.2f}")
    print("Next: review with `assets.py sheet --plan " + plan["plan_id"] + "`, then rate every output "
          "keep / salvage / reject. Nothing is deleted; salvage candidates feed post.py.")


# ------------------------------------------------------------ free commands

def cmd_status(args, r: Path):
    b = dl.budget(r)
    print(f"workspace: {r}")
    print(f"FAL_KEY: {'set' if os.environ.get('FAL_KEY') else 'missing'}   "
          f"RD_API_KEY: {'set' if os.environ.get('RD_API_KEY') else 'missing'}")
    print(f"budget: total cap {b.get('cap_usd')}, per-plan cap {b.get('per_plan_cap_usd') or DEFAULT_PER_PLAN_CAP} (default)")
    print(f"spent to date: ${dl.ledger_total(r):.2f}")
    lib = dl.lib_load(r)["assets"]
    by = {}
    for a in lib:
        by[a.get("rating", "unrated")] = by.get(a.get("rating", "unrated"), 0) + 1
    print(f"library: {len(lib)} assets {by}")
    pend = [p.stem for p in (r / "plans").glob("PLAN-*.json")
            if json.loads(p.read_text()).get("status") in ("awaiting_approval", "partial")]
    print(f"plans awaiting approval/partial: {pend or 'none'}")


def cmd_budget(args, r: Path):
    b = dl.budget(r)
    if args.cap is not None:
        b["cap_usd"] = args.cap
    if args.per_plan is not None:
        b["per_plan_cap_usd"] = args.per_plan
    (r / "budget.json").write_text(json.dumps(b, indent=2))
    print(json.dumps(b))


def cmd_schema(args, r: Path):
    url = f"https://fal.ai/models/{args.endpoint}/llms.txt"
    try:
        txt = http_text(url)
    except Exception as e:
        dl.die(f"could not fetch {url}: {e}")
    keep, on = [], False
    for line in txt.splitlines():
        if line.startswith("## Pricing") or line.startswith("### Input Schema") or line.startswith("### Output Schema"):
            on = True
        elif line.startswith("## Usage Examples") or line.startswith("## Additional Resources"):
            on = False
        if on:
            keep.append(line)
    print("\n".join(keep)[: args.max_chars] or txt[: args.max_chars])


def cmd_rd_balance(args, r: Path):
    key = os.environ.get("RD_API_KEY") or dl.die("RD_API_KEY not set")
    print(json.dumps(http_json("GET", f"{RD_API}/inferences/credits", {"X-RD-Token": key})))


def cmd_show(args, r: Path):
    plan, _ = load_plan(r, args.plan_id)
    print_plan(r, plan)


def cmd_ledger(args, r: Path):
    p = r / "ledger.jsonl"
    if not p.exists():
        print("no spend yet")
        return
    for line in p.read_text().splitlines()[-args.tail:]:
        e = json.loads(line)
        print(f"{e['ts']} {e.get('plan_id')} {e.get('job')} {e.get('status')} ${float(e.get('cost_usd') or 0):.3f} "
              f"{','.join(e.get('assets', []))}")
    print(f"TOTAL ${dl.ledger_total(r):.2f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="workspace folder (default ./.design or $DESIGN_ROOT)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("status")
    p = sp.add_parser("budget"); p.add_argument("--cap", type=float); p.add_argument("--per-plan", type=float)
    p = sp.add_parser("schema"); p.add_argument("endpoint"); p.add_argument("--max-chars", type=int, default=6000)
    sp.add_parser("rd-balance")
    p = sp.add_parser("plan"); p.add_argument("spec"); p.add_argument("--offline", action="store_true",
                                                                      help="skip free live RD price checks")
    p = sp.add_parser("show"); p.add_argument("plan_id")
    p = sp.add_parser("run"); p.add_argument("plan_id"); p.add_argument("--approve", required=True)
    p.add_argument("--user-said", required=True); p.add_argument("--only", help="comma-separated job ids")
    p = sp.add_parser("ledger"); p.add_argument("--tail", type=int, default=50)
    args = ap.parse_args()
    r = dl.root(args.root)
    dl.load_env(r)
    {"status": cmd_status, "budget": cmd_budget, "schema": cmd_schema, "rd-balance": cmd_rd_balance,
     "plan": cmd_plan, "show": cmd_show, "run": cmd_run, "ledger": cmd_ledger}[args.cmd](args, r)


if __name__ == "__main__":
    main()
