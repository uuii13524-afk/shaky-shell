---
title: 'How to Fix Cloudflare Pages Disconnected from GitHub'
date: '2026-05-01'
category: 'Cloudflare'
layout: '../../layouts/PostLayoutEn.astro'
description: 'How to fix and reconnect Cloudflare Pages when it loses its GitHub connection and deployments stop triggering on push.'
---

## Symptoms

Git push does not get reflected on Cloudflare Pages. The following message appears in the dashboard:

```
This project is disconnected from your Git account.
This may cause deployments to fail.
```

## Environment

- Cloudflare Pages
- GitHub
- Astro

## What I Tried

- Ran git push but changes were not reflected
- Checked the Deployments tab but no new deployments appeared

## Cause

The connection between Cloudflare and GitHub had been severed.

## Solution

1. Open the affected project in the Cloudflare dashboard
2. Go to Settings → click "Manage" under Git repository
3. Re-authenticate your GitHub account
4. Push an empty commit to force a deployment

```
git commit --allow-empty -m "force deploy"
git push
```

## Preventing Recurrence

When a deployment is not reflected, first check the logs in the Deployments tab. For help reading build logs, see [How to Read Cloudflare Pages Build Logs and Fix Errors](/en/cloudflare-pages-build-log).

## Related Articles

- [Cloudflare Pages GitHub Auto-Deploy Not Working: How to Fix It](/en/cloudflare-pages-deploy-not-working)
- [How to Read Cloudflare Pages Build Logs and Fix Errors](/en/cloudflare-pages-build-log)
- [How to Deploy Astro to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [Full Steps to Set an Xserver Domain as a Cloudflare Pages Custom Domain](/en/xserver-cloudflare-full-setup)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
