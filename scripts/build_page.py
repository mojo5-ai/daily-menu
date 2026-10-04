#!/usr/bin/env python3
"""Generate today's single-file meal recommendation page.

Reads cached recipe JSON, filters out taboo/allergy ingredients, builds the
initial menu, and renders the template into one self-contained HTML file.
The page embeds the full filtered dataset so the in-page refresh button can
re-pick recipes offline; pinned/favoured/delicious state lives in the page's
localStorage.

Output (stdout, JSON): {"out": path, "menu": {slot: [names]}, "dataset": int, "excluded": int}
"""
import argparse
import datetime as dt
import json
import os
import random
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(SKILL_ROOT, "assets", "page_template.html")
DEFAULT_CACHE = os.path.join(SKILL_ROOT, "cache", "all_recipes.json")
DEFAULT_OUT = os.path.expanduser("~/howtocook/meals.html")

# slot -> (primary categories, fallback categories)
SLOTS = {
    "早餐": (["早餐"], ["主食"]),
    "午餐": (["荤菜", "素菜", "水产"], []),
    "晚餐": (["荤菜", "素菜", "水产"], []),
    "汤": (["汤"], ["甜品"]),
    "甜品": (["甜品"], ["饮品"]),
    "小吃": (["饮品"], ["甜品"]),
}
SLOT_ORDER = ["早餐", "午餐", "晚餐", "汤", "甜品", "小吃"]


def default_counts(people):
    """Initial per-slot dish counts at page generation.
    午餐/晚餐 scale with people (one dish per person); the rest default to 1.
    On the page, changing the people count only rescales 午餐/晚餐."""
    return {"早餐": 1, "午餐": people, "晚餐": people, "汤": 1, "甜品": 1, "小吃": 1}


def compact(r):
    img = None
    imgs = r.get("images") or []
    if imgs and isinstance(imgs[0], str) and imgs[0].startswith("http"):
        img = imgs[0]
    elif isinstance(r.get("image_path"), str) and r["image_path"].startswith("http"):
        img = r["image_path"]
    return {
        "id": r["id"],
        "name": r.get("name", r["id"]).replace("的做法", "").strip() or r["id"],
        "category": r.get("category", ""),
        "difficulty": r.get("difficulty"),
        "img": img,
        "ing": [[i.get("name", ""), i.get("text_quantity", "")] for i in r.get("ingredients", [])],
        "steps": [[s.get("step", n + 1), s.get("description", "")] for n, s in enumerate(r.get("steps", []))],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--allergies", default="", help="comma-separated allergy ingredients")
    ap.add_argument("--avoid", default="", help="comma-separated taboo ingredients")
    ap.add_argument("--people", type=int, default=2)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    with open(args.cache, encoding="utf-8") as f:
        recipes = json.load(f)

    excluded = [x.strip() for x in (args.allergies + "," + args.avoid).split(",") if x.strip()]

    def ok(r):
        for ing in r.get("ingredients", []):
            name = (ing.get("name") or "").lower()
            if any(bad.lower() in name for bad in excluded):
                return False
        return True

    pool = [r for r in recipes if ok(r)]
    by_cat = {}
    for r in pool:
        by_cat.setdefault(r.get("category", ""), []).append(r)

    menu = {}
    used = set()
    counts = default_counts(args.people)
    for slot in SLOT_ORDER:
        primary, fallback = SLOTS[slot]
        n = counts[slot]
        take = []
        for cats in (primary, fallback):
            cands = [r for cat in cats for r in by_cat.get(cat, []) if r["id"] not in used]
            random.shuffle(cands)
            take = cands[:n]
            if take:
                break
        for r in take:
            used.add(r["id"])
        menu[slot] = [r["id"] for r in take]

    dataset = [compact(r) for r in pool]
    meta = {
        "generated": dt.date.today().isoformat(),
        "data_from": dt.date.fromtimestamp(os.path.getmtime(args.cache)).isoformat(),
        "people": args.people,
        "allergies": [x.strip() for x in args.allergies.split(",") if x.strip()],
        "avoid": [x.strip() for x in args.avoid.split(",") if x.strip()],
    }

    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    def safe(o):
        # keep embedded JSON from breaking out of the <script> block
        return json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    for ph, val in (
        ("__META__", safe(meta)),
        ("__MENU__", safe(menu)),
        ("__DATASET__", safe(dataset)),
    ):
        if ph not in html:
            print(f"template missing placeholder {ph}", file=sys.stderr)
            sys.exit(1)
        html = html.replace(ph, val)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)

    display = {c["id"]: c["name"] for c in dataset}
    print(json.dumps({
        "out": os.path.abspath(args.out),
        "menu": {k: [display.get(i, i) for i in v] for k, v in menu.items()},
        "dataset": len(dataset),
        "excluded": len(recipes) - len(pool),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
