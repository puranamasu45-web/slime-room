#!/usr/bin/env python3
"""X (Twitter) 自動投稿スクリプト"""

import json
import os
import sys
import random
from pathlib import Path

import tweepy


def get_client():
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    return client


def load_posts(filepath="templates/posts.json"):
    path = Path(__file__).parent / filepath
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def post_random(client, posts):
    candidates = [p for p in posts if not p.get("posted")]
    if not candidates:
        print("全テンプレ投稿済み。リセットするか新しいネタ追加してな。")
        sys.exit(0)

    entry = random.choice(candidates)
    text = entry["text"]

    response = client.create_tweet(text=text)
    tweet_id = response.data["id"]
    print(f"投稿完了: {text[:50]}... (ID: {tweet_id})")
    return tweet_id


def post_text(client, text):
    response = client.create_tweet(text=text)
    tweet_id = response.data["id"]
    print(f"投稿完了: {text[:50]}... (ID: {tweet_id})")
    return tweet_id


def main():
    client = get_client()

    if len(sys.argv) > 1 and sys.argv[1] == "--text":
        text = " ".join(sys.argv[2:])
        post_text(client, text)
    else:
        posts = load_posts()
        post_random(client, posts)


if __name__ == "__main__":
    main()
