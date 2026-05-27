---
title: 'How to Auto-Generate robots.txt and Sitemap in Astro'
date: '2026-05-05'
category: 'Astro'
layout: '../../layouts/PostLayoutEn.astro'
description: 'How to auto-generate sitemap.xml with the @astrojs/sitemap plugin and manually place robots.txt in your Astro site.'
---

## What I Wanted to Do

I wanted to add robots.txt and sitemap.xml to my Astro site for SEO.

## Environment

- Astro 5
- Cloudflare Pages

## Auto-Generating a Sitemap

### 1. Install the Plugin

```
npm install @astrojs/sitemap
```

### 2. Edit astro.config.mjs

```js
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://your-domain.com',
  integrations: [sitemap()],
});
```

### 3. Verify

```
https://your-domain.com/sitemap-index.xml
```

## Setting Up robots.txt

Save the following as `public/robots.txt`.

```
User-agent: *
Allow: /

Sitemap: https://your-domain.com/sitemap-index.xml
```

## Gotchas

- If `site` is not configured, the sitemap will not be generated
- Place robots.txt inside the `public/` directory
- Cloudflare may overwrite robots.txt, but this is generally not a problem

Once the sitemap is in place, also set up [SEO meta tags in Astro](/en/astro-seo-meta-tags) to round out your SEO configuration.

## Related Articles

- [How to Deploy Astro to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [How to Add a New Page in Astro](/en/astro-add-page)
- [Google Search Console HTML File Verification with Astro and Cloudflare Pages](/en/google-search-console-html-verification)
- [How to Read Cloudflare Pages Build Logs and Fix Errors](/en/cloudflare-pages-build-log)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
