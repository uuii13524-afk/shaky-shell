---
title: 'Set Up a Custom Domain on Cloudflare Pages with Xserver'
date: '2026-05-05'
category: 'Cloudflare'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Cloudflare', 'Xserver', 'カスタムドメイン', 'ネームサーバー']
en_tags: ['Cloudflare', 'Xserver', 'custom domain', 'nameserver']
description: 'Full walkthrough for connecting an Xserver domain to Cloudflare Pages as a custom domain — from nameserver change to DNS setup and HTTPS.'
---
## What I Wanted to Do

Use a domain registered on Xserver as a custom domain for a Cloudflare Pages site.

## Overview

```
Get nameservers from Cloudflare
↓
Change nameservers on Xserver to Cloudflare
↓
Wait for Cloudflare status to become Active
↓
Activate custom domain in Cloudflare Pages
```

## Steps

### 1. Connect a Domain in Cloudflare Pages

1. "Workers & Pages" → project → "Custom domains"
2. "Set up a custom domain" → enter your domain → "Continue"
3. "Begin DNS transfer" → "Continue to activation"
4. Note the two Cloudflare nameserver addresses shown

### 2. Change Nameservers on Xserver

1. Log in to the Xserver domain management panel
2. "ネームサーバー設定" → "その他のサービスで利用する"
3. Enter the two Cloudflare nameserver addresses → Save

### 3. Wait for Active Status in Cloudflare

1. Click "I updated my nameservers"
2. Wait 30 minutes – 1 hour
3. Once the status shows "Active", you're ready

### 4. Activate the Custom Domain

1. "Custom domains" → enter your domain → "Continue"
2. Click "Activate domain"

## Common Pitfalls

- Don't try to activate the custom domain before the nameserver change is complete — it won't proceed
- The process requires two separate steps: first go Active, then activate the custom domain

After your domain is connected, verify HTTPS is working correctly with [How to Check SSL Settings for a Custom Domain on Cloudflare](/en/cloudflare-ssl-check).

## Related Posts

- [Change Xserver Nameservers to Cloudflare](/en/xserver-cloudflare-nameserver)
- [How to Check SSL Settings for a Custom Domain on Cloudflare](/en/cloudflare-ssl-check)
- [How to Deploy an Astro Site to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [Cloudflare Pages Auto-Deploy Not Working](/en/cloudflare-pages-deploy-not-working)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
