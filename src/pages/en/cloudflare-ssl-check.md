---
title: 'How to Check SSL Settings for a Custom Domain on Cloudflare'
date: '2026-05-07'
category: 'Cloudflare'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Cloudflare', 'SSL', 'HTTPS', 'ドメイン']
en_tags: ['Cloudflare', 'SSL', 'HTTPS', 'custom domain']
description: 'How to check and fix SSL settings for a custom domain on Cloudflare. Covers SSL mode selection and enabling Always Use HTTPS.'
---
## How to Check SSL Settings

1. Cloudflare dashboard → target domain
2. Left menu: "SSL/TLS" → "Overview"

Recommended setting when using Cloudflare Pages: **Full**

## Enable HTTPS Redirect

"SSL/TLS" → "Edge Certificates" → turn on "Always Use HTTPS"

## Troubleshooting by Symptom

| Symptom | Fix |
|---------|-----|
| Browser shows "Not secure" | Change SSL/TLS mode to "Full" |
| Certificate error | Wait 15 min – 24 hours for propagation |
| Mixed Content error | Change all asset URLs to HTTPS |

After confirming SSL is working, check [How to Set Up Redirect Rules in Cloudflare](/en/cloudflare-redirect-rules) to make sure HTTP is properly redirecting to HTTPS.

## Related Posts

- [Set Up a Custom Domain on Cloudflare Pages with Xserver](/en/xserver-cloudflare-full-setup)
- [Change Xserver Nameservers to Cloudflare](/en/xserver-cloudflare-nameserver)
- [Cloudflare Pages Auto-Deploy Not Working](/en/cloudflare-pages-deploy-not-working)
- [How to Deploy an Astro Site to Cloudflare Pages](/en/astro-cloudflare-deploy)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
