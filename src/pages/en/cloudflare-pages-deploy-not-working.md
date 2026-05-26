---
title: 'Cloudflare Pages GitHub Auto-Deploy Not Working: How to Fix It'
date: '2026-05-04'
category: 'Cloudflare'
layout: '../../layouts/PostLayoutEn.astro'
---

## Symptoms

Git push does not trigger a new deployment on Cloudflare Pages.
No new entries appear in the Deployments tab.
You may also see this warning message:

```
This project is disconnected from your Git account.
This may cause deployments to fail.
```

## Cause 1: Cloudflare Lost Connection to GitHub

### Fix

1. Click "Manage" under Git repository in Settings
2. Re-authenticate your GitHub account
3. Force a new deployment by pushing an empty commit

```
git commit --allow-empty -m "force deploy"
git push
```

## Cause 2: Old Commit Being Deployed

```
git commit --allow-empty -m "force deploy"
git push
```

## Cause 3: Build Error

Open the build log from the Deployments tab and look for lines starting with `[ERROR]` or `Failed`.

## Key Points

- Empty commit push is the most reliable way to force redeployment
- Always check the build log first

## Related Articles

- [Cloudflare Pages Build Log Guide](/posts/cloudflare-pages-build-log)
- [How to Deploy Astro to Cloudflare Pages](/en/docker-install-windows)


## Recommended VPS / Cloud Hosting

If you're looking for high-performance cloud infrastructure, Cherry Servers offers developer-friendly VPS and dedicated servers optimized for AI, Web3, and production workloads.

<a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a>