# daily-menu · 每日菜谱推荐

一个 Codex 技能（skill）：基于 [HowToCook](https://github.com/Anduin2017/HowToCook) 菜谱数据，每日智能推荐三餐菜单，生成一个**单文件、可离线交互的 HTML 页面**。

## 功能

- 早 / 午 / 晚 / 汤 / 甜品 / 小吃 六个餐位，卡片网格展示菜品图片
- 点击菜名展开制作原料与制作过程
- 每个餐位：🔗 同步开关（点亮后菜量跟随人数）+ 菜数量输入框（自定义数量持久保留）
- 人数调节（1-10）：只缩放已 🔗 的餐位，不重抽已有菜品
- 「今日推荐」按钮：离线随机换菜（图钉菜锁定不动）
- 每道菜四个标记：📌 图钉（刷新/每日保留）· ☺️ 美味 · ❤️ 收藏（按分类收藏夹抽屉）· ✅ 完成（成就抽屉，按日期/按菜名两个维度展示完成日期）
- 「谱」图标：跳转 [HowToCook 站点](https://howtocook.aiursoft.com/Dashboard/Index)
- 全部状态存浏览器 localStorage，跨日重新生成页面不丢失

## 安装（作为 Codex 技能）

```bash
git clone https://github.com/mojo5-ai/daily-menu ~/.codex/skills/daily-recipe-recommender
```

注意：技能目录名必须为 `daily-recipe-recommender`（与 `SKILL.md` 中 `name` 一致）。

## 使用

在 Codex 中说「今天吃什么」「帮我推荐今天的三餐菜单」或 `$daily-recipe-recommender`：

1. 技能会询问忌口/过敏原与用餐人数（可跳过）
2. 首次运行自动下载菜谱数据到 `cache/`（30 天缓存）
3. 生成 `~/howtocook/meals.html`（浏览器直接打开，无需服务器）

## 目录

```
SKILL.md              技能说明（Codex 读取）
agents/openai.yaml    UI 元数据
scripts/fetch_data.py 数据拉取与 30 天缓存
scripts/build_page.py 生成单文件页面（过滤忌口 + 随机组餐 + 注入模板）
assets/page_template.html 页面模板（全部交互逻辑）
cache/                运行时数据缓存（.gitignore 排除）
```

## 数据来源与许可

菜谱数据快照来自 [worryzyy/HowToCook-mcp](https://github.com/worryzyy/HowToCook-mcp) 的 `all_recipes.json`（322 道菜），原始菜谱来自 [Anduin2017/HowToCook](https://github.com/Anduin2017/HowToCook)（Unlicense，公共领域）。图片由 `media.githubusercontent.com` 提供，加载失败时自动降级为文字占位。
