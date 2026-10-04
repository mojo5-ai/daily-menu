---
name: daily-recipe-recommender
description: Generate today's meal plan as a single-file interactive HTML page from the HowToCook recipe dataset (breakfast/lunch/dinner/soup/dessert/snack slots, with dish photos, per-slot count steppers, a people-count control, click-to-expand ingredient and step details, in-page refresh, and pin / delicious / favourite toggles). Use when the user asks for a daily or "今天吃什么" meal recommendation, or to re-recommend the menu. Do not use for looking up one specific recipe or general cooking-knowledge questions.
---

# Daily Recipe Recommender

Produce one self-contained HTML page (no dev server) that recommends today's meals from the HowToCook dataset. The page shows dish photos in a card grid; clicking a dish name expands 制作原料/制作过程. Header layout: "谱" tile (links to the HowToCook dashboard) on the left, centered ✨今日推荐 button with a people stepper beneath it, stacked slide-in drawer buttons on the right: the favourites drawer above an achievements drawer (dishes marked done with their done dates, browsable by date or by dish name). Each slot (早餐/午餐/晚餐/汤/甜品/小吃) shows a 🔗 link toggle and a dish-count input right after the slot name. A linked slot (🔗 lit, Tiffany blue) rescales its dish count with the people count; unlinked slots keep their own count. 午餐/晚餐 are linked by default. ✨今日推荐 re-picks the menu client-side (fully offline); changing the people count rescales ONLY the 🔗-linked slots, it does NOT re-randomize already-picked dishes. Per-dish toggles 📌 图钉 / ☺️ 美味 / ❤️ 收藏 / ✅ 完成 persist in the page's localStorage.

## Workflow

1. Ask one short skippable question: 忌口/过敏原 and 用餐人数. If the user skips or says "随便", use: no taboos, 1 人. (Do not ask about slots/counts — the page has fixed slots and the user tunes them in-page.)
2. Ensure fresh data (run from the skill folder):
   ```bash
   python3 scripts/fetch_data.py
   ```
   30-day cache under `cache/` (prints JSON with the `cache` path). Exit code 1 means no cache and no network: stop and tell the user; do not silently fall back to AI-generated recipes. Use `--force` when the user wants to refresh the dataset.
3. Generate the page:
   ```bash
   python3 scripts/build_page.py --allergies "虾" --avoid "香菜" --people 2
   ```
   - `--allergies` / `--avoid`: comma-separated; substring-matched against ingredient names and baked into the embedded pool, so the in-page refresh never suggests them.
   - `--people`: default 1. Sets the initial dish counts per slot (午餐/晚餐 = one dish per person, 1 for the other slots); the page can override counts afterwards via its UI.
   - `--out`: default `~/howtocook/meals.html`. The stable path is intentional: browser localStorage keeps pin/favourite/delicious/counts/people state across daily regenerations.
   - `--seed N`: reproducible menu when requested.
   The script prints JSON: `out` path and the picked menu per slot.
4. Reply with the absolute file path as a Markdown link plus the picked dish names per slot. If the user wants, open it on macOS with `open <path>`.

## Invariants

- The page embeds the full filtered dataset (with image URLs), so refresh works offline; images load from media.githubusercontent.com and fall back to a name-initial placeholder when offline/failed. Do not add other network calls to the template.
- Persisted state is under localStorage key `htc.state.v1`: `pins`, `delicious`, `favs`, `dones`, `doneDates` (id → YYYY-MM-DD), `people`, `slotCounts`, `linked`.
- The drawers (favourites/achievements) share one side panel with a CSS slide-in animation (transform + visibility, backdrop fade); drive them with `.open`/`.show` classes, never the `hidden` attribute. Remembered `slotCounts` and `people` must never be clobbered by refresh / re-recommend / daily regeneration.
- `default_counts()` in `scripts/build_page.py` sets the initial per-slot counts at generation (午餐/晚餐 = one dish per person, others = 1). On the page, changing the people count rescales ONLY 午餐/晚餐; 早餐/汤/甜品/小吃 keep their current (possibly custom) counts.
- The 🔗 per-slot link toggle (default linked = 午餐/晚餐) decides which slots follow the people count; persist it in `state.linked`.
- Changing the people count must only adjust dish counts (trim non-pinned / fill the gap), never re-pick existing dishes; only ✨今日推荐 re-randomizes.
- Only edit `assets/page_template.html` when the user asks for UI changes; keep the `__DATASET__`, `__MENU__`, `__META__` placeholders — `build_page.py` fails fast if one is missing.
