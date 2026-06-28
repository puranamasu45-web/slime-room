from unittest.mock import MagicMock, patch

from sns_bot.src.x_poster import check_duplicate_post


def test_check_duplicate_detects_same_text():
    post_log = [
        {"text": "既存のツイート", "tweet_id": "123"},
    ]
    assert check_duplicate_post("既存のツイート", post_log) is True


def test_check_duplicate_allows_new_text():
    post_log = [
        {"text": "既存のツイート", "tweet_id": "123"},
    ]
    assert check_duplicate_post("新しいツイート", post_log) is False


def test_check_duplicate_empty_log():
    assert check_duplicate_post("何でも", []) is False


@patch("sns_bot.src.x_poster.is_dry_run", return_value=True)
def test_post_tweet_dry_run(mock_dry_run):
    from sns_bot.src.x_poster import post_tweet

    result = post_tweet("テストツイート")
    assert result["id"] == "dry_run"
    assert result["text"] == "テストツイート"
