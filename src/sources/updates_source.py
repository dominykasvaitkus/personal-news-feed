from __future__ import annotations

from datetime import timezone
from pathlib import Path

import yaml
from dateutil.parser import parse as parse_date

from ..config import ContentMode, UpdatesSourceConfig
from ..models import FeedItem, utc_now
from .base import SourceAdapter


class UpdatesSourceAdapter(SourceAdapter):
    def __init__(self, config: UpdatesSourceConfig, content_mode: ContentMode) -> None:
        self.config = config
        self.content_mode = content_mode

    def fetch_items(self) -> list[FeedItem]:
        path = Path(self.config.file_path)
        if not path.exists():
            return []

        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        updates = raw if isinstance(raw, list) else []

        items: list[FeedItem] = []
        for upd in updates:
            if not isinstance(upd, dict):
                continue
            title = str(upd.get("title", "")).strip()
            url = str(upd.get("url", "")).strip()
            if not title or not url:
                continue

            summary: str | None = None
            if self.content_mode == "summary":
                summary = str(upd.get("summary", "")).strip() or None

            published_at = utc_now()
            published_raw = str(upd.get("published_at", "")).strip()
            if published_raw:
                try:
                    published_at = parse_date(published_raw).astimezone(timezone.utc)
                except Exception:  # noqa: BLE001
                    pass

            external_id = str(upd.get("id", "")).strip() or None

            items.append(
                FeedItem(
                    source_id=self.config.id,
                    source_type="updates",
                    title=title,
                    url=url,
                    summary=summary,
                    published_at=published_at,
                    external_id=external_id,
                )
            )

        return items
