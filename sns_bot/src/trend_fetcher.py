import argparse
import random
import sys
from datetime import datetime, timezone

from pytrends.request import TrendReq

from sns_bot.src.utils import (
    load_blocked_keywords,
    load_json,
    load_settings,
    logger,
    save_json,
    setup_logging,
)

# Evergreen, season- and time-independent keywords used when pytrends returns
# nothing (429, empty result, or an exception). They keep the posting pipeline
# supplied so the account never goes silent, and read naturally in the
# templates no matter when they are posted.
FALLBACK_KEYWORDS = [
    "ゲーム",
    "アニメ",
    "マンガ",
    "映画",
    "音楽",
    "グルメ",
    "カフェ",
    "旅行",
    "読書",
    "ファッション",
    "スイーツ",
    "ガジェット",
]


def get_fallback_keywords() -> list[dict]:
    return [{"keyword": kw, "source": "fallback"} for kw in FALLBACK_KEYWORDS]


def fetch_trending_keywords() -> list[dict]:
    pytrends = TrendReq(hl="ja-JP", tz=-540)
    df = pytrends.trending_searches(pn="japan")
    keywords = df[0].tolist()
    return [{"keyword": kw, "source": "google_trends"} for kw in keywords]


def filter_blocked(keywords: list[dict], blocked: list[str]) -> list[dict]:
    return [
        kw
        for kw in keywords
        if not any(b in kw["keyword"] for b in blocked)
    ]


def deduplicate(new_keywords: list[dict], existing_log: list) -> list[dict]:
    recent_keywords = set()
    for entry in existing_log[-200:]:
        recent_keywords.add(entry.get("keyword", ""))

    return [kw for kw in new_keywords if kw["keyword"] not in recent_keywords]


def run():
    setup_logging()
    settings = load_settings()
    logger.info("Fetching trends for region: %s", settings["trends"]["region"])

    try:
        raw_keywords = fetch_trending_keywords()
    except Exception as e:
        logger.warning("pytrends failed (%s); using fallback keywords", e)
        raw_keywords = []

    if not raw_keywords:
        logger.warning("pytrends returned no keywords; using fallback keywords")
        raw_keywords = get_fallback_keywords()

    logger.info("Fetched %d raw trending keywords", len(raw_keywords))

    blocked = load_blocked_keywords()
    filtered = filter_blocked(raw_keywords, blocked)
    logger.info("After blocking: %d keywords", len(filtered))

    existing_log = load_json("trends_log.json")
    new_keywords = deduplicate(filtered, existing_log)
    logger.info("New unique keywords: %d", len(new_keywords))

    # Guarantee at least one keyword reaches the log so the post step is never
    # left without input, even if dedup removed everything (e.g. fallback words
    # already used recently). Prefer a fresh fallback word, but fall back to any.
    if not new_keywords:
        fallback = get_fallback_keywords()
        fresh_fallback = deduplicate(fallback, existing_log)
        new_keywords = [random.choice(fresh_fallback or fallback)]
        logger.warning(
            "No new keywords after dedup; injecting fallback keyword: %s",
            new_keywords[0]["keyword"],
        )

    now = datetime.now(timezone.utc).isoformat()
    entries = [
        {
            "keyword": kw["keyword"],
            "source": kw["source"],
            "fetched_at": now,
        }
        for kw in new_keywords
    ]

    existing_log.extend(entries)

    max_log_size = 1000
    if len(existing_log) > max_log_size:
        existing_log = existing_log[-max_log_size:]

    save_json("trends_log.json", existing_log)
    logger.info("Saved %d total entries to trends_log.json", len(existing_log))

    return new_keywords


def main():
    parser = argparse.ArgumentParser(description="Fetch trending keywords")
    parser.parse_args()
    keywords = run()
    for kw in keywords:
        print(f"  - {kw['keyword']}")


if __name__ == "__main__":
    main()
