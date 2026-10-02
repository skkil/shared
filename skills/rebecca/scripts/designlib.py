"""Shared helpers for the lead-designer scripts.

Everything the skill produces lives in one workspace folder (default ./.design) so assets,
plans, spend and design decisions survive across sessions and get reused, not regenerated.

    .design/
      DESIGN.md            durable design decisions (tokens, voice, direction contract)
      budget.json          {"cap_usd": 25.0, "per_plan_cap_usd": 5.0}
      ledger.jsonl         every paid call, append-only
      library.json         every asset (generated, derived, imported) with provenance
      plans/PLAN-*.json    generation plans, awaiting or after approval
      assets/              files on disk
      review/              screenshots, contact sheets, critic reports
      roll-history.jsonl   creative rolls already used (avoid repeating directions)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

LIB_VERSION = 1


def root(explicit: str | None = None) -> Path:
    """Resolve the workspace. Order: --root flag, $DESIGN_ROOT, ./.design."""
    base = explicit or os.environ.get("DESIGN_ROOT")
    p = Path(base) if base else Path.cwd() / ".design"
    for sub in ("plans", "assets", "review"):
        (p / sub).mkdir(parents=True, exist_ok=True)
    return p


def load_env(r: Path) -> None:
    """Load KEY=VALUE pairs from env files near the workspace. Never prints values.
    Existing environment variables win."""
    for f in [r / ".env", r.parent / ".env.design", r.parent / ".env.agents", r.parent / ".env"]:
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            if k.startswith("export "):
                k = k[len("export "):].strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ library

def lib_path(r: Path) -> Path:
    return r / "library.json"


def lib_load(r: Path) -> dict:
    p = lib_path(r)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"version": LIB_VERSION, "assets": []}


def lib_save(r: Path, lib: dict) -> None:
    tmp = lib_path(r).with_suffix(".tmp")
    tmp.write_text(json.dumps(lib, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(lib_path(r))


def next_asset_id(lib: dict) -> str:
    n = 1 + max([int(a["id"].split("-")[1]) for a in lib["assets"]] or [0])
    return f"A-{n:04d}"


def register(r: Path, file: Path, *, kind: str, source: str, prompt: str = "", model: str = "",
             params: dict | None = None, cost_usd: float = 0.0, tags: list[str] | None = None,
             plan_id: str = "", job_id: str = "", derived_from: list[str] | None = None,
             op: str = "", rating: str = "unrated", notes: str = "") -> dict:
    """Add a file to the asset library and return its record (idempotent per file+content)."""
    lib = lib_load(r)
    file = Path(file)
    rel = os.path.relpath(file.resolve(), r.resolve())
    digest = sha256_file(file)
    for a in lib["assets"]:
        if a.get("file") == rel and a.get("sha256") == digest:
            return a
    rec = {
        "id": next_asset_id(lib),
        "file": rel,
        "kind": kind,              # image | sprite | animation | model3d | video | audio | other
        "source": source,          # fal | retrodiffusion | derived | user | stock | code
        "model": model,
        "prompt": prompt,
        "params": params or {},
        "cost_usd": round(float(cost_usd), 4),
        "tags": sorted(set(tags or [])),
        "plan_id": plan_id,
        "job_id": job_id,
        "derived_from": derived_from or [],
        "op": op,
        "rating": rating,          # unrated | keep | salvage | reject
        "notes": notes,
        "created": now(),
        "sha256": digest,
    }
    lib["assets"].append(rec)
    lib_save(r, lib)
    return rec


def find_asset(r: Path, ref: str) -> tuple[dict | None, Path]:
    """Resolve an asset id (A-0001) or a file path to (record|None, absolute path)."""
    lib = lib_load(r)
    for a in lib["assets"]:
        if a["id"] == ref:
            return a, r / a["file"]
    p = Path(ref)
    if not p.is_absolute():
        p = Path.cwd() / p
    for a in lib["assets"]:
        if (r / a["file"]).resolve() == p.resolve():
            return a, p
    return None, p


def search(r: Path, words: list[str], tags: list[str] | None = None) -> list[dict]:
    """Rank assets by overlap with words/tags. Rejected assets are still returned (flagged):
    a failed generation is often salvageable with post-processing."""
    lib = lib_load(r)
    words = [w.lower() for w in words if len(w) > 2]
    tags = [t.lower() for t in (tags or [])]
    scored = []
    for a in lib["assets"]:
        hay = " ".join([a.get("prompt", ""), " ".join(a.get("tags", [])), a.get("notes", ""),
                        a.get("model", "")]).lower()
        score = sum(1 for w in words if w in hay) + 2 * sum(1 for t in tags if t in a.get("tags", []))
        if a.get("rating") == "keep":
            score += 1
        if score > 0:
            scored.append((score, a))
    scored.sort(key=lambda x: -x[0])
    return [a for _, a in scored]


# -------------------------------------------------------------------- spend

def budget(r: Path) -> dict:
    p = r / "budget.json"
    if p.exists():
        return json.loads(p.read_text())
    return {"cap_usd": None, "per_plan_cap_usd": None}


def ledger_total(r: Path) -> float:
    p = r / "ledger.jsonl"
    if not p.exists():
        return 0.0
    tot = 0.0
    for line in p.read_text().splitlines():
        try:
            tot += float(json.loads(line).get("cost_usd", 0) or 0)
        except Exception:
            pass
    return round(tot, 4)


def ledger_append(r: Path, entry: dict) -> None:
    with open(r / "ledger.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": now(), **entry}, ensure_ascii=False) + "\n")


def die(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)
