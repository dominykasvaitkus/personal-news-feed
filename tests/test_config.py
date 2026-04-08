import textwrap

from src.config import load_config


def test_load_config(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent(
            """
            feed:
              title: Test Feed
              description: Test
              link: https://example.com
              language: en
              max_items: 10
              content_mode: summary
            sources:
              - id: one
                name: One
                type: rss
                url: https://example.com/feed.xml
            """
        ).strip(),
        encoding="utf-8",
    )

    app_cfg = load_config(cfg)
    assert app_cfg.feed.title == "Test Feed"
    assert len(app_cfg.sources) == 1
