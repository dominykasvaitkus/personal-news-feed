# Personal News Feed (Python)

A Python-first personal feed aggregator that combines multiple source types into one RSS feed.

## Features

- Combine sources into one feed:
  - RSS feeds
  - Websites (CSS-selector based extraction)
  - Email newsletters (IMAP inbox polling)
- Content mode toggle:
  - `link`: title + link only
  - `summary`: title + link + snippet/summary
- Privacy mode toggle:
  - `public`: writes `output/feed.xml`
  - `secret_path`: writes `output/feed-<token>.xml`
- Deduplication across all sources
- Scheduled automation with GitHub Actions (every 3 hours by default)
- PowerShell helper script for virtualenv-first workflow

## Quick Start (Local)

1. Bootstrap environment and dependencies (Windows PowerShell):

```powershell
.\scripts\dev.ps1 -Task bootstrap
```

2. Copy starter config:

```powershell
.\scripts\dev.ps1 -Task copy-config
```

3. Set privacy token (only needed for `privacy.mode: secret_path`):

```powershell
$env:NEWS_FEED_PRIVATE_TOKEN="choose-a-long-random-token"
```

4. If using email sources, set your password as an environment variable:

```powershell
$env:NEWS_FEED_EMAIL_PASSWORD="your-app-password"
```

5. Run:

```powershell
.\scripts\dev.ps1 -Task run
```

Output file:

- `output/feed.xml` for public mode
- `output/feed-<token>.xml` for secret path mode

## Configuration

All settings are in `config.yaml`.

Use `config.starter.yaml` as your default source set. It includes real RSS feeds and tuned website selectors (disabled by default).

- `feed.content_mode`
  - `link` for lightweight entries
  - `summary` for richer entries

- `privacy.mode`
  - `public`
  - `secret_path` (requires token env variable)

- `sources`
  - `type: rss` with `url`
  - `type: web` with `item_selector`, `title_selector`, and optional `summary_selector`
  - `type: email` with IMAP details

## Helper Script Tasks

- `bootstrap`: create `.venv`, upgrade pip, install requirements
- `install`: install requirements into `.venv`
- `test`: run pytest through `.venv`
- `run`: run feed generation through `.venv`
- `copy-config`: copy starter config to `config.yaml`

## GitHub Actions Automation

Workflow file:

- `.github/workflows/build-feed.yml`

What it does:

1. Runs every 3 hours.
2. Installs dependencies.
3. Copies `config.starter.yaml` to `config.yaml`.
4. Runs feed generation.
5. Commits updated generated feed output and dedup state.

## Step 2: GitHub Setup

Follow `docs/github-setup.md`.
It covers repository creation/push, secrets setup, and manual workflow trigger.

## Step 3: Reader App Defaults

Selected defaults:

- Android: Read You
- Windows: Fluent Reader

See `docs/reader-apps.md` for URL and setup details.

## Privacy Notes

Current implementation supports `public` and `secret_path` modes.
See `docs/private-delivery-options.md` for tradeoffs and the authenticated-proxy option.

## Testing

```powershell
.\scripts\dev.ps1 -Task test
```

## Next Planned Enhancements

- Reader-specific authenticated proxy option
- Better website extraction presets per site
- Email message-id state tracking for incremental polling
- Per-source rate limits and caching
