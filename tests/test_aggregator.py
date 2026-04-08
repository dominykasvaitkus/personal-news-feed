from datetime import datetime, timezone

from src.aggregator import sorted_items
from src.models import FeedItem


def test_sorted_items_descending():
    old = FeedItem(
        source_id="one",
        source_type="rss",
        title="Old",
        url="https://example.com/old",
        summary=None,
        published_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    new = FeedItem(
        source_id="one",
        source_type="rss",
        title="New",
        url="https://example.com/new",
        summary=None,
        published_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )

    result = sorted_items([old, new])
    assert result[0].title == "New"
