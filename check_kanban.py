#!/usr/bin/env python3
"""
カンバン停滞タスクチェックスクリプト
毎朝実行して、停滞・期限切れタスクをログに記録する
"""
import urllib.request
import json
from datetime import datetime, timezone, timedelta
import os

API_KEY = "AIzaSyBadywmMpuz7v6uPaOis85YoTjRAT_yurU"
PROJECT_ID = "my-kanban-4cafd"
LOG_PATH = os.path.expanduser("~/.claude/projects/-Users-ayaho/memory/kanban_log.md")

JST = timezone(timedelta(hours=9))

def fetch_tasks():
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/tasks?key={API_KEY}&pageSize=200"
    with urllib.request.urlopen(url) as res:
        data = json.loads(res.read())
    tasks = []
    for d in data.get("documents", []):
        f = d.get("fields", {})
        def sv(key): return f.get(key, {}).get("stringValue")
        def nv(key): return f.get(key, {}).get("integerValue") or f.get(key, {}).get("doubleValue")
        def bv(key): return f.get(key, {}).get("booleanValue", False)
        tasks.append({
            "id": d["name"].split("/")[-1],
            "title": sv("title") or "",
            "status": sv("status") or "",
            "category": sv("category") or "",
            "due": sv("due"),
            "pinned": bv("pinned"),
            "updatedAt": int(nv("updatedAt") or nv("created") or 0),
            "created": int(nv("created") or 0),
        })
    return tasks

def check(tasks):
    now = datetime.now(JST)
    today_str = now.strftime("%Y-%m-%d")
    stale_days = 7  # 7日以上動きがないDoingを停滞とみなす

    alerts = []

    for t in tasks:
        if t["status"] == "done":
            continue

        # 期限切れ
        if t["due"] and t["due"] < today_str:
            alerts.append(f"⚠️ **期限切れ** [{t['category']}] {t['title']}（期日: {t['due']}）")

        # 3日以内に期限が来る
        elif t["due"]:
            diff = (datetime.strptime(t["due"], "%Y-%m-%d") - datetime.strptime(today_str, "%Y-%m-%d")).days
            if 0 <= diff <= 3:
                alerts.append(f"⏰ **期日間近{diff}日** [{t['category']}] {t['title']}（期日: {t['due']}）")

        # Doingで停滞
        if t["status"] == "doing" and t["updatedAt"]:
            updated = datetime.fromtimestamp(t["updatedAt"] / 1000, tz=JST)
            days_in_doing = (now - updated).days
            if days_in_doing >= stale_days:
                alerts.append(f"🐢 **Doingで{days_in_doing}日停滞** [{t['category']}] {t['title']}")

    return alerts

def snapshot_summary(tasks):
    todo = [t for t in tasks if t["status"] == "todo"]
    doing = [t for t in tasks if t["status"] == "doing"]
    done_recent = [t for t in tasks if t["status"] == "done"]
    return f"Todo: {len(todo)}件 / Doing: {len(doing)}件 / Done(累計): {len(done_recent)}件"

def append_log(alerts, summary):
    now = datetime.now(JST)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    lines = [f"\n### {date_str} {time_str}", f"**状況:** {summary}"]
    if alerts:
        lines.append("**アラート:**")
        for a in alerts:
            lines.append(f"- {a}")
    else:
        lines.append("**アラート:** なし")

    # ファイルがなければ作成
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            f.write("---\nname: カンバン進捗ログ\ndescription: カンバンの日次スナップショットと停滞アラート\ntype: project\n---\n\n## カンバン進捗ログ\n")

    with open(LOG_PATH, "a") as f:
        f.write("\n".join(lines) + "\n")

    print("\n".join(lines))

if __name__ == "__main__":
    tasks = fetch_tasks()
    alerts = check(tasks)
    summary = snapshot_summary(tasks)
    append_log(alerts, summary)
