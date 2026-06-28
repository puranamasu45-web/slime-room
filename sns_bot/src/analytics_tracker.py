import os
from datetime import datetime, timezone

import tweepy

from sns_bot.src.utils import (
    is_dry_run,
    load_json,
    logger,
    save_json,
    setup_logging,
)


def get_x_client() -> tweepy.Client:
    return tweepy.Client(
        bearer_token=os.environ.get("X_BEARER_TOKEN"),
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )


def fetch_tweet_metrics(client: tweepy.Client, tweet_id: str) -> dict | None:
    try:
        response = client.get_tweet(
            tweet_id,
            tweet_fields=["public_metrics", "created_at"],
        )
        if response.data:
            return response.data.public_metrics
    except Exception as e:
        logger.warning("Failed to fetch metrics for tweet %s: %s", tweet_id, e)
    return None


def run():
    setup_logging()
    logger.info("Starting analytics collection")

    post_log = load_json("post_log.json")
    if not post_log:
        logger.info("No posts to analyze")
        return

    real_posts = [p for p in post_log if not p.get("dry_run", False)]
    if not real_posts:
        logger.info("No real (non-dry-run) posts to analyze")
        return

    if is_dry_run():
        logger.info("[DRY RUN] Would fetch metrics for %d posts", len(real_posts))
        return

    client = get_x_client()
    updated = 0

    for entry in post_log:
        if entry.get("dry_run", False):
            continue

        tweet_id = entry.get("tweet_id")
        if not tweet_id or tweet_id == "dry_run":
            continue

        metrics = fetch_tweet_metrics(client, tweet_id)
        if metrics:
            entry["metrics"] = {
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "impressions": metrics.get("impression_count", 0),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            updated += 1

    save_json("post_log.json", post_log)
    logger.info("Updated metrics for %d/%d posts", updated, len(real_posts))

    print_summary(post_log)


def print_summary(post_log: list):
    real_posts = [p for p in post_log if not p.get("dry_run") and p.get("metrics")]
    if not real_posts:
        return

    total_likes = sum(p["metrics"].get("likes", 0) for p in real_posts)
    total_rts = sum(p["metrics"].get("retweets", 0) for p in real_posts)
    total_impressions = sum(p["metrics"].get("impressions", 0) for p in real_posts)

    logger.info("=== Analytics Summary ===")
    logger.info("Total posts: %d", len(real_posts))
    logger.info("Total likes: %d", total_likes)
    logger.info("Total retweets: %d", total_rts)
    logger.info("Total impressions: %d", total_impressions)

    if real_posts:
        best = max(real_posts, key=lambda p: p["metrics"].get("likes", 0))
        logger.info(
            "Best post: '%s' (%d likes)",
            best["text"][:50],
            best["metrics"].get("likes", 0),
        )


if __name__ == "__main__":
    run()
