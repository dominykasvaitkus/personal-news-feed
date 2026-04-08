from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .models import FeedItem


class Deduplicator:
    def __init__(self, state_file: str | Path = "state/seen_hashes.json") -> None:
        self._state_file = Path(state_file)
        self._seen: set[str] = set()
        self._load()

    def _load(self) -> None:
        if not self._state_file.exists():
            return
        raw = json.loads(self._state_file.read_text(encoding="utf-8"))
        self._seen = set(raw)

    def _save(self) -> None:
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state_file.write_text(
            json.dumps(sorted(self._seen), indent=2), encoding="utf-8"
        )

    @staticmethod
    def _item_hash(item: FeedItem) -> str:
        canonical = f"{item.url.strip().lower()}|{item.title.strip().lower()}"
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def filter_new(self, items: list[FeedItem]) -> list[FeedItem]:
        fresh: list[FeedItem] = []
        for item in items:
            h = self._item_hash(item)
            if h in self._seen:
                continue
            self._seen.add(h)
            fresh.append(item)
        self._save()
        return fresh
