from __future__ import annotations

import email
import imaplib
import os
import re
from datetime import timezone
from email.message import Message
from html import unescape

from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date

from ..config import ContentMode, EmailSourceConfig
from ..models import FeedItem, utc_now
from .base import SourceAdapter

URL_RE = re.compile(r"https?://[^\s\"'<>]+")


class EmailSourceAdapter(SourceAdapter):
    def __init__(self, config: EmailSourceConfig, content_mode: ContentMode) -> None:
        self.config = config
        self.content_mode = content_mode

    def fetch_items(self) -> list[FeedItem]:
        password = os.getenv(self.config.password_env)
        if not password:
            raise ValueError(
                f"Missing environment variable for email password: {self.config.password_env}"
            )

        conn = imaplib.IMAP4_SSL(self.config.host, self.config.port)
        conn.login(self.config.username, password)
        conn.select(self.config.folder)

        status, data = conn.search(None, "ALL")
        if status != "OK":
            conn.logout()
            return []

        ids = data[0].split()[-200:]
        items: list[FeedItem] = []
        for msg_id in ids:
            fetch_status, payload = conn.fetch(msg_id, "(RFC822)")
            if fetch_status != "OK" or not payload:
                continue

            raw = payload[0][1]
            if not isinstance(raw, (bytes, bytearray)):
                continue

            msg = email.message_from_bytes(raw)
            sender = msg.get("From", "")
            if self.config.sender_allowlist and not any(
                sender_fragment.lower() in sender.lower()
                for sender_fragment in self.config.sender_allowlist
            ):
                continue

            title = msg.get("Subject", "Newsletter")
            url, summary = self._extract_content(msg)
            if not url:
                continue

            published = utc_now()
            date_header = msg.get("Date")
            if date_header:
                try:
                    published = parse_date(date_header).astimezone(timezone.utc)
                except Exception:  # noqa: BLE001
                    pass

            if self.content_mode == "link":
                summary = None

            items.append(
                FeedItem(
                    source_id=self.config.id,
                    source_type="email",
                    title=title.strip(),
                    url=url,
                    summary=summary,
                    published_at=published,
                    external_id=msg.get("Message-ID"),
                )
            )

        conn.logout()
        return items

    def _extract_content(self, msg: Message) -> tuple[str | None, str | None]:
        html_part: str | None = None
        text_part: str | None = None

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype not in {"text/plain", "text/html"}:
                    continue
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                text = payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
                if ctype == "text/html" and not html_part:
                    html_part = text
                elif ctype == "text/plain" and not text_part:
                    text_part = text
        else:
            payload = msg.get_payload(decode=True) or b""
            text = payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
            if msg.get_content_type() == "text/html":
                html_part = text
            else:
                text_part = text

        url: str | None = None
        summary: str | None = None
        if html_part:
            soup = BeautifulSoup(html_part, "html.parser")
            first_link = soup.find("a", href=True)
            if first_link:
                url = first_link.get("href")
            summary = soup.get_text(" ", strip=True)
            summary = unescape(summary[:500]) if summary else None

        if not url and text_part:
            match = URL_RE.search(text_part)
            url = match.group(0) if match else None
            if self.content_mode == "summary":
                summary = text_part.strip()[:500] or None

        return url, summary
