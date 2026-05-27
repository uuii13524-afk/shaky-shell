---
title: 'Google Search Console HTML File Verification with Astro + Cloudflare Pages'
date: '2026-05-04'
category: 'SEO'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['SEO', 'Google Search Console', 'Astro', 'Cloudflare Pages']
en_tags: ['SEO', 'Google Search Console', 'Astro', 'Cloudflare Pages']
description: 'How to verify your Astro + Cloudflare Pages site in Google Search Console using the HTML file method, from downloading the file to submitting a sitemap.'
---
## What I Wanted to Do

Register an Astro site hosted on Cloudflare Pages with Google Search Console.

## Steps

### 1. Start Ownership Verification in Search Console

1. Open https://search.google.com/search-console
2. Enter your site URL under "URL prefix" → "Continue"
3. Select "HTML file" as the verification method
4. Download the verification HTML file

### 2. Place the File in the public Folder

```
your-project/public/googleXXXXXXXXXXXXXXXX.html
```

Place it in `public/`, not `src/`.

### 3. Push and Deploy

```bash
git add .
git commit -m "add google search console verification"
git push
```

### 4. Verify in Search Console

After the deployment completes, click "Verify".

### 5. Submit Sitemap

Left menu: "Sitemaps" → enter `sitemap-index.xml` → "Submit"

## Common Pitfalls

- The HTML file must go in `public/` — placing it in `src/` won't work
- Clicking "Verify" before the deployment completes will fail
- Don't delete the verification file after confirming — Search Console checks it periodically

After verification, generate and submit a sitemap with [Generate sitemap.xml and robots.txt in Astro](/en/astro-sitemap-robots).

## Related Posts

- [How to Deploy an Astro Site to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [Generate sitemap.xml and robots.txt in Astro](/en/astro-sitemap-robots)
- [How to Add a New Page in Astro](/en/astro-add-page)
- [How to Read Cloudflare Pages Build Logs and Fix Errors](/en/cloudflare-pages-build-log)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
