#!/usr/bin/env python3
"""
my-share 私房 IPTV M3U 自動過濾腳本

數據源(全部免費公開):
  - iptv-org(主要源): https://github.com/iptv-org/iptv
  - 回退源 1:         https://raw.githubusercontent.com/suxuang/iptv-cn/main/all.m3u
  - 回退源 2:         https://raw.githubusercontent.com/joevess/IPTV/main/lite.m3u

過濾規則:
  - 名稱 OR tvg-id 命中以下關鍵字之一即收錄:
      ViuTV、港台電視、CCTV-5、CCTV-5+、廣東體育、芒果TV、湖南衛視
  - 去重(以 url 為 key)
  - 失敗源容錯,確保至少有 1 個 source 成功就生成 m3u

輸出: my-channels.m3u(utf-8, M3U Plus 格式)
"""
from __future__ import annotations

import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

# === 過濾規則(每行: [匹配關鍵字, 顯示分類]) ===
FILTER_RULES = [
    (r"ViuTV", "ViuTV"),
    (r"港台電視|RTHK", "港台電視"),
    (r"CCTV-?5\+?", "CCTV-5 系列"),
    (r"廣東體育|GDSports|Guangdong Sports", "廣東體育"),
    (r"芒果TV|湖南衛視|Hunan Satellite|Mango TV|HNTV", "芒果 / 湖南衛視"),
]

# === 數據源(主要 + 2 個回退) ===
SOURCES = [
    # iptv-org:合法開源大寶庫(簡繁分流)
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/hk.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tw.m3u",
    # 國內每日自動維護嘅聚合源:CCTV5 / 湖南衛視 / 芒果 / 港台都有
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/list.m3u",
]

OUTPUT_FILE = "my-channels.m3u"
FETCH_TIMEOUT = 25  # 秒
USER_AGENT = "Mozilla/5.0 (compatible; my-share-iptv-bot/1.0)"


def fetch(url: str) -> str | None:
    """抓取 m3u 文本。失敗返回 None。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            raw = resp.read()
            for enc in ("utf-8", "gbk", "gb2312", "utf-16"):
                try:
                    return raw.decode(enc)
                except UnicodeDecodeError:
                    continue
            return raw.decode("utf-8", errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        print(f"  ⚠️  source failed: {url} ({e})", file=sys.stderr)
        return None


def parse_m3u(text: str):
    """解析 M3U Plus → [(name, attrs_dict, url), ...]"""
    if not text or not text.lstrip().startswith("#EXTM3U"):
        return []
    entries = []
    attrs: dict = {}
    name = ""
    for line in text.splitlines():
        line = line.rstrip()
        if not line:
            continue
        if line.startswith("#EXTINF:"):
            # 提取 tvg-name 和 group-title
            name_match = re.search(r'tvg-name="([^"]*)"', line)
            tvg_name = name_match.group(1) if name_match else ""
            group_match = re.search(r'group-title="([^"]*)"', line)
            group = group_match.group(1) if group_match else ""
            # 抓末尾 , 後的名稱
            tail = line.split(",", 1)[1].strip() if "," in line else ""
            name = tail or tvg_name
            attrs = {"tvg-name": tvg_name, "group-title": group}
        elif line.startswith("#") or line.startswith("EXTINF"):
            continue
        else:
            entries.append((name, attrs, line))
            name = ""
            attrs = {}
    return entries


def matches(name: str, attrs: dict) -> tuple[bool, str]:
    """檢查是否命中過濾規則。返回 (命中?, 分類標籤)。"""
    text = " ".join([name or "", attrs.get("tvg-name", "") or "", attrs.get("group-title", "") or ""])
    for pattern, label in FILTER_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return True, label
    return False, ""


def main() -> int:
    print(f"[{datetime.now(timezone.utc).isoformat()}] 開始抓取 IPTV 源...")
    all_entries: dict[str, tuple[str, dict, str]] = {}

    for src in SOURCES:
        print(f"→ 抓取: {src}")
        text = fetch(src)
        if not text:
            continue
        entries = parse_m3u(text)
        print(f"  解析到 {len(entries)} 條")
        for name, attrs, url in entries:
            if not url.startswith(("http://", "https://", "rtmp://", "rtsp://")):
                continue
            hit, label = matches(name, attrs)
            if not hit:
                continue
            # 用 url 去重;首次入選者保留
            if url not in all_entries:
                all_entries[url] = (name, attrs, label)

    if not all_entries:
        print("❌ 所有源都失敗,本次無更新", file=sys.stderr)
        return 1

    # 按分類排序
    grouped: dict[str, list[tuple[str, dict, str]]] = {}
    for url, (name, attrs, label) in all_entries.items():
        grouped.setdefault(label, []).append((name, attrs, url))

    # 寫出 m3u plus
    hkt = timezone(timedelta(hours=8))
    now_str = datetime.now(hkt).strftime("%Y-%m-%d %H:%M HKT")
    lines = ['#EXTM3U']
    for label in ["ViuTV", "港台電視", "CCTV-5 系列", "廣東體育", "芒果 / 湖南衛視"]:
        if label not in grouped:
            continue
        lines.append(f'# 📺 {label}')
        for name, attrs, url in grouped[label]:
            safe_name = (name or label).replace('"', "'")
            lines.append(
                f'#EXTINF:-1 tvg-name="{safe_name}" group-title="{label}",{safe_name}'
            )
            lines.append(url)
    lines.append(f'# 最後更新:{now_str}')

    output = "\n".join(lines) + "\n"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"✅ 寫出 {OUTPUT_FILE}: {len(all_entries)} 條頻道")
    for label, items in grouped.items():
        print(f"   - {label}: {len(items)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())