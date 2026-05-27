---
title: 'How to Add a New Page in Astro'
date: '2026-05-08'
category: 'Astro'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Learn how to add new pages in Astro using HTML or Markdown, including file placement, routing rules, and how to add links.'
---

## What I Wanted to Do

I wanted to add a new page to my Astro site.

## Basic Page Structure

```
src/
  pages/
    index.astro    → https://your-domain/
    about.astro    → https://your-domain/about
    posts/
      first.md     → https://your-domain/posts/first
```

## Creating a Page with a Markdown File

```markdown
---
title: 'Article Title'
date: '2026-05-08'
---

## Heading

Write the body content here.
```

## Gotchas

- Files placed outside `src/pages/` will not become pages
- The filename becomes the URL path as-is

Once you have multiple pages, it is a good idea to also set up [SEO meta tags in Astro](/en/astro-seo-meta-tags).

## Related Articles

- [How to Deploy Astro to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [How to Auto-Generate robots.txt and Sitemap in Astro](/en/astro-sitemap-robots)
- [Google Search Console HTML File Verification with Astro and Cloudflare Pages](/en/google-search-console-html-verification)
- [How to Read Cloudflare Pages Build Logs and Fix Errors](/en/cloudflare-pages-build-log)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
