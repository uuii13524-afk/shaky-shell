---
title: 'Change Xserver Nameservers to Cloudflare'
date: '2026-05-02'
category: 'Cloudflare'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Cloudflare', 'Xserver', 'ネームサーバー', 'DNS']
en_tags: ['Cloudflare', 'Xserver', 'nameserver', 'DNS']
description: 'How to change the nameservers of an Xserver domain to Cloudflare. Step-by-step guide from getting nameserver addresses to confirming Active status.'
---
## What I Wanted to Do

Use a Cloudflare Pages custom domain with a domain registered on Xserver.

## Steps

1. In Cloudflare, select "Connect a domain" — two nameserver addresses are generated
2. Log in to the Xserver domain management panel
3. Go to "ネームサーバー設定" → select "その他のサービスで利用する"
4. Enter the two Cloudflare nameserver addresses and save
5. Back in Cloudflare, click "I updated my nameservers"
6. Wait 30 minutes to 1 hour for status to become Active

## Common Pitfalls

- Cloudflare has separate areas for Workers and Pages — make sure you're in the right one
- Propagation takes time — be patient and don't click verify too early
- After going Active, you still need to go back and activate the custom domain in Pages settings (two-step process)

Once the nameservers are Active, continue with [Set Up a Custom Domain on Cloudflare Pages with Xserver](/en/xserver-cloudflare-full-setup) to finish the domain activation.

## Related Posts

- [Set Up a Custom Domain on Cloudflare Pages with Xserver](/en/xserver-cloudflare-full-setup)
- [How to Check SSL Settings for a Custom Domain on Cloudflare](/en/cloudflare-ssl-check)
- [How to Deploy an Astro Site to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [Cloudflare Pages Auto-Deploy Not Working](/en/cloudflare-pages-deploy-not-working)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
