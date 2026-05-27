---
title: 'How to Set SEO Meta Tags in Astro'
date: '2026-05-18'
category: 'Astro'
layout: '../../layouts/PostLayoutEn.astro'
description: 'How to add SEO meta tags like title, description, and OGP to your Astro site, including a shared BaseHead component approach.'
---

## Basic Meta Tags

```astro
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Page Title - Site Name</title>
  <meta name="description" content="Page description (around 120 characters)" />
  <link rel="canonical" href="https://example.com/page" />
</head>
```

## OGP Tags

```astro
<meta property="og:title" content="Page Title" />
<meta property="og:description" content="Description" />
<meta property="og:url" content="https://example.com/page" />
<meta property="og:type" content="article" />
```

## Sharing Tags Across Pages via a Layout Component

```astro
---
const { title, description } = Astro.props;
---
<html>
  <head>
    <title>{title}</title>
    <meta name="description" content={description} />
  </head>
  <body><slot /></body>
</html>
```

## Gotchas

- A `description` of around 120–160 characters is recommended
- Omitting the `canonical` tag may cause your content to be treated as a duplicate

To further strengthen your SEO, combine this with [auto-generating robots.txt and sitemap in Astro](/en/astro-sitemap-robots) to properly control how search engines crawl your site.

## Related Articles

- [How to Add a New Page in Astro](/en/astro-add-page)
- [How to Auto-Generate robots.txt and Sitemap in Astro](/en/astro-sitemap-robots)
- [Google Search Console HTML File Verification with Astro and Cloudflare Pages](/en/google-search-console-html-verification)
- [How to Style Markdown Content in Astro](/en/astro-markdown-styles)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
