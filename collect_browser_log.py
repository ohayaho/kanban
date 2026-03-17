#!/usr/bin/env python3
"""
Edgeブラウザ履歴の日次ログ収集スクリプト
毎朝4時にcronで実行（Edge終了中）
"""
import sqlite3, shutil, os, re
from datetime import datetime, timedelta, timezone
from collections import Counter

HISTORY_SRC  = os.path.expanduser(
    "~/Library/Application Support/Microsoft Edge/Default/History")
HISTORY_TMP  = "/tmp/edge_history_daily.db"
LOG_PATH     = os.path.expanduser(
    "~/.claude/projects/-Users-ayaho/memory/browser_log.md")

JST = timezone(timedelta(hours=9))

# ドメインを意味あるラベルに変換
DOMAIN_LABELS = {
    "github.com":           "開発（GitHub）",
    "mail.google.com":      "メール",
    "note.com":             "note発信",
    "editor.note.com":      "note記事編集",
    "chatgpt.com":          "ChatGPT",
    "claude.ai":            "Claude",
    "x.com":                "X（発信）",
    "voicy.jp":             "Voicy学習",
    "youtube.com":          "YouTube",
    "amazon.co.jp":         "Amazon買い物",
    "kurashiru.com":        "料理（クラシル）",
    "calendar.google.com":  "カレンダー",
    "docs.google.com":      "Googleドキュメント",
    "console.firebase.google.com": "Firebase開発",
    "uniqlo.com":           "ショッピング（ユニクロ）",
}

def collect():
    if not os.path.exists(HISTORY_SRC):
        print("Edgeの履歴ファイルが見つかりません")
        return

    try:
        shutil.copy2(HISTORY_SRC, HISTORY_TMP)
    except Exception as e:
        print(f"ファイルコピー失敗（Edgeが起動中？）: {e}")
        return

    con = sqlite3.connect(HISTORY_TMP)
    cur = con.cursor()

    # 昨日1日分
    now = datetime.now(JST)
    yesterday_start = datetime(now.year, now.month, now.day, tzinfo=JST) - timedelta(days=1)
    yesterday_end   = yesterday_start + timedelta(days=1)
    chrome_epoch    = datetime(1601, 1, 1, tzinfo=timezone.utc)
    t_start = int((yesterday_start.astimezone(timezone.utc) - chrome_epoch).total_seconds() * 1_000_000)
    t_end   = int((yesterday_end.astimezone(timezone.utc)   - chrome_epoch).total_seconds() * 1_000_000)

    cur.execute("""
        SELECT url, title, visit_count FROM urls
        WHERE last_visit_time >= ? AND last_visit_time < ?
    """, (t_start, t_end))
    rows = cur.fetchall()
    con.close()

    if not rows:
        print("昨日の履歴なし")
        return

    domain_count = Counter()
    for url, title, count in rows:
        m = re.match(r'https?://([^/]+)', url or '')
        if m:
            domain = m.group(1).replace('www.', '').replace('accounts.', '')
            # ノイズを除外
            if domain in ('google.com', 'googleapis.com', 'gstatic.com',
                          'bing.com', 'microsoftonline.com'):
                continue
            domain_count[domain] += count

    date_str = yesterday_start.strftime("%Y-%m-%d")
    top = domain_count.most_common(10)

    lines = [f"\n### {date_str}"]
    for domain, count in top:
        label = DOMAIN_LABELS.get(domain, domain)
        lines.append(f"- {label}（{count}回）")

    # ファイルがなければ作成
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            f.write("---\nname: ブラウザ閲覧ログ\ndescription: Edge閲覧履歴の日次サマリー\ntype: project\n---\n\n## ブラウザ閲覧ログ（日次）\n")

    with open(LOG_PATH, "a") as f:
        f.write("\n".join(lines) + "\n")

    print(f"{date_str} のログ保存完了（{len(rows)}URL / top10抽出）")
    print("\n".join(lines))

if __name__ == "__main__":
    collect()
