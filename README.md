# Daily Digest

English | [中文](#中文)

**Preview / 在线预览：https://xiangjianan.github.io/daily-digest/**

---

## English

A mobile-first web page that aggregates the daily outputs of [Hermes Agent](https://github.com/NousResearch/hermes-agent) scheduled tasks (cron jobs) into one clean dashboard — instead of scrolling through long chat messages on a phone.

### Features

- 📅 **Browse by date** — each day shows one card per job: publish time, run duration, success/failure status
- 📖 **Collapsible full text** with lightweight Markdown rendering; all links open in a new tab
- 🌗 **Light / dark theme** — follows system preference, manually toggleable
- 📲 **PWA** — installable to the home screen, offline-capable via service worker
- ⚡ No build step, no dependencies — a single HTML file plus static JSON

### How it works

```
Hermes state.db (SQLite) ──▶ export.py ──▶ data/*.json ──▶ git push ──▶ GitHub Pages
```

1. Hermes stores every cron run as a session in a local SQLite database; each job's final reply is the content that gets delivered to the chat.
2. `export.py` extracts those replies and regenerates the per-day JSON files (`data/YYYY-MM-DD.json` + `manifest.json`).
3. A script-only cron job (no LLM involved) runs the exporter a few times a day and pushes only when content actually changed.

### Aggregated jobs

| | Job | Schedule (UTC+8) |
|---|---|---|
| 🛠️ | Daily creative tool demo | 03:00 |
| 🎮 | Daily addictive mini-game demo | 10:00 |
| 🔥 | Interesting new GitHub projects | 17:00 |

### Local development

Static files only — open `index.html` through any HTTP server (service worker and `fetch()` require http/https):

```bash
python3 -m http.server 8080
# then visit http://localhost:8080
```

---

## 中文

一个手机优先的网页，把 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 每日定时任务的输出聚合到同一个页面里——不用再在手机上翻长长的聊天消息。

**在线预览：https://xiangjianan.github.io/daily-digest/**

### 特性

- 📅 按日期浏览：每天一张卡片对应一个任务，含发布时间、用时、成功/失败状态
- 📖 全文折叠展开，轻量 Markdown 渲染，所有链接新标签页打开
- 🌗 亮色 / 暗色主题，跟随系统偏好，可手动切换
- 📲 支持 PWA：可添加到手机主屏幕，Service Worker 离线可用
- ⚡ 无构建、无依赖：单文件 HTML + 静态 JSON

### 工作原理

1. Hermes 会把每次 cron 运行存为本地 SQLite 会话，任务最终回复即推送内容；
2. `export.py` 提取这些回复，重建按日期的 JSON 数据；
3. 一个纯脚本的定时任务（不消耗 LLM token）每天多次运行导出器，内容有变化才推送。

### 聚合的任务

| | 任务 | 时间（UTC+8） |
|---|---|---|
| 🛠️ | 每日创意小工具 Demo | 03:00 |
| 🎮 | 每日沉迷小游戏 Demo | 10:00 |
| 🔥 | GitHub 每日有趣新项目 | 17:00 |
