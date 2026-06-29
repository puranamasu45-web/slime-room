from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from sns_bot.src import analytics_tracker
from sns_bot.src.analytics_tracker import METRICS_WINDOW_DAYS, run


def _iso(days_ago: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def _build_log():
    return [
        # dry-run: never read.
        {"tweet_id": "dry_run", "dry_run": True, "posted_at": _iso(0), "text": "dry"},
        # fresh real post: inside the window, should be read.
        {"tweet_id": "fresh", "dry_run": False, "posted_at": _iso(1), "text": "fresh"},
        # old real post: outside the window, should be frozen and not read.
        {
            "tweet_id": "old",
            "dry_run": False,
            "posted_at": _iso(METRICS_WINDOW_DAYS + 2),
            "text": "old",
        },
        # already frozen: should be skipped entirely.
        {
            "tweet_id": "frozen",
            "dry_run": False,
            "posted_at": _iso(1),
            "metrics_final": True,
            "text": "frozen",
        },
    ]


@patch("sns_bot.src.analytics_tracker.save_json")
@patch("sns_bot.src.analytics_tracker.fetch_tweet_metrics")
@patch("sns_bot.src.analytics_tracker.get_x_client")
@patch("sns_bot.src.analytics_tracker.is_dry_run", return_value=False)
def test_run_reads_only_recent_posts(mock_dry, mock_client, mock_fetch, mock_save):
    mock_fetch.return_value = {
        "like_count": 5,
        "retweet_count": 1,
        "reply_count": 0,
        "impression_count": 100,
    }
    log = _build_log()

    with patch("sns_bot.src.analytics_tracker.load_json", return_value=log):
        run()

    # Only the single fresh post should have triggered an API read.
    read_ids = [call.args[1] for call in mock_fetch.call_args_list]
    assert read_ids == ["fresh"]

    by_id = {e["tweet_id"]: e for e in log}
    assert by_id["fresh"]["metrics"]["likes"] == 5
    # The old post is now frozen so it is never read again.
    assert by_id["old"]["metrics_final"] is True
    # Frozen post stays frozen and untouched.
    assert by_id["frozen"].get("metrics") is None

    mock_save.assert_called_once()


@patch("sns_bot.src.analytics_tracker.save_json")
@patch("sns_bot.src.analytics_tracker.fetch_tweet_metrics")
@patch("sns_bot.src.analytics_tracker.get_x_client")
@patch("sns_bot.src.analytics_tracker.is_dry_run", return_value=False)
def test_run_skips_client_when_all_frozen(mock_dry, mock_client, mock_fetch, mock_save):
    log = [
        {
            "tweet_id": "old",
            "dry_run": False,
            "posted_at": _iso(METRICS_WINDOW_DAYS + 5),
            "text": "old",
        },
        {
            "tweet_id": "frozen",
            "dry_run": False,
            "posted_at": _iso(1),
            "metrics_final": True,
            "text": "frozen",
        },
    ]

    with patch("sns_bot.src.analytics_tracker.load_json", return_value=log):
        run()

    # Nothing to read -> no client created and no API reads.
    mock_client.assert_not_called()
    mock_fetch.assert_not_called()
    assert log[0]["metrics_final"] is True
