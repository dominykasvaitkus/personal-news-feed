from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class FeedItem:
    source_id: str
    source_type: str
    title: str
    url: str
    summary: Optional[str]
    published_at: datetime
    external_id: Optional[str] = None

    def unique_fallback(self) -> str:
        return f"{self.source_id}|{self.title.strip().lower()}|{self.url.strip()}"
