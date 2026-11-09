# 实现偏差记录 · OS 题库

对应规范：.pencil/documents/0b19d475.../handoff/IMPLEMENT.md v1.0.0
实现文件：题库.html

## D-01 实现载体：单文件 HTML，而非 Vite + React + TS

- 规格条款：§2 构建 — Vite + React 18+ + TypeScript（strict）
- 实际做法：单文件 题库.html，原生 JS + CSS，题目数据内联为 JSON 常量
- 原因：交付物要求双击即开、完全离线、可直接改；不引入 node 工具链与构建步骤
- 影响范围：状态用单个普通对象 S 承载（对应 useReducer 的 state），无类型检查；组件用字符串模板函数替代 React 组件

## D-02 字体未自托管

- 规格条款：§2 字体 — Inter Tight / Inter / JetBrains Mono，自托管 woff2 + font-display: swap
- 实际做法：系统字体栈回退（Inter Tight → Inter → -apple-system → Segoe UI → 微软雅黑）
- 原因：单文件离线分发，不携带字体文件
- 影响范围：字形宽度与设计稿有细微差异，尤其是 28px 题面的字距

## D-03 图标未使用 lucide-react

- 规格条款：§2 图标 — lucide-react，禁止手写 SVG
- 实际做法：主题与更多按钮使用字符 ☾ / ☀ / ⋯，翻页用文字按钮
- 原因：无外部依赖
- 影响范围：图标风格与设计稿不一致，后续可替换为内联 SVG 路径

## D-04 新增规格未列出的交互

- 规格条款：§6 组件契约未包含以下项
- 实际做法：新增快捷键 Q（中英对照）、W（随机顺序）、E（只看错题）、R（收藏）、← →（上一题/下一题）、Ctrl+.（折叠侧栏）；新增收藏功能与 starred 字段；章节筛选改为可多选
- 原因：用户追加需求
- 影响范围：侧栏「选项」组、顶栏键位提示、Progress 模型增加 starred

## D-05 空态图标使用 Noto Emoji 小猪

- 规格条款：§6 EmptyState — 图标 19 置于 44×44 surface 圆底
- 实际做法：Google Noto Emoji（U+1F437）SVG 以 data URI 内联，透明底色，26px 置于 44×44 surface 圆底
- 原因：用户指定使用该 emoji，且要求保留图标底色
- 影响范围：仅空态

## D-06 进度键与迁移

- 规格条款：§2 持久化 — 单键 osqb.progress.v1
- 实际做法：使用 osqb.progress.v1；首次运行时从旧键 os_bank_v2 迁移 answered/wrong
- 原因：保留用户已有作答记录
- 影响范围：仅首次迁移，之后不再读写旧键
