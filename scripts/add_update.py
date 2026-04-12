from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser(description="Append a major update entry for RSS publishing.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--url", default="https://github.com/dominykasvaitkus/personal-news-feed/commits/main")
    parser.add_argument("--id", default="")
    parser.add_argument("--file", default="updates/major_updates.yaml")
    args = parser.parse_args()

    out_path = Path(args.file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    existing = []
    if out_path.exists():
        loaded = yaml.safe_load(out_path.read_text(encoding="utf-8"))
        if isinstance(loaded, list):
            existing = loaded

    now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    item_id = args.id.strip() or f"update-{now_iso}"

    new_item = {
        "id": item_id,
        "title": args.title.strip(),
        "summary": args.summary.strip(),
        "url": args.url.strip(),
        "published_at": now_iso,
    }

    existing.insert(0, new_item)
    out_path.write_text(yaml.safe_dump(existing, sort_keys=False, allow_unicode=False), encoding="utf-8")
    print(f"Added update entry: {item_id}")


if __name__ == "__main__":
    main()
