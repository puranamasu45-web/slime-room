from unittest.mock import patch

from sns_bot.src.trend_fetcher import (
    deduplicate,
    filter_blocked,
    get_fallback_keywords,
    run,
)


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


def test_get_fallback_keywords_nonempty_and_tagged():
    fallback = get_fallback_keywords()
    assert len(fallback) >= 1
    assert all(kw["source"] == "fallback" for kw in fallback)


@patch("sns_bot.src.trend_fetcher.save_json")
@patch("sns_bot.src.trend_fetcher.load_json", return_value=[])
@patch("sns_bot.src.trend_fetcher.load_blocked_keywords", return_value=[])
@patch(
    "sns_bot.src.trend_fetcher.load_settings",
    return_value={"trends": {"region": "japan"}},
)
@patch(
    "sns_bot.src.trend_fetcher.fetch_trending_keywords",
    side_effect=Exception("429 Too Many Requests"),
)
def test_run_uses_fallback_on_exception(
    mock_fetch, mock_settings, mock_blocked, mock_load, mock_save
):
    result = run()
    assert len(result) >= 1
    assert all(kw["source"] == "fallback" for kw in result)
    # At least one entry was persisted to the log.
    saved = mock_save.call_args[0][1]
    assert len(saved) >= 1


@patch("sns_bot.src.trend_fetcher.save_json")
@patch("sns_bot.src.trend_fetcher.load_json", return_value=[])
@patch("sns_bot.src.trend_fetcher.load_blocked_keywords", return_value=[])
@patch(
    "sns_bot.src.trend_fetcher.load_settings",
    return_value={"trends": {"region": "japan"}},
)
@patch("sns_bot.src.trend_fetcher.fetch_trending_keywords", return_value=[])
def test_run_uses_fallback_on_empty(
    mock_fetch, mock_settings, mock_blocked, mock_load, mock_save
):
    result = run()
    assert len(result) >= 1
    assert result[0]["source"] == "fallback"


@patch("sns_bot.src.trend_fetcher.save_json")
@patch("sns_bot.src.trend_fetcher.load_blocked_keywords", return_value=[])
@patch(
    "sns_bot.src.trend_fetcher.load_settings",
    return_value={"trends": {"region": "japan"}},
)
@patch("sns_bot.src.trend_fetcher.fetch_trending_keywords", return_value=[])
def test_run_guarantees_entry_even_when_all_fallback_seen(
    mock_fetch, mock_settings, mock_blocked, mock_save
):
    # Every fallback word is already in the log -> dedup would empty the list,
    # but the guarantee must still inject one fresh entry.
    seen = [{"keyword": kw["keyword"]} for kw in get_fallback_keywords()]
    with patch("sns_bot.src.trend_fetcher.load_json", return_value=seen):
        result = run()
    assert len(result) >= 1
    assert result[0]["source"] == "fallback"
