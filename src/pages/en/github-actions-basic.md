---
title: 'GitHub Actions: How to Set Up Basic Auto-Deploy'
date: '2026-05-10'
category: 'GitHub Actions'
---

## How It Works

```
Push to GitHub
→ GitHub Actions triggers
→ Runs the YAML workflow file in .github/workflows/
→ Build, test, deploy automatically
```

## Basic Workflow Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install dependencies
        run: npm install

      - name: Build
        run: npm run build
```

Push to GitHub and check the Actions tab to see it running.

## Common Trigger Options

```yaml
# On push to main
on:
  push:
    branches: [main]

# On pull request
on:
  pull_request:
    branches: [main]

# Manual trigger
on:
  workflow_dispatch:
```

## Key Points

- The `.github/workflows/` folder name must be exact
- YAML indentation matters — use 2 spaces
- Check the Actions tab for logs when something fails
- Store secrets in Settings → Secrets and use `${{ secrets.MY_KEY }}`

## Related Articles

- [How to Create Your First GitHub Repository and Push](/posts/github-first-push)
- [GitHub Actions: Using Secrets for Sensitive Data](/posts/github-actions-secrets)
- [GitHub Actions: Speed Up Builds with Node.js Cache](/posts/github-actions-node-cache)
