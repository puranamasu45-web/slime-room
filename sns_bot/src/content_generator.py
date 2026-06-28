import random
import re

from sns_bot.src.utils import load_settings, load_templates, logger


MAX_TWEET_LENGTH = 280


def make_hashtag(keyword: str) -> str:
    cleaned = re.sub(r"[\s　]+", "", keyword)
    cleaned = re.sub(r"[#＃]", "", cleaned)
    return cleaned


def generate_tweet(keyword: str, style: str | None = None) -> str | None:
    settings = load_settings()
    templates_data = load_templates()
    all_templates = templates_data.get("templates", {})

    config_style = style or settings.get("content", {}).get("template_style", "general")

    if config_style == "mixed":
        available_styles = list(all_templates.keys())
        config_style = random.choice(available_styles)

    style_templates = all_templates.get(config_style, all_templates.get("general", []))
    if not style_templates:
        logger.error("No templates found for style: %s", config_style)
        return None

    template = random.choice(style_templates)

    keyword_hashtag = make_hashtag(keyword)

    tweet = template.format(
        keyword=keyword,
        keyword_hashtag=keyword_hashtag,
    )

    if len(tweet) > MAX_TWEET_LENGTH:
        tweet = tweet[:MAX_TWEET_LENGTH - 1] + "…"

    return tweet


def select_keyword(trends: list[dict]) -> dict | None:
    if not trends:
        logger.warning("No trends available for content generation")
        return None
    return random.choice(trends[:10])


def generate_post(trends: list[dict], style: str | None = None) -> dict | None:
    selected = select_keyword(trends)
    if not selected:
        return None

    keyword = selected["keyword"]
    tweet = generate_tweet(keyword, style)
    if not tweet:
        return None

    logger.info("Generated tweet (%d chars) for keyword: %s", len(tweet), keyword)
    return {
        "keyword": keyword,
        "text": tweet,
        "char_count": len(tweet),
    }
