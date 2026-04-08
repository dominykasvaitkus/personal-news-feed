from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import FeedItem


class SourceAdapter(ABC):
    @abstractmethod
    def fetch_items(self) -> list[FeedItem]:
        raise NotImplementedError
