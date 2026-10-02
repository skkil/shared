#!/usr/bin/env python3
"""Jennifer's memory and research library.

  python research_lib.py init                       scaffold .jennifer/ (or $JENNIFER_HOME) with config and folders
  python research_lib.py add FILE --product sync --tags pricing,competitors [--stale-days 90] [--title T]
  python research_lib.py list [--tag pricing] [--product sync]
  python research_lib.py stale                       items past their staleness horizon
  python research_lib.py touch FILE                  mark an item refreshed today
The index lives in <home>/research/index.json; paths are stored relative to <home> when possible.
"""
import argparse, datetime, json, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(HERE, "..", "assets", "templates")


def home():
    return os.environ.get("JENNIFER_HOME") or os.path.join(os.getcwd(), ".jennifer")


def index_path():
    return os.path.join(home(), "research", "index.json")


def load():
    try:
        return json.load(open(index_path(), encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"items": []}


def save(idx):
    os.makedirs(os.path.dirname(index_path()), exist_ok=True)
    json.dump(idx, open(index_path(), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def rel(p):
    p = os.path.abspath(p)
    h = os.path.abspath(home())
    return os.path.relpath(p, h) if p.startswith(h) else p


def title_of(path):
    try:
        for line in open(path, encoding="utf-8"):
            if line.startswith("#"):
                return line.lstrip("#").strip()
    except FileNotFoundError:
        pass
    return os.path.basename(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["init", "add", "list", "stale", "touch"])
    ap.add_argument("file", nargs="?")
    ap.add_argument("--product", default=""); ap.add_argument("--tags", default=""); ap.add_argument("--tag")
    ap.add_argument("--stale-days", type=int, default=90); ap.add_argument("--title")
    a = ap.parse_intermixed_args()
    today = datetime.date.today()
    if a.cmd == "init":
        h = home()
        for d in ("products", "research", "domains", "interviews", "ideas", "decisions"):
            os.makedirs(os.path.join(h, d), exist_ok=True)
        cfg = os.path.join(h, "config.md")
        if not os.path.exists(cfg):
            shutil.copy(os.path.join(TEMPLATES, "config.md"), cfg)
        j = os.path.join(h, "ideas", "journal.md")
        if not os.path.exists(j):
            open(j, "w", encoding="utf-8").write("# Idea journal\n\n| Date | Idea | Origin (lens / far domain) | Product | Fate | Reason |\n|---|---|---|---|---|---|\n")
        if not os.path.exists(index_path()):
            save({"items": []})
        print(f"Initialized {h}. Next: fill config.md, then create products/<name>/PRODUCT.md from assets/templates/PRODUCT.md.")
        return
    idx = load()
    if a.cmd == "add":
        if not a.file:
            raise SystemExit("add needs FILE")
        r = rel(a.file)
        idx["items"] = [i for i in idx["items"] if i["path"] != r]
        idx["items"].append({"path": r, "title": a.title or title_of(a.file), "product": a.product,
                             "tags": [t.strip() for t in a.tags.split(",") if t.strip()],
                             "added": today.isoformat(), "refreshed": today.isoformat(), "stale_days": a.stale_days})
        save(idx)
        print(f"Indexed {r} (stale after {a.stale_days} days)")
    elif a.cmd == "touch":
        r = rel(a.file)
        for i in idx["items"]:
            if i["path"] == r:
                i["refreshed"] = today.isoformat()
        save(idx)
        print(f"Refreshed {r}")
    else:
        rows = []
        for i in idx["items"]:
            age = (today - datetime.date.fromisoformat(i["refreshed"])).days
            due = age - i["stale_days"]
            if a.tag and a.tag not in i["tags"]:
                continue
            if a.product and i["product"] != a.product:
                continue
            if a.cmd == "stale" and due <= 0:
                continue
            rows.append((due, i, age))
        if not rows:
            print("Nothing stale." if a.cmd == "stale" else "No items.")
            return
        print("| Title | Product | Tags | Refreshed | Age (days) | Status | Path |\n|---|---|---|---|---|---|---|")
        for due, i, age in sorted(rows, key=lambda x: -x[0]):
            status = f"STALE by {due}d" if due > 0 else f"fresh ({-due}d left)"
            print(f"| {i['title']} | {i['product']} | {', '.join(i['tags'])} | {i['refreshed']} | {age} | {status} | {i['path']} |")


if __name__ == "__main__":
    main()
