import os

from src.aggregator import resolve_output_path
from src.config import AppConfig, FeedSettings, PrivacySettings


def test_resolve_output_path_public():
    cfg = AppConfig(
        feed=FeedSettings(output_filename="feed.xml"),
        privacy=PrivacySettings(mode="public"),
        sources=[],
    )
    assert resolve_output_path(cfg) == "output/feed.xml"


def test_resolve_output_path_secret(monkeypatch):
    monkeypatch.setenv("NEWS_FEED_PRIVATE_TOKEN", "abc_123")
    cfg = AppConfig(
        feed=FeedSettings(output_filename="feed.xml"),
        privacy=PrivacySettings(mode="secret_path", token_env="NEWS_FEED_PRIVATE_TOKEN"),
        sources=[],
    )
    assert resolve_output_path(cfg) == "output/feed-abc_123.xml"


def test_resolve_output_path_secret_missing_env(monkeypatch):
    monkeypatch.delenv("NEWS_FEED_PRIVATE_TOKEN", raising=False)
    cfg = AppConfig(
        feed=FeedSettings(output_filename="feed.xml"),
        privacy=PrivacySettings(mode="secret_path", token_env="NEWS_FEED_PRIVATE_TOKEN"),
        sources=[],
    )

    try:
        resolve_output_path(cfg)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError when token env var is missing")
