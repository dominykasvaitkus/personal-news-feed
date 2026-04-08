from __future__ import annotations

from datetime import datetime, timezone

import feedparser

from ..config import ContentMode, RssSourceConfig
from ..models import FeedItem
from .base import SourceAdapter


class RssSourceAdapter(SourceAdapter):
    def __init__(self, config: RssSourceConfig, content_mode: ContentMode) -> None:
        self.config = config
        self.content_mode = content_mode

    def fetch_items(self) -> list[FeedItem]:
        parsed = feedparser.parse(self.config.url)
        items: list[FeedItem] = []
        for entry in getattr(parsed, "entries", []):
            title = getattr(entry, "title", "(untitled)")
            link = getattr(entry, "link", "")
            if not link:
                continue
            summary: str | None = None
            if self.content_mode == "summary":
                summary = getattr(entry, "summary", None)

            published = datetime.now(timezone.utc)
            published_parsed = getattr(entry, "published_parsed", None)
            if published_parsed:
                published = datetime(*published_parsed[:6], tzinfo=timezone.utc)

            items.append(
                FeedItem(
                    source_id=self.config.id,
                    source_type="rss",
                    title=title.strip(),
                    url=link.strip(),
                    summary=summary.strip() if isinstance(summary, str) else None,
                    published_at=published,
                    external_id=getattr(entry, "id", None),
                )
            )
        return items
