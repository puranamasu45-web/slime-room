import os
from datetime import datetime, timedelta, timezone

import tweepy

from sns_bot.src.utils import (
    is_dry_run,
    load_json,
    logger,
    save_json,
    setup_logging,
)

# Only collect metrics for posts newer than this many days. Older posts are
# frozen (metrics_final=True) and never read again. Without this gate every
# run re-fetched metrics for the entire post history, so the daily X API read
# volume grew with the number of posts and total cost scaled quadratically
# with the number of days the bot had been running.
METRICS_WINDOW_DAYS = 3


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

    now = datetime.now(timezone.utc)
    window = timedelta(days=METRICS_WINDOW_DAYS)

    # Created lazily so we never need X API credentials (or open a client) when
    # every post is already frozen and there is nothing to read.
    client = None
    updated = 0
    frozen = 0

    for entry in post_log:
        # dry-run posts have no real tweet to read.
        if entry.get("dry_run", False):
            continue

        # Already frozen: never read again.
        if entry.get("metrics_final"):
            continue

        tweet_id = entry.get("tweet_id")
        if not tweet_id or tweet_id == "dry_run":
            continue

        # Outside the metrics window: freeze it and stop reading it forever.
        posted_at = entry.get("posted_at")
        if posted_at:
            try:
                age = now - datetime.fromisoformat(posted_at)
            except ValueError:
                logger.warning(
                    "Invalid posted_at %r for tweet %s; freezing entry",
                    posted_at,
                    tweet_id,
                )
                entry["metrics_final"] = True
                frozen += 1
                continue
            if age > window:
                entry["metrics_final"] = True
                frozen += 1
                continue

        # Within the window: this is the only case that costs an API read.
        if client is None:
            client = get_x_client()

        metrics = fetch_tweet_metrics(client, tweet_id)
        if metrics:
            entry["metrics"] = {
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "impressions": metrics.get("impression_count", 0),
                "updated_at": now.isoformat(),
            }
            updated += 1

    save_json("post_log.json", post_log)
    logger.info(
        "Updated metrics for %d posts, froze %d posts older than %d days "
        "(out of %d real posts)",
        updated,
        frozen,
        METRICS_WINDOW_DAYS,
        len(real_posts),
    )

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
