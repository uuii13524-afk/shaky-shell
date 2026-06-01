---
title: 'How to Enable gzip Compression in nginx'
date: '2026-05-24'
category: 'nginx'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['nginx', 'gzip', 'パフォーマンス']
en_tags: ['nginx', 'gzip', 'performance']
---

## What I wanted to do

My site served through nginx was slow to load.
I heard that enabling gzip compression reduces file sizes and speeds things up, so I gave it a try.

## What is gzip compression?

It's a mechanism that compresses text-based files (HTML, CSS, JS, JSON, etc.) before transferring them.
The browser automatically decompresses them, so there's no impact on the user experience.
Depending on the file type, JS and CSS can often be reduced by 70–80%.

## Edit the configuration file

```bash
sudo nano /etc/nginx/nginx.conf
```

Add the following inside the `http` block.

```nginx
http {
    # gzip settings
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_types
        text/plain
        text/css
        text/xml
        application/json
        application/javascript
        application/xml
        application/xml+rss
        text/javascript
        image/svg+xml;
}
```

## What each setting means

| Setting | Description |
|---------|-------------|
| `gzip on` | Enables gzip compression |
| `gzip_vary on` | Adds `Vary: Accept-Encoding` header (for CDN compatibility) |
| `gzip_proxied any` | Compresses responses for proxied requests |
| `gzip_comp_level 6` | Compression level (1–9; 6 is a good balance) |
| `gzip_types` | MIME types to compress (images are generally excluded) |

## Apply and verify the settings

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Check if compression is working

```bash
curl -H "Accept-Encoding: gzip" -I https://example.com
```

If `Content-Encoding: gzip` appears in the response headers, it's working.

```
HTTP/2 200
content-type: text/html
content-encoding: gzip
```

You can also verify in Chrome DevTools:
`Network` tab → select a file → check `Response Headers` for `content-encoding: gzip`.

## Per-site configuration

You can also add the settings inside the `server` block in individual files under `/etc/nginx/sites-available/`.

```nginx
server {
    listen 80;
    server_name example.com;

    gzip on;
    gzip_types text/css application/javascript;

    location / {
        root /var/www/html;
    }
}
```

## Gotchas

- You don't need to add `text/html` to `gzip_types` — it's compressed automatically when `gzip on` is set
- Images (jpg/png/webp) are already compressed, so adding them to `gzip_types` has no effect
- Setting `gzip_comp_level` to 9 increases compression but also CPU load — 6 is enough
- If your site is behind Cloudflare, Cloudflare also compresses responses, which can override nginx's settings
- Forgetting `gzip_vary on` can cause CDNs to confuse gzip and non-gzip cached versions

## Related articles

- [nginx Basic Configuration File Guide](/posts/nginx-basic-config)
- [How to Set Up a Reverse Proxy with nginx](/posts/nginx-reverse-proxy)
- [nginx 502 Bad Gateway: Causes and Fixes](/posts/nginx-502-bad-gateway)
- [Getting an SSL Certificate with Certbot (nginx)](/posts/nginx-ssl-certbot)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
