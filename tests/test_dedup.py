from datetime import timezone

from src.dedup import Deduplicator
from src.models import FeedItem, utc_now


def test_dedup_filters_duplicates(tmp_path):
    state_file = tmp_path / "seen.json"
    dedup = Deduplicator(state_file)

    item1 = FeedItem(
        source_id="a",
        source_type="rss",
        title="Story",
        url="https://example.com/story",
        summary="x",
        published_at=utc_now().astimezone(timezone.utc),
    )
    item2 = FeedItem(
        source_id="b",
        source_type="web",
        title="Story",
        url="https://example.com/story",
        summary="y",
        published_at=utc_now().astimezone(timezone.utc),
    )

    fresh = dedup.filter_new([item1, item2])
    assert len(fresh) == 1
