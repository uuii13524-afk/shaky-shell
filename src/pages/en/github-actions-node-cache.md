---
title: 'Speed Up GitHub Actions Builds with Node.js npm Cache'
date: '2026-05-15'
category: 'GitHub Actions'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['GitHub Actions', 'Node.js', 'キャッシュ', 'CI/CD']
en_tags: ['GitHub Actions', 'Node.js', 'cache', 'CI/CD']
description: 'How to enable npm caching in GitHub Actions with actions/setup-node to reduce CI build times. Includes npm install vs npm ci comparison.'
---
## Config with Cache Enabled

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-node@v4
    with:
      node-version: '22'
      cache: 'npm'      # This is all you need
  - run: npm ci
  - run: npm run build
```

## npm install vs npm ci

| | npm install | npm ci |
|--|--|--|
| Speed | Normal | Faster |
| package-lock.json | May update it | Never updates it |
| Use case | Development | CI/CD |

## Common Pitfalls

- Adding `cache: 'npm'` is all it takes — no extra configuration needed
- Cache is invalidated when `package-lock.json` changes

For the overall workflow structure, see [GitHub Actions: Basic Auto-Deploy Setup](/en/github-actions-basic).

## Related Posts

- [GitHub Actions: Basic Auto-Deploy Setup](/en/github-actions-basic)
- [Managing Secrets in GitHub Actions](/en/github-actions-secrets)
- [Fix npm Cache Problems](/en/npm-cache-clear)
- [npm vs yarn: Differences and When to Use Each](/en/npm-vs-yarn)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
