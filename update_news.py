#!/usr/bin/env python3
"""update_news.py — HK on-the-ground news scraper for Terry's personal site.

Strategy (zero-cost, no API keys):
1. Try multiple official HK news sources via HTTP fetch.
2. Parse HTML / XML, extract (title, link, summary, published).
3. Apply strict keyword filter: only keep items mentioning
   馬灣 / 天水圍 / 港燈 / HK Electric / 交通中斷 / 電力故障 / etc.
4. De-duplicate, sort by published desc, write news-data.json.

Designed to run on GitHub Actions (ubuntu-latest, Python 3.12).
"""
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from html import unescape
from pathlib import Path

HKT = timezone(timedelta(hours=8))
USER_AGENT = "Mozilla/5.0 (compatible; TerryNewsBot/1.0; +https://github.com/Terry20250224/my-share)"
OUTPUT_PATH = Path(__file__).parent / "news-data.json"
TIMEOUT = 20

# Strict filter — only on-the-ground items relevant to Terry's daily life.
KEYWORDS = [
    "馬灣", "天水圍", "港燈", "HK Electric", "中華電力", "中電",
    "元朗", "屯門", "荃灣", "葵青", "離島", "青衣", "大嶼山",
    "交通中斷", "交通意外", "嚴重擠塞", "道路封閉", "封路",
    "電力故障", "大規模停電", "供電中斷",
    "巴士", "地鐵", "港鐵", "西鐵", "輕鐵",
    "突發", "緊急", "疏散", "山泥傾瀉", "水浸", "塌樹",
    "八號風球", "黑色暴雨", "極端天氣",
]

# Tag priority (highest first) — drives UI color
TAG_RULES = [
    ("urgent",  ["突發", "緊急", "疏散", "八號風球", "黑色暴雨", "火警", "山泥傾瀉", "水浸"]),
    ("power",   ["港燈", "HK Electric", "中華電力", "中電", "停電", "供電中斷", "電力故障"]),
    ("traffic", ["交通", "巴士", "地鐵", "港鐵", "西鐵", "輕鐵", "隧道", "幹線", "封路", "擠塞", "改道"]),
]

MAX_ITEMS = 30  # hard cap to keep JSON small


def http_get(url: str) -> str | None:
    """Fetch URL with browser UA. Return body or None on any error."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.7"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = r.read()
            charset = r.headers.get_content_charset() or "utf-8"
            return data.decode(charset, errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        print(f"[fetch] FAIL {url}: {e}", file=sys.stderr)
        return None


def normalize_item(title: str, link: str, summary: str = "", published: str | None = None, source: str = "") -> dict:
    """Build a normalised news item dict."""
    title = re.sub(r"\s+", " ", title or "").strip()
    summary = re.sub(r"\s+", " ", summary or "").strip()
    tag = "local"
    text = (title + " " + summary).lower()
    for t, words in TAG_RULES:
        if any(w.lower() in text for w in words):
            tag = t
            break
    return {
        "title": title,
        "summary": summary[:280],
        "link": link,
        "published": published,
        "source": source,
        "tag": tag,
    }


def matches_keyword(title: str, summary: str) -> bool:
    text = title + " " + summary
    return any(kw in text for kw in KEYWORDS)


# ---------- RTHK latest news (HTML scrape, no RSS available) ----------

RTHK_RSS_LOCAL = "https://rthk.hk/rthk/news/rss/c_expressnews_clocal.xml"
RTHK_RSS_GREAT = "https://rthk.hk/rthk/news/rss/c_expressnews_cgreaterchina.xml"
RTHK_RSS_INTL = "https://rthk.hk/rthk/news/rss/c_expressnews_cinternational.xml"

def _parse_rss_items(xml: str, source_label: str) -> list[dict]:
    """Parse RTHK RSS XML into normalised news items."""
    items: list[dict] = []
    # RTHK wraps text in <![CDATA[...]]>; fall back to plain <title>...</title>.
    for m in re.finditer(
        r"<item>\s*<title>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</title>\s*"
        r"<guid[^>]*>(.*?)</guid>\s*"
        r"<link>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</link>\s*"
        r"(?:<description>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</description>\s*)?"
        r"<pubDate>\s*(.*?)\s*</pubDate>",
        xml, re.DOTALL,
    ):
        title = unescape(m.group(1)).strip()
        link = unescape(m.group(2 if m.group(3).startswith("http") else 3)).strip() or unescape(m.group(3)).strip()
        desc = unescape(m.group(4) or "").strip()
        pub = m.group(5).strip()
        if not title or not link:
            continue
        items.append(normalize_item(title, link, desc, pub, source_label))
    return items


def scrape_rthk() -> list[dict]:
    """Pull RTHK 即時新聞 / 本地 RSS feed (verified live URL)."""
    items: list[dict] = []
    for url, label in [
        (RTHK_RSS_LOCAL, "RTHK 即時新聞・本地"),
        (RTHK_RSS_GREAT, "RTHK 即時新聞・大中華"),
    ]:
        xml = http_get(url)
        if not xml or "<rss" not in xml.lower():
            continue
        items.extend(_parse_rss_items(xml, label))
    return items


# ---------- HK Government whatsnew (try RSS, fall back to HTML) ----------

def scrape_datagovhk() -> list[dict]:
    items: list[dict] = []
    # Try RSS first
    rss = http_get("https://data.gov.hk/feeds/whatsnew/whatsnew.rss.xml")
    if rss and "<rss" in rss.lower() or "<feed" in rss.lower():
        for m in re.finditer(r"<item>\s*<title>([^<]+)</title>\s*<link>([^<]+)</link>(?:\s*<pubDate>([^<]+)</pubDate>)?(?:\s*<description>([^<]+)</description>)?", rss):
            title, link, pub, desc = m.group(1), m.group(2), m.group(3), m.group(4)
            if matches_keyword(title, desc):
                items.append(normalize_item(title, link, desc or "", pub, "政府資料一線通"))
    # Fall back to HTML what's-new listing
    if not items:
        html = http_get("https://data.gov.hk/whatsnew/whatsnew_zh.html")
        if html:
            for m in re.finditer(r'<a\s+href="([^"]+)"[^>]*>([^<]{10,200})</a>', html):
                link, title = m.group(1), unescape(m.group(2)).strip()
                if link.startswith("/") or link.startswith("./"):
                    link = "https://data.gov.hk" + link
                if not link.startswith("http"):
                    continue
                if matches_keyword(title, ""):
                    items.append(normalize_item(title, link, "", None, "政府資料一線通"))
    return items


# ---------- HKO weather warnings (XML feed, structured) ----------

def scrape_hko_warnings() -> list[dict]:
    """Pull HK Observatory weather warning summary — only interesting when warnings are active."""
    items: list[dict] = []
    xml = http_get("https://rss.weather.gov.hk/rss/WeatherWarningSummaryv2_uc.xml")
    if not xml:
        return items
    # extract <title> + <link> pairs
    for m in re.finditer(r"<item>\s*<title>([^<]+)</title>\s*<link>([^<]+)</link>\s*<pubDate>([^<]+)</pubDate>", xml):
        title, link, pub = m.group(1), m.group(2), m.group(3)
        # HKO publishes a "no warning" item when nothing's active — skip those
        if "no warning" in title.lower() or "沒有警告" in title or "没有警告" in title:
            continue
        # Always show weather warnings if any are active
        items.append(normalize_item(title, link, "香港天文台現行天氣警告", pub, "HK Observatory 天氣警告"))
    return items


# ---------- Pipeline ----------

def dedupe(items: list[dict]) -> list[dict]:
    seen_titles: set[str] = set()
    out: list[dict] = []
    for it in items:
        t = it["title"].strip()
        if not t or t in seen_titles:
            continue
        seen_titles.add(t)
        out.append(it)
    return out


def main() -> int:
    print("[scrape] starting HK on-the-ground news fetch…")
    all_items: list[dict] = []
    for fn, label in [(scrape_rthk, "RTHK"), (scrape_datagovhk, "DATA.GOV.HK"), (scrape_hko_warnings, "HKO")]:
        print(f"[scrape] {label}")
        try:
            chunk = fn()
            before = len(chunk)
            filt = [it for it in chunk if matches_keyword(it["title"], it.get("summary", ""))]
            print(f"  → {before} item(s); {len(filt)} passed keyword filter")
            all_items.extend(filt)
        except Exception as e:
            print(f"  → exception: {e}", file=sys.stderr)

    all_items = dedupe(all_items)[:MAX_ITEMS]
    print(f"[scrape] {len(all_items)} item(s) after dedupe + cap ({MAX_ITEMS})")

    now_utc = datetime.now(timezone.utc)
    now_hkt = now_utc.astimezone(HKT)
    payload = {
        "version": 1,
        "updated_utc": now_utc.isoformat(),
        "updated_hkt": now_hkt.strftime("%Y-%m-%d %H:%M HKT"),
        "source": "RTHK + DATA.GOV.HK + HKO",
        "count": len(all_items),
        "items": all_items,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[write] {OUTPUT_PATH} ({len(all_items)} items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
