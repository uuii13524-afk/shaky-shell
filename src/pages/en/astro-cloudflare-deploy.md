---
title: 'How to Deploy Astro to Cloudflare Pages'
date: '2026-05-03'
category: 'Astro'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Step-by-step guide to deploying an Astro site to Cloudflare Pages, including GitHub integration and custom domain setup.'
---

## What I Wanted to Do

I wanted to publish my Astro site using Cloudflare Pages.

## Environment

- Windows 11
- Node.js
- Astro
- GitHub
- Cloudflare Pages

## Steps

### 1. Install Astro

```
npm create astro@latest
```

### 2. Verify Locally

```
cd project-name
npm run dev
```

If the Astro welcome screen appears at http://localhost:4321, you are good to go.

### 3. Push to GitHub

If this is your first time pushing to GitHub, see [How to Push to GitHub for the First Time](/en/github-first-push).

```
git init
git add .
git commit -m "first commit"
git remote add origin YOUR_GITHUB_URL
git push -u origin main
```

### 4. Connect to Cloudflare Pages

1. Go to "Workers & Pages" → "Create application"
2. Click "Looking to deploy Pages? Get started" at the bottom of the screen
3. Click "Import an existing Git repository" → "Get started"
4. Select your repository
5. Choose "Astro" from the Framework preset dropdown
6. Click "Save and Deploy"

## Gotchas

- Clicking "Create application" opens the Workers screen. For Pages, use "Get started" at the bottom of the page
- Selecting the Astro framework preset automatically fills in the build settings
- If you need to set environment variables after deployment, see [How to Set Environment Variables in Cloudflare Pages](/en/cloudflare-pages-env-variables)

## Related Articles

- [Full Steps to Set an Xserver Domain as a Cloudflare Pages Custom Domain](/en/xserver-cloudflare-full-setup)
- [Cloudflare Pages GitHub Auto-Deploy Not Working: How to Fix It](/en/cloudflare-pages-deploy-not-working)
- [How to Read Cloudflare Pages Build Logs and Fix Errors](/en/cloudflare-pages-build-log)
- [How to Add a New Page in Astro](/en/astro-add-page)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
