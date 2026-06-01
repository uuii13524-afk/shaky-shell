---
title: 'nginx location Directive Syntax and Priority Guide'
date: '2026-06-01'
category: 'nginx'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['nginx', 'location', 'サーバー設定', 'Webサーバー']
en_tags: ['nginx', 'location directive', 'server config', 'web server']
description: 'A guide to nginx location directive syntax and matching priority. Covers exact match, prefix match, and regex with practical config examples.'
---
## What I Wanted to Do
I needed to route different URLs to different handlers in nginx.
The goal was to forward only `/api/` paths to a backend server while serving static files directly — but I kept getting the routing wrong because I didn't understand location matching rules.

## Types of location Directives

### Exact Match (= modifier)
```nginx
location = /favicon.ico {
    log_not_found off;
    access_log off;
}
```
- Only matches when the URL is exactly this string
- Highest priority of all location types
- Commonly used to suppress logs for favicon and robots.txt

### Prefix Match (no modifier)
```nginx
location /api/ {
    proxy_pass http://localhost:3000;
}
```
- Matches any URL starting with `/api/`
- Simplest form — good for most routing needs

### Priority Prefix Match (^~ modifier)
```nginx
location ^~ /static/ {
    root /var/www;
}
```
- Once matched, nginx skips all regex location evaluation
- Use when static files must take priority over regex blocks

### Regex Match (~ or ~* modifier)
```nginx
# Case-sensitive
location ~ \.php$ {
    fastcgi_pass unix:/run/php/php8.2-fpm.sock;
    include fastcgi_params;
}

# Case-insensitive
location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2)$ {
    expires 30d;
    access_log off;
}
```
- `~` is case-sensitive, `~*` is case-insensitive
- Often used for static file caching rules

## Matching Priority Order

1. `=` exact match (highest priority)
2. `^~` prefix match that skips regex
3. `~` or `~*` regex (evaluated in definition order)
4. Plain prefix match (longest match wins)

## Practical Configuration Examples

### PHP App with API Routing
```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/html;

    location = / {
        index index.php;
    }

    location /api/ {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/run/php/php8.2-fpm.sock;
        include fastcgi_params;
    }
}
```

### Static File Caching
```nginx
location ~* \.(jpg|jpeg|png|gif|ico|svg|css|js|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}
```

## Common Pitfalls
- The `=` modifier requires an exact URL — `/favicon.ico/` with a trailing slash is a different path
- Regex locations are evaluated in the order they appear, so put more specific patterns first
- A trailing slash in `proxy_pass` strips the location prefix: `/api/foo` becomes `/foo`
- When nesting locations, `alias` replaces the matched path while `root` appends it — they behave differently
- Always test config with `nginx -t` before reloading: `systemctl reload nginx`

## Related Articles
- [nginx Basic Configuration File Structure](/en/nginx-basic-config)
- [nginx Reverse Proxy Setup for Node.js Apps](/en/nginx-reverse-proxy)
- [How to Fix nginx 502 Bad Gateway Error](/en/nginx-502-bad-gateway)
- [Setting Up SSL with Let's Encrypt and Certbot on nginx](/en/nginx-ssl-certbot)
- [Enable gzip Compression in nginx for Faster Page Loads](/en/nginx-gzip-compression)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
