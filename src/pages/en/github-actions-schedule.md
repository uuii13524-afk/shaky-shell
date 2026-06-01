---
title: 'How to Schedule Workflows in GitHub Actions (cron)'
date: '2026-05-19'
category: 'GitHub Actions'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['GitHub Actions', 'スケジュール', 'cron', 'CI/CD']
en_tags: ['GitHub Actions', 'schedule', 'cron', 'CI/CD']
description: 'How to set up scheduled (cron) triggers in GitHub Actions. Includes UTC time conversion tips and how to also allow manual runs.'
---
## Basic Setup

```yaml
on:
  schedule:
    - cron: '0 9 * * *'    # Daily at 09:00 UTC
```

## Common cron Examples

```
0 9 * * *       # Daily at 09:00 UTC
0 0 * * 1       # Every Monday at 00:00 UTC
0 9 1 * *       # 1st of every month at 09:00 UTC
*/30 * * * *    # Every 30 minutes
```

## UTC Time Conversion

GitHub Actions cron runs in UTC, which is 5–9 hours behind most of the world.

```
09:00 JST = 00:00 UTC → cron: '0 0 * * *'
```

## Also Allow Manual Runs

```yaml
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
```

## Common Pitfalls

- Cron runs in UTC — double-check the offset for your timezone
- Repositories with no recent activity may have scheduled workflows disabled by GitHub

## Related Posts

- [GitHub Actions: Basic Auto-Deploy Setup](/en/github-actions-basic)
- [Managing Secrets in GitHub Actions](/en/github-actions-secrets)
- [Speed Up GitHub Actions Builds with Node.js npm Cache](/en/github-actions-node-cache)
- [How to Push Your First Repository to GitHub](/en/github-first-push)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
