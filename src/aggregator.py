from __future__ import annotations

import logging
import os
import re
from collections.abc import Iterable

from .config import AppConfig, EmailSourceConfig, RssSourceConfig, WebSourceConfig, load_config
from .dedup import Deduplicator
from .feed_output import write_rss
from .models import FeedItem
from .sources.base import SourceAdapter
from .sources.email_source import EmailSourceAdapter
from .sources.rss_source import RssSourceAdapter
from .sources.web_source import WebSourceAdapter
from .utils import run_with_retries, setup_logging

logger = logging.getLogger(__name__)


def build_adapter(config: RssSourceConfig | WebSourceConfig | EmailSourceConfig, content_mode: str) -> SourceAdapter:
    if isinstance(config, RssSourceConfig):
        return RssSourceAdapter(config, content_mode)
    if isinstance(config, WebSourceConfig):
        return WebSourceAdapter(config, content_mode)
    if isinstance(config, EmailSourceConfig):
        return EmailSourceAdapter(config, content_mode)
    raise TypeError(f"Unsupported source config type: {type(config)!r}")


def gather_items(config: AppConfig) -> list[FeedItem]:
    all_items: list[FeedItem] = []
    for source in config.sources:
        if not source.enabled:
            logger.info("Skipping disabled source: %s", source.id)
            continue

        adapter = build_adapter(source, config.feed.content_mode)

        def fetch() -> list[FeedItem]:
            return adapter.fetch_items()

        try:
            source_items = run_with_retries(fetch, retries=2)
            if source.max_items is not None and source.max_items >= 0:
                source_items = source_items[: source.max_items]
            logger.info("Fetched %s items from source %s", len(source_items), source.id)
            all_items.extend(source_items)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed source %s: %s", source.id, exc)

    return sorted_items(all_items)


def sorted_items(items: Iterable[FeedItem]) -> list[FeedItem]:
    return sorted(items, key=lambda item: item.published_at, reverse=True)


def resolve_output_path(config: AppConfig) -> str:
    file_name = config.feed.output_filename
    if config.privacy.mode == "secret_path":
        token = os.getenv(config.privacy.token_env, "").strip()
        if not token:
            raise ValueError(
                f"Privacy mode 'secret_path' requires env var {config.privacy.token_env}."
            )
        safe_token = re.sub(r"[^a-zA-Z0-9_-]", "", token)
        if not safe_token:
            raise ValueError("Private token contained no valid characters.")
        file_name = f"feed-{safe_token}.xml"
    return f"output/{file_name}"


def main() -> None:
    setup_logging()
    config_path = os.getenv("NEWS_FEED_CONFIG_PATH", "config.yaml")
    state_file = os.getenv("NEWS_FEED_STATE_FILE", "state/seen_hashes.json")

    config = load_config(config_path)
    items = gather_items(config)

    dedup = Deduplicator(state_file=state_file)
    fresh_items = dedup.filter_new(items)
    logger.info("Items after deduplication: %s", len(fresh_items))

    output_path = resolve_output_path(config)
    write_rss(config.feed, fresh_items, output_path=output_path)
    logger.info("Wrote RSS output to %s", output_path)


if __name__ == "__main__":
    main()
