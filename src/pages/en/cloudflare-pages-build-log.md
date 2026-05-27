---
title: 'How to Read Cloudflare Pages Build Logs and Fix Errors'
date: '2026-05-09'
category: 'Cloudflare'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Cloudflare', 'Cloudflare Pages', 'デプロイ', 'ビルドエラー']
en_tags: ['Cloudflare', 'Cloudflare Pages', 'deploy', 'build error']
description: 'How to open Cloudflare Pages build logs and fix common build errors. Covers the Deployments tab, log navigation, and typical failure causes.'
---
## How to Open Build Logs

1. Cloudflare dashboard → Workers & Pages
2. Select your project → Deployments tab
3. Click the target deployment → View build logs

## What a Successful Build Looks Like

```
Cloning repository...
Installing project dependencies
Executing user command
Uploading...
Success: Your site was deployed
```

## Common Errors and Fixes

### Astro.glob is not a function

Deprecated in Astro 5. Replace with `import.meta.glob()`.

### Cannot find module

```bash
npm install @astrojs/sitemap
```

### Old commit being deployed

```bash
git commit --allow-empty -m "force deploy"
git push
```

## Common Pitfalls

- The error cause appears just before the `Failed` line — search for `ERROR` with Ctrl+F
- If no new deployment appears at all, the issue may be a GitHub disconnection rather than a build error

For disconnection issues, see [Cloudflare Pages Disconnected from GitHub: Fix](/en/cloudflare-github-disconnect).

## Related Posts

- [Cloudflare Pages Disconnected from GitHub: Fix](/en/cloudflare-github-disconnect)
- [Cloudflare Pages Auto-Deploy Not Working: Fix](/en/cloudflare-pages-deploy-not-working)
- [Deploy Astro to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [Auto-generate robots.txt and sitemap in Astro](/en/astro-sitemap-robots)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
