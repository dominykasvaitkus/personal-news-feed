from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Literal, Union

import yaml
from pydantic import BaseModel, Field, ValidationError


ContentMode = Literal["link", "summary"]


class FeedSettings(BaseModel):
    title: str = "Personal Combined Feed"
    description: str = "Aggregated personal feed"
    link: str = "https://example.invalid"
    language: str = "en"
    max_items: int = 300
    content_mode: ContentMode = "summary"
    output_filename: str = "feed.xml"


PrivacyMode = Literal["public", "secret_path"]


class PrivacySettings(BaseModel):
    mode: PrivacyMode = "public"
    token_env: str = "NEWS_FEED_PRIVATE_TOKEN"


class BaseSourceConfig(BaseModel):
    id: str
    name: str
    type: str
    enabled: bool = True
    timeout_seconds: int = 20
    max_items: int | None = None


class RssSourceConfig(BaseSourceConfig):
    type: Literal["rss"]
    url: str


class WebSourceConfig(BaseSourceConfig):
    type: Literal["web"]
    url: str
    item_selector: str = "article a"
    title_selector: str | None = None
    summary_selector: str | None = None
    base_url: str | None = None


class EmailSourceConfig(BaseSourceConfig):
    type: Literal["email"]
    host: str
    port: int = 993
    username: str
    password_env: str
    folder: str = "INBOX"
    sender_allowlist: list[str] = Field(default_factory=list)


SourceConfig = Annotated[
    Union[RssSourceConfig, WebSourceConfig, EmailSourceConfig],
    Field(discriminator="type"),
]


class AppConfig(BaseModel):
    feed: FeedSettings
    privacy: PrivacySettings = PrivacySettings()
    sources: list[SourceConfig]


def load_config(path: str | Path = "config.yaml") -> AppConfig:
    cfg_path = Path(path)
    if not cfg_path.exists():
        raise FileNotFoundError(
            f"Configuration file {cfg_path} not found. Copy config.example.yaml to config.yaml."
        )

    raw: dict[str, Any] = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    try:
        return AppConfig.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid config format: {exc}") from exc
