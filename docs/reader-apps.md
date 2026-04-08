# Reader Apps (Step 3)

Selected defaults:
- Android: Read You
- Windows: Fluent Reader

These are good baseline clients for personal RSS usage with custom feed URLs.

## Feed URL to use

With `privacy.mode: secret_path`, your feed path is:

- /output/feed-<your-token>.xml

When hosted on GitHub Pages, this usually becomes:

- https://<your-user>.github.io/<your-repo>/output/feed-<your-token>.xml

## Why this pairing

- Read You: modern Android reader, good for self-hosted/custom feeds.
- Fluent Reader: native-like Windows experience and straightforward feed management.

## Authentication note

The current implementation uses unguessable secret URL paths.
This is private enough for many personal workflows but is not strict auth.
If you want strict authenticated access, next step is adding an auth proxy layer.
