---
title: 'How to Set Environment Variables in Cloudflare Pages'
date: '2026-05-13'
category: 'Cloudflare'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Cloudflare', 'Cloudflare Pages', '環境変数', 'デプロイ']
en_tags: ['Cloudflare', 'Cloudflare Pages', 'environment variables', 'deploy']
description: 'How to add environment variables like API keys in Cloudflare Pages dashboard, and how to reference them in Astro or other frameworks.'
---
## How to Set Variables

1. Cloudflare dashboard → project → "Settings" → "Variables and Secrets"
2. "Add variable" → enter name and value → save

## Reference in Code

```javascript
// In Astro
const apiKey = import.meta.env.MY_API_KEY;
```

## Local Development

Create a `.env` file:

```
MY_API_KEY=your-local-key
```

Add `.env` to `.gitignore` to avoid committing it.

## Common Pitfalls

- After adding a variable, a redeploy is required for it to take effect
- Never commit `.env` to your repository

To exclude `.env` from Git, see [How to Set Up .gitignore](/en/git-gitignore-setup). For managing secrets in GitHub Actions workflows, see [Managing Secrets in GitHub Actions](/en/github-actions-secrets).

## Related Posts

- [Cloudflare Pages Auto-Deploy Not Working](/en/cloudflare-pages-deploy-not-working)
- [How to Set Up .gitignore](/en/git-gitignore-setup)
- [Managing Secrets in GitHub Actions](/en/github-actions-secrets)
- [How to Deploy an Astro Site to Cloudflare Pages](/en/astro-cloudflare-deploy)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
