#!/usr/bin/env python3
"""Draw random ideation lenses and far domains, avoiding recently used ones.

Language models drift toward the same typical ideas; randomness from outside the model breaks the pattern.
  python lens_roll.py --n 4 --far 2 --product sync     4 lenses (distinct categories when possible) + 2 far domains
  python lens_roll.py --far 3 --only-far               far domains only
  python lens_roll.py --n 3 --category business,users  restrict lens categories
  python lens_roll.py --list                           show the decks
Options: --seed N (reproducible), --avoid-recent N (default 20 draws), --no-record, --history PATH.
History defaults to $JENNIFER_HOME/lens_history.json or ./.jennifer/lens_history.json.
"""
import argparse, datetime, json, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")


def history_path(arg):
    if arg:
        return arg
    home = os.environ.get("JENNIFER_HOME") or os.path.join(os.getcwd(), ".jennifer")
    return os.path.join(home, "lens_history.json")


def load_history(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"draws": []}


def recent_ids(hist, n):
    ids = []
    for d in reversed(hist["draws"]):
        ids.extend(d.get("lenses", []) + d.get("far", []))
        if len(ids) >= n:
            break
    return set(ids[:n])


def pick(pool, k, rnd, recent, key_cat=None):
    fresh = [x for x in pool if x["id"] not in recent]
    if len(fresh) < k:
        fresh = pool[:]
    rnd.shuffle(fresh)
    if not key_cat:
        return fresh[:k]
    chosen, cats = [], set()
    for x in fresh:
        if x[key_cat] not in cats:
            chosen.append(x); cats.add(x[key_cat])
        if len(chosen) == k:
            return chosen
    for x in fresh:
        if x not in chosen:
            chosen.append(x)
        if len(chosen) == k:
            break
    return chosen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--far", type=int, default=1)
    ap.add_argument("--only-far", action="store_true")
    ap.add_argument("--category")
    ap.add_argument("--product", default="")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--avoid-recent", type=int, default=20)
    ap.add_argument("--no-record", action="store_true")
    ap.add_argument("--history")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    lenses = json.load(open(os.path.join(ASSETS, "lens-deck.json"), encoding="utf-8"))["lenses"]
    far = json.load(open(os.path.join(ASSETS, "far-domains.json"), encoding="utf-8"))["domains"]
    if a.list:
        print("## Lenses")
        for l in lenses:
            print(f"- [{l['category']}] {l['name']} ({l['id']})")
        print("\n## Far domains")
        print(", ".join(d["name"] for d in far))
        return
    seed = a.seed if a.seed is not None else random.SystemRandom().randint(1, 10**9)
    rnd = random.Random(seed)
    hp = history_path(a.history)
    hist = load_history(hp)
    recent = recent_ids(hist, a.avoid_recent)
    if a.category:
        cats = {c.strip() for c in a.category.split(",")}
        lenses = [l for l in lenses if l["category"] in cats] or lenses
    got_l = [] if a.only_far else pick(lenses, a.n, rnd, recent, "category")
    got_f = pick(far, a.far, rnd, recent) if a.far else []
    print(f"# Lens roll (seed {seed}{', product ' + a.product if a.product else ''})\n")
    for l in got_l:
        print(f"## Lens: {l['name']}  [{l['category']}]\n{l['question']}\n")
    for d in got_f:
        print(f"## Far domain: {d['name']}\nPractices to mine for mechanisms: {'; '.join(d['practices'])}.\n"
              "Abstract the product problem first, find the mechanism behind a practice, map it, then translate for usability.\n")
    if not a.no_record:
        hist["draws"].append({"date": datetime.date.today().isoformat(), "product": a.product, "seed": seed,
                              "lenses": [l["id"] for l in got_l], "far": [d["id"] for d in got_f]})
        os.makedirs(os.path.dirname(hp) or ".", exist_ok=True)
        json.dump(hist, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"(recorded in {hp})")


if __name__ == "__main__":
    main()
