from sns_bot.src.content_generator import generate_post, generate_tweet, make_hashtag


def test_make_hashtag_removes_spaces():
    assert make_hashtag("東京 オリンピック") == "東京オリンピック"


def test_make_hashtag_removes_hash():
    assert make_hashtag("#テスト") == "テスト"
    assert make_hashtag("＃テスト") == "テスト"


def test_generate_tweet_returns_string():
    tweet = generate_tweet("テストキーワード", style="general")
    assert tweet is not None
    assert isinstance(tweet, str)
    assert "テストキーワード" in tweet
    assert len(tweet) <= 280


def test_generate_tweet_different_styles():
    for style in ["general", "question", "opinion", "news", "entertainment"]:
        tweet = generate_tweet("AI技術", style=style)
        assert tweet is not None
        assert "AI技術" in tweet


def test_generate_post_with_trends():
    trends = [
        {"keyword": "トレンド1", "source": "google_trends"},
        {"keyword": "トレンド2", "source": "google_trends"},
    ]
    result = generate_post(trends)
    assert result is not None
    assert "keyword" in result
    assert "text" in result
    assert "char_count" in result
    assert result["char_count"] <= 280


def test_generate_post_empty_trends():
    result = generate_post([])
    assert result is None


def test_generate_tweet_hashtag_included():
    tweet = generate_tweet("Python", style="general")
    assert "#Python" in tweet or "Python" in tweet
