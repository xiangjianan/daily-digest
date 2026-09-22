#!/usr/bin/env python3
"""从 Hermes state.db 提取每日 cron 任务的最终输出，生成静态 JSON 并推送 GitHub。

每次运行全量重建 data/（历史自愈），仅在内容有变化时 commit+push。
无变化时静默退出（stdout 为空）。
"""
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HOME = Path.home()
DB_PATH = HOME / ".hermes" / "state.db"
REPO_DIR = HOME / "daily-digest"
DATA_DIR = REPO_DIR / "data"

# job_id -> 展示配置
JOBS = {
    "6ff8e716c927": {"name": "每日创意小工具", "emoji": "🛠️", "time": "03:00"},
    "4e5dc8651932": {"name": "每日沉迷小游戏", "emoji": "🎮", "time": "10:00"},
    "5bdfe48fa5d4": {"name": "GitHub 趣项目", "emoji": "🔥", "time": "17:00"},
}
JOB_ORDER = list(JOBS.keys())

PREVIEW_LEN = 180


def clean_text(text: str) -> str:
    """去掉 cron 注入的前缀说明等噪音，只保留正文。"""
    return text.strip()


def extract_session(db, session_id):
    """返回 (最终 assistant 正文, 开始时间, 结束时间, 状态)"""
    rows = db.execute(
        "SELECT role, content, timestamp FROM messages WHERE session_id=? ORDER BY id",
        (session_id,),
    ).fetchall()
    if not rows:
        return None
    started = rows[0][2]
    ended = rows[-1][2]
    final_text = None
    for role, content, ts in rows:
        if role == "assistant" and content and content.strip():
            final_text = content  # 取最后一条非空 assistant
    status = "ok" if final_text else "fail"
    return final_text, started, ended, status


def main():
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    sessions = db.execute(
        "SELECT id, started_at FROM sessions WHERE source='cron'"
    ).fetchall()

    # {date_str: {job_id: {...}}}
    days = {}
    for sid, started_at in sessions:
        m = re.match(r"cron_([0-9a-f]+)_", sid)
        if not m or m.group(1) not in JOBS:
            continue
        job_id = m.group(1)
        day = datetime.fromtimestamp(started_at).strftime("%Y-%m-%d")
        result = extract_session(db, sid)
        if result is None:
            continue
        text, t0, t1, status = result
        dur_min = max(0, round((t1 - t0) / 60))
        preview = clean_text(text)[:PREVIEW_LEN] if text else ""
        entry = {
            "name": JOBS[job_id]["name"],
            "emoji": JOBS[job_id]["emoji"],
            "time": JOBS[job_id]["time"],
            "status": status,
            "duration_min": dur_min,
            "preview": preview,
        }
        days.setdefault(day, {})[job_id] = entry
        if text:
            days[day][job_id]["full"] = clean_text(text)

    db.close()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 每日文件
    for day, jobs in sorted(days.items()):
        ordered = [dict(jobs[jid], job_id=jid) for jid in JOB_ORDER if jid in jobs]
        payload = {"date": day, "jobs": ordered}
        (DATA_DIR / f"{day}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
        )

    # manifest（不含全文，页面先拉这个）
    manifest_days = []
    for day in sorted(days.keys(), reverse=True):
        jobs = days[day]
        ordered = [dict(jobs[jid], job_id=jid) for jid in JOB_ORDER if jid in jobs]
        manifest_days.append({"date": day, "jobs": ordered})
    manifest = {"days": manifest_days}
    (DATA_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    # git 有变化才推送
    def run(cmd, **kw):
        return subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True, **kw)

    run(["git", "add", "data"])
    diff = run(["git", "diff", "--cached", "--quiet"]).returncode != 0
    if not diff:
        print("", end="")  # 静默
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    run(["git", "commit", "-m", f"sync {now}"])
    push = run(["git", "push"])
    if push.returncode == 0:
        print(f"✅ daily-digest 已同步 {now}（{len(manifest_days)} 天）")
    else:
        print(f"❌ push 失败: {push.stderr.strip()[:300]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
