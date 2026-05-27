---
title: 'nginx Basic Configuration File Guide'
date: '2026-05-12'
category: 'nginx'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['nginx', 'Linux', 'サーバー設定', 'Webサーバー']
en_tags: ['nginx', 'Linux', 'server config', 'web server']
description: 'A guide to writing nginx config files. Covers the server block, location directives, listen, root, and how to test and reload config.'
---
## What I Wanted to Do

I needed to serve a static site and set up a reverse proxy with nginx, but the config file syntax wasn't obvious.

## Basic Config File

```nginx
server {
    listen 80;
    server_name example.com;

    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

## Reverse Proxy Config

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Test and Reload Config

```bash
nginx -t          # Syntax check
nginx -s reload   # Reload without downtime
```

## Common Pitfalls

- Always run `nginx -t` before reloading — a syntax error will take down the server
- Missing semicolons `;` are a frequent cause of errors
- Before exposing nginx publicly, open ports 80 and 443 in the firewall

For firewall setup, see [Linux UFW Firewall Basics](/en/linux-firewall-ufw).

## Related Posts

- [nginx 502 Bad Gateway: Causes and Fixes](/en/nginx-502-bad-gateway)
- [nginx Reverse Proxy Setup (Serving a Node.js App)](/en/nginx-reverse-proxy)
- [Enable gzip Compression in nginx](/en/nginx-gzip-compression)
- [nginx SSL with Let's Encrypt (certbot)](/en/nginx-ssl-certbot)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
