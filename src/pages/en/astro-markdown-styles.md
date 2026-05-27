---
title: 'How to Style Markdown Content in Astro'
date: '2026-05-15'
category: 'Astro'
layout: '../../layouts/PostLayoutEn.astro'
description: 'How to apply CSS styles to Markdown content in Astro using global CSS or the Tailwind typography plugin.'
---

## Method 1: Use Global CSS

Create `src/styles/global.css`.

```css
article h2 { font-size: 1.5rem; margin-top: 2rem; }
article p { line-height: 1.8; margin-bottom: 1rem; }
article code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }
article pre { background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 8px; overflow-x: auto; }
```

Import it in your layout file.

```astro
---
import '../styles/global.css';
---
```

## Layout File Configuration

```markdown
---
title: 'Article Title'
layout: '../../layouts/PostLayout.astro'
---
```

## Gotchas

- HTML generated from Markdown does not automatically get CSS classes
- The layout file path is relative to the Markdown file

After setting up your styles, also configure [SEO meta tags in Astro](/en/astro-seo-meta-tags) to complete your basic SEO setup.

## Related Articles

- [How to Add a New Page in Astro](/en/astro-add-page)
- [How to Set SEO Meta Tags in Astro](/en/astro-seo-meta-tags)
- [How to Deploy Astro to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [How to Read Cloudflare Pages Build Logs and Fix Errors](/en/cloudflare-pages-build-log)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
