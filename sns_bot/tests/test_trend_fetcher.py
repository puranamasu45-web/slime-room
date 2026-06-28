from unittest.mock import patch

from sns_bot.src.trend_fetcher import deduplicate, filter_blocked


def test_filter_blocked_removes_matching():
    keywords = [
        {"keyword": "地震速報", "source": "google_trends"},
        {"keyword": "新作ゲーム", "source": "google_trends"},
        {"keyword": "逮捕された", "source": "google_trends"},
    ]
    blocked = ["地震", "逮捕"]
    result = filter_blocked(keywords, blocked)
    assert len(result) == 1
    assert result[0]["keyword"] == "新作ゲーム"


def test_filter_blocked_empty_list():
    keywords = [{"keyword": "テスト", "source": "google_trends"}]
    result = filter_blocked(keywords, [])
    assert len(result) == 1


def test_deduplicate_removes_existing():
    new_keywords = [
        {"keyword": "トレンドA", "source": "google_trends"},
        {"keyword": "トレンドB", "source": "google_trends"},
        {"keyword": "トレンドC", "source": "google_trends"},
    ]
    existing_log = [
        {"keyword": "トレンドA", "fetched_at": "2024-01-01"},
    ]
    result = deduplicate(new_keywords, existing_log)
    assert len(result) == 2
    keywords = [r["keyword"] for r in result]
    assert "トレンドA" not in keywords


def test_deduplicate_all_new():
    new_keywords = [{"keyword": "新しい", "source": "google_trends"}]
    result = deduplicate(new_keywords, [])
    assert len(result) == 1
