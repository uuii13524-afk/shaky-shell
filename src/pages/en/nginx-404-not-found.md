---
title: 'nginx 404 Not Found: Causes and How to Fix It'
date: '2026-06-07'
category: 'nginx'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['nginx', '404', 'Not Found', 'サーバー設定', 'Linux']
en_tags: ['nginx', '404', 'not found', 'server config', 'linux']
description: 'Why nginx returns 404 Not Found and how to fix it. Covers root path issues, try_files misconfiguration, file permissions, and alias vs root behavior.'
---
## What I Was Trying to Do

I set up nginx on a VPS to serve a Next.js static export, but every URL returned 404 Not Found. The config was copied straight from the docs, so I had no idea where to start. It took two hours to track down the actual cause.

## Environment

- Ubuntu 22.04
- nginx 1.18.0
- Next.js 14.x (static export, output to `out/` directory)

## Common Causes of nginx 404

### Cause 1: The root path doesn't exist or is empty

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/html/out;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Verify the directory actually exists:

```bash
ls -la /var/www/html/out
```

If it's missing or empty, nginx has nothing to serve and returns 404. For Next.js, you need to run `npm run build` with the static export config before copying the files.

### Cause 2: try_files ends with =404 in a SPA

```nginx
# This breaks all routes in a SPA
location / {
    try_files $uri $uri/ =404;
}
```

```nginx
# Correct for SPA: fall back to index.html
location / {
    try_files $uri $uri/ /index.html;
}
```

Using `=404` as the last fallback means any URL without a matching file returns 404 immediately. React, Next.js, and Vue SPAs route client-side, so you need to fall back to `index.html`.

### Cause 3: File permissions are too restrictive

```bash
# nginx runs as www-data
ls -la /var/www/html/out/

# Set correct ownership and permissions
chmod -R 755 /var/www/html/out
chown -R www-data:www-data /var/www/html/out
```

If the owner is still root, nginx can't read the files and returns 403 or 404.

### Cause 4: Confusing root and alias

```nginx
# root includes the location path in the file lookup
location /static/ {
    root /var/www/files;
    # /static/foo.js → looks for /var/www/files/static/foo.js
}

# alias strips the location path
location /static/ {
    alias /var/www/files/;
    # /static/foo.js → looks for /var/www/files/foo.js
}
```

Using `root` when you meant `alias` will cause nginx to look in the wrong place every time.

## What I Tried First

I kept running `systemctl restart nginx` after each config change, but nothing changed. It turned out there was a syntax error in the config, and nginx was running the old version the whole time.

```bash
# Always check syntax before reloading
nginx -t

# Reload if syntax is OK
systemctl reload nginx
```

I also ignored the error log for way too long. Looking at it immediately would have saved most of the debugging time.

```bash
tail -f /var/log/nginx/error.log
```

The log clearly said:

```
2026/06/07 10:23:14 [error] 1234#1234: *1 "/var/www/html/out/about/index.html" is not found
```

That's the whole story right there.

## The Fix

Running `nginx -t` first revealed the syntax error. After fixing the root path and permissions, everything worked.

```bash
nginx -t
ls -la /var/www/html/out/index.html
chown -R www-data:www-data /var/www/html/out
chmod -R 755 /var/www/html/out
systemctl reload nginx
```

If the error log shows `is not found`, the root path or file is missing. If it shows `Permission denied`, fix ownership and permissions. This fixed it.

## Key Takeaways

- Always run `nginx -t` before reloading — syntax errors silently keep nginx on the old config
- Check the error log first: `/var/log/nginx/error.log` usually states exactly what file nginx couldn't find
- SPAs need `try_files $uri $uri/ /index.html`, not `=404` — the latter breaks all non-root routes
- Both `chown` and `chmod` must be correct; fixing only one still blocks access
- `root` and `alias` behave differently: `root` appends the location path, `alias` strips it — mixing them up is a common source of silent 404s

## Related Articles

- [nginx Basic Configuration File Guide](/en/nginx-basic-config)
- [nginx 502 Bad Gateway: Causes and How to Fix It](/en/nginx-502-bad-gateway)
- [nginx location Directives Explained](/en/nginx-location-directives)
- [nginx Reverse Proxy Setup](/en/nginx-reverse-proxy)
- [Linux File Permissions Guide (chmod/chown)](/en/linux-file-permissions)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
