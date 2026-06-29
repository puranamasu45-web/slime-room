import argparse
import os
import sys
from datetime import datetime, timezone

import tweepy

from sns_bot.src.content_generator import generate_post
from sns_bot.src.utils import (
    is_dry_run,
    load_json,
    load_settings,
    logger,
    save_json,
    setup_logging,
)


def get_x_client() -> tweepy.Client:
    return tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )


def get_recent_trends() -> list[dict]:
    trends = load_json("trends_log.json")
    return trends[-20:] if trends else []


def check_duplicate_post(tweet_text: str, post_log: list) -> bool:
    recent_texts = {entry["text"] for entry in post_log[-50:]}
    return tweet_text in recent_texts


def post_tweet(text: str) -> dict:
    if is_dry_run():
        logger.info("[DRY RUN] Would post: %s", text)
        return {"id": "dry_run", "text": text}

    client = get_x_client()
    response = client.create_tweet(text=text)
    tweet_id = response.data["id"]
    logger.info("Posted tweet ID: %s", tweet_id)
    return {"id": tweet_id, "text": text}


def run(keyword_override: str | None = None):
    setup_logging()
    settings = load_settings()
    logger.info("Starting X poster (dry_run=%s)", is_dry_run())

    trends = get_recent_trends()
    if keyword_override:
        trends = [{"keyword": keyword_override, "source": "manual"}] + trends

    if not trends:
        logger.warning("No trends available. Exiting.")
        return

    post_log = load_json("post_log.json")

    max_attempts = 5
    for attempt in range(max_attempts):
        post = generate_post(trends)
        if not post:
            logger.warning("Failed to generate post (attempt %d)", attempt + 1)
            continue

        if check_duplicate_post(post["text"], post_log):
            logger.info("Duplicate detected, retrying (attempt %d)", attempt + 1)
            continue

        result = post_tweet(post["text"])

        entry = {
            "tweet_id": result["id"],
            "keyword": post["keyword"],
            "text": post["text"],
            "char_count": post["char_count"],
            "posted_at": datetime.now(timezone.utc).isoformat(),
            "dry_run": is_dry_run(),
            "metrics": {},
        }
        post_log.append(entry)
        save_json("post_log.json", post_log)
        logger.info("Post logged successfully")
        return

    logger.error("Failed to generate a unique post after %d attempts", max_attempts)


def main():
    parser = argparse.ArgumentParser(description="Post to X")
    parser.add_argument("--keyword", default=None, help="Override keyword")
    args = parser.parse_args()
    run(keyword_override=args.keyword)


if __name__ == "__main__":
    main()
