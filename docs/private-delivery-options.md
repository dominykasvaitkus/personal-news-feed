# Private Feed Delivery Options

This project supports two practical privacy modes now, with one stronger option planned once reader apps are chosen.

## Option 1: Public URL (default)

- Config: `privacy.mode: public`
- Output: `output/feed.xml`
- Pros: simplest setup, universal reader compatibility.
- Cons: not private.

## Option 2: Secret Path URL (implemented)

- Config: `privacy.mode: secret_path`
- Requires env var: `NEWS_FEED_PRIVATE_TOKEN` (or custom `privacy.token_env`)
- Output pattern: `output/feed-<token>.xml`
- Pros: easy, no extra hosting layer, works with most readers.
- Cons: security by unguessable URL, not true authentication.

## Option 3: Authenticated Proxy (recommended for strict privacy)

- Not implemented in code yet because final design depends on selected Android/Windows readers.
- Typical approach:
  1. Keep feed generation in GitHub Actions.
  2. Serve feed behind a free auth-capable proxy endpoint.
  3. Use per-user token or basic auth if reader supports it.
- Pros: real access control.
- Cons: reader compatibility varies.

## Config Examples

```yaml
privacy:
  mode: public
```

```yaml
privacy:
  mode: secret_path
  token_env: NEWS_FEED_PRIVATE_TOKEN
```
