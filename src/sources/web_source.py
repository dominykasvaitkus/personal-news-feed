from __future__ import annotations

from datetime import timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date

from ..config import ContentMode, WebSourceConfig
from ..models import FeedItem, utc_now
from .base import SourceAdapter


class WebSourceAdapter(SourceAdapter):
    def __init__(self, config: WebSourceConfig, content_mode: ContentMode) -> None:
        self.config = config
        self.content_mode = content_mode

    def fetch_items(self) -> list[FeedItem]:
        response = requests.get(
            self.config.url,
            timeout=self.config.timeout_seconds,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        nodes = soup.select(self.config.item_selector)
        items: list[FeedItem] = []
        for node in nodes:
            title_node = node
            if self.config.title_selector:
                selected = node.select_one(self.config.title_selector)
                if selected is not None:
                    title_node = selected

            link_node = title_node if title_node.get("href") else title_node.find("a", href=True)
            if link_node is None and node.get("href"):
                link_node = node

            href = link_node.get("href") if link_node else None
            if not href:
                continue
            base_url = self.config.base_url or self.config.url
            final_url = urljoin(base_url, href)
            title = title_node.get_text(strip=True)
            if not title:
                continue

            summary: str | None = None
            if self.content_mode == "summary" and self.config.summary_selector:
                summary_node = node.select_one(self.config.summary_selector)
                if summary_node:
                    summary = summary_node.get_text(strip=True)

            published_at = utc_now()
            time_node = node.find_parent().find("time") if node.find_parent() else None
            if time_node and time_node.get("datetime"):
                try:
                    published_at = parse_date(time_node["datetime"]).astimezone(timezone.utc)
                except Exception:  # noqa: BLE001
                    pass

            items.append(
                FeedItem(
                    source_id=self.config.id,
                    source_type="web",
                    title=title,
                    url=final_url,
                    summary=summary,
                    published_at=published_at,
                    external_id=None,
                )
            )
        return items
