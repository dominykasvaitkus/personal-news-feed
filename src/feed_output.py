from __future__ import annotations

from feedgen.feed import FeedGenerator

from .config import FeedSettings
from .models import FeedItem


def write_rss(feed: FeedSettings, items: list[FeedItem], output_path: str = "output/feed.xml") -> None:
    fg = FeedGenerator()
    fg.title(feed.title)
    fg.description(feed.description)
    fg.link(href=feed.link, rel="alternate")
    fg.language(feed.language)

    for item in items[: feed.max_items]:
        entry = fg.add_entry(order="append")
        entry.id(item.external_id or item.url)
        entry.title(item.title)
        entry.link(href=item.url)
        entry.pubDate(item.published_at)
        if item.summary:
            entry.description(item.summary)

    fg.rss_file(output_path)
