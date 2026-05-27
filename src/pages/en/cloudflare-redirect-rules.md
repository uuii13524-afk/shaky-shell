---
title: 'How to Set Up Redirect Rules in Cloudflare'
date: '2026-05-16'
category: 'Cloudflare'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Cloudflare', 'リダイレクト', 'DNS', 'SEO']
en_tags: ['Cloudflare', 'redirect', 'DNS', 'SEO']
description: 'How to create redirect rules in the Cloudflare dashboard to redirect old URLs to new ones with 301 or 302 status codes.'
---
## How to Create a Redirect Rule

1. Cloudflare dashboard → target domain
2. Left menu: "Rules" → "Redirect Rules"
3. Click "Create rule"

## Redirect an Old URL to a New One

**Condition:** URI Path → equals → `/old-page`

**Action:** Static redirect → `https://example.com/new-page` → 301

## Status Code Reference

| Code | Meaning |
|------|---------|
| 301 | Permanent redirect |
| 302 | Temporary redirect |

## Common Pitfalls

- Rule order matters — rules are evaluated top to bottom
- The free plan allows up to 10 redirect rules
- If "Always Use HTTPS" is enabled, an HTTP→HTTPS redirect rule is unnecessary

For more complex redirect logic that can't be handled with rules, [Cloudflare Workers Introduction](/en/cloudflare-workers-intro) gives you full flexibility with JavaScript.

## Related Posts

- [How to Check SSL Settings for a Custom Domain on Cloudflare](/en/cloudflare-ssl-check)
- [Set Up a Custom Domain on Cloudflare Pages with Xserver](/en/xserver-cloudflare-full-setup)
- [How to Set Up Cloudflare Analytics on Your Astro Site](/en/cloudflare-analytics-setup)
- [How to Deploy an Astro Site to Cloudflare Pages](/en/astro-cloudflare-deploy)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
