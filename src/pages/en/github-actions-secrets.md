---
title: 'Managing Secrets in GitHub Actions'
date: '2026-05-13'
category: 'GitHub Actions'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['GitHub Actions', 'Secrets', 'セキュリティ', 'CI/CD']
en_tags: ['GitHub Actions', 'Secrets', 'security', 'CI/CD']
description: 'How to store API keys and other sensitive values in GitHub Actions Secrets and reference them securely inside workflow files.'
---
## How to Add a Secret

1. GitHub repository → "Settings" → "Secrets and variables" → "Actions"
2. "New repository secret" → enter Name and Secret value

## Reference in a Workflow

```yaml
steps:
  - name: Deploy
    env:
      API_KEY: ${{ secrets.API_KEY }}
    run: echo "Using the API key"
```

## Common Pitfalls

- Secret values are masked in logs — they won't appear in plain text
- Once saved, you can't view the value again — only overwrite it
- Secrets are not available in workflows triggered by forks

For managing environment variables in Cloudflare Pages, see [How to Set Environment Variables in Cloudflare Pages](/en/cloudflare-pages-env-variables). Also add `.env` to `.gitignore` — see [How to Set Up .gitignore](/en/git-gitignore-setup).

## Related Posts

- [GitHub Actions: Basic Auto-Deploy Setup](/en/github-actions-basic)
- [How to Set Up .gitignore](/en/git-gitignore-setup)
- [How to Set Environment Variables in Cloudflare Pages](/en/cloudflare-pages-env-variables)
- [Speed Up GitHub Actions Builds with Node.js npm Cache](/en/github-actions-node-cache)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
