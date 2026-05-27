---
title: 'GitHub Actions: How to Set Up Basic Auto-Deploy'
date: '2026-05-10'
category: 'GitHub Actions'
layout: '../../layouts/PostLayoutEn.astro'
---

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
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm install
      - run: npm run build
```

## Common Triggers

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
```

## Key Points

- The `.github/workflows/` folder name must be exact
- YAML indentation matters — use 2 spaces
- Store secrets in Settings → Secrets

## Related Articles

- [GitHub Actions: Using Secrets](/posts/github-actions-secrets)
- [GitHub Actions: Node.js Cache](/posts/github-actions-node-cache)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
