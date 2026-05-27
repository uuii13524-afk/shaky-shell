---
title: 'How to Set Up Cloudflare Analytics on an Astro Site'
date: '2026-05-19'
category: 'Cloudflare'
layout: '../../layouts/PostLayoutEn.astro'
description: 'How to add Cloudflare Analytics to an Astro site. A free, cookie-free web analytics tool with simple script installation.'
---

## What is Cloudflare Analytics?

- No cookies required
- Privacy-friendly measurement
- May be automatically enabled if you are using Cloudflare Pages

## Setup Steps

1. Go to the Cloudflare dashboard → "Analytics & Logs" → "Web Analytics"
2. Click "Add a site" → enter your URL
3. Copy the generated script tag

Paste it just before the `</body>` closing tag in your Astro layout file.

```astro
<script defer src='https://static.cloudflareinsights.com/beacon.min.js'
  data-cf-beacon='{"token": "YOUR_TOKEN"}'></script>
```

## Data Available

- Page views and unique visitors
- Top pages and referrers
- Traffic by country

## Gotchas

- Data may take a few hours to appear
- Because no cookies are used, the script is less likely to be blocked by ad blockers

While setting up Analytics, also configure [SEO meta tags in Astro](/en/astro-seo-meta-tags) to complete your site's measurement foundation.

## Related Articles

- [How to Deploy Astro to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [How to Add a New Page in Astro](/en/astro-add-page)
- [Google Search Console HTML File Verification with Astro and Cloudflare Pages](/en/google-search-console-html-verification)
- [Cloudflare Pages GitHub Auto-Deploy Not Working: How to Fix It](/en/cloudflare-pages-deploy-not-working)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
