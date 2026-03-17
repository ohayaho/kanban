#!/usr/bin/env python3
"""
習志野の気象データを毎朝取得して、health_log.mdの「気象：未取得」を更新するスクリプト
"""
import urllib.request
import json
import os
import re
from datetime import datetime, timezone, timedelta

LOCATION  = "Narashino"
LOG_PATH  = os.path.expanduser("~/.claude/projects/-Users-ayaho/memory/health_log.md")
JST       = timezone(timedelta(hours=9))

WEATHER_JA = {
    "Sunny": "晴れ", "Clear": "晴れ", "Partly cloudy": "晴れ時々曇り",
    "Cloudy": "曇り", "Overcast": "曇り", "Mist": "霧",
    "Light rain": "小雨", "Moderate rain": "雨", "Heavy rain": "大雨",
    "Light snow": "小雪", "Moderate snow": "雪", "Heavy snow": "大雪",
    "Thundery outbreaks possible": "雷雨の可能性",
    "Blowing snow": "吹雪", "Freezing drizzle": "凍雨",
    "Patchy rain possible": "にわか雨の可能性",
    "Patchy snow possible": "にわか雪の可能性",
}

def fetch_weather():
    url = f"https://wttr.in/{LOCATION}?format=j1"
    with urllib.request.urlopen(url, timeout=10) as res:
        data = json.loads(res.read())["data"]
    cc = data["current_condition"][0]
    w  = data["weather"][0]
    desc_en = cc["weatherDesc"][0]["value"]
    desc_ja = WEATHER_JA.get(desc_en, desc_en)
    return {
        "desc":     desc_ja,
        "temp":     cc["temp_C"],
        "min_temp": w["mintempC"],
        "max_temp": w["maxtempC"],
        "pressure": cc["pressure"],
    }

def format_weather(wx):
    return f"{wx['desc']}、最低{wx['min_temp']}℃/最高{wx['max_temp']}℃、気圧{wx['pressure']}hPa"

def update_log(wx):
    today = datetime.now(JST).strftime("%Y-%m-%d")
    weather_str = format_weather(wx)

    if not os.path.exists(LOG_PATH):
        print("health_log.md が見つかりません")
        return

    with open(LOG_PATH, "r") as f:
        content = f.read()

    # 今日のエントリに「気象：未取得」があれば更新
    pattern = rf"(## {today}.*?\*\*気象：\*\* )未取得"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, rf"\g<1>{weather_str}", content, flags=re.DOTALL)
        with open(LOG_PATH, "w") as f:
            f.write(content)
        print(f"{today} の気象データを更新: {weather_str}")
    else:
        print(f"{today} のエントリが見つからないか、すでに気象データが入っています")

if __name__ == "__main__":
    wx = fetch_weather()
    update_log(wx)
