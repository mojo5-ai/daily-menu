#!/usr/bin/env python3
"""Download and cache HowToCook recipe data (all_recipes.json).

Output (stdout, JSON): {"cache": "<abs path>", "fresh": bool, "recipes": int, "error": str?}
Exits 1 only when no usable cache exists at all.
"""
import argparse
import json
import os
import sys
import time
import urllib.request

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
URL = "https://raw.githubusercontent.com/worryzyy/HowToCook-mcp/master/all_recipes.json"
TTL = 30 * 86400  # 30 days


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="ignore cache age and re-download")
    args = ap.parse_args()

    os.makedirs(CACHE_DIR, exist_ok=True)
    cache = os.path.join(CACHE_DIR, "all_recipes.json")

    if not args.force and os.path.exists(cache):
        age = time.time() - os.path.getmtime(cache)
        if age < TTL:
            with open(cache) as f:
                data = json.load(f)
            print(json.dumps({"cache": cache, "fresh": True, "recipes": len(data)}, ensure_ascii=False))
            return

    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "daily-recipe-recommender"})
        with urllib.request.urlopen(req, timeout=60) as r:
            blob = r.read()
        payload = json.loads(blob)
        if not isinstance(payload, list) or not payload:
            raise ValueError("unexpected data shape: expected non-empty list")
        tmp = cache + ".tmp"
        with open(tmp, "wb") as f:
            f.write(blob)
        os.replace(tmp, cache)
        print(json.dumps({"cache": cache, "fresh": True, "recipes": len(payload)}, ensure_ascii=False))
    except Exception as e:
        if os.path.exists(cache):
            print(json.dumps({"cache": cache, "fresh": False, "error": str(e)}, ensure_ascii=False))
        else:
            print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
