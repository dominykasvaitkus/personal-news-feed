# GitHub Setup (Step 2)

This repo is ready for scheduled feed generation, but GitHub-side setup requires a remote repository.

## 1. Initialize local git repo (if missing)

```powershell
git init
git add .
git commit -m "Initial personal news feed setup"
```

## 2. Create a GitHub repository and connect remote

Use GitHub web UI to create an empty repository, then run:

```powershell
git remote add origin https://github.com/<your-user>/<your-repo>.git
git branch -M main
git push -u origin main
```

## 3. Add required repository secrets

In GitHub: Settings -> Secrets and variables -> Actions -> New repository secret

Required:
- NEWS_FEED_PRIVATE_TOKEN: long random token used in secret path mode

Optional (only if email source is enabled):
- NEWS_FEED_EMAIL_PASSWORD: email app password

## 4. Trigger workflow manually once

In GitHub: Actions -> Build RSS Feed -> Run workflow

Expected output commit:
- output/feed-<token>.xml
- state/seen_hashes.json

## 5. Enable schedule

The workflow is already configured to run every 3 hours via cron.
