---
title: 'nginx Reverse Proxy Setup: Expose a Node.js App on Port 80/443'
date: '2026-05-23'
category: 'nginx'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['nginx', 'リバースプロキシ', 'Node.js', 'VPS']
en_tags: ['nginx', 'reverse proxy', 'Node.js', 'VPS']
---

## What I Wanted to Do

I had a Node.js app running on port 3000 on a VPS and needed to expose it publicly on port 80 and 443 using nginx as a reverse proxy.

## How Reverse Proxy Works

```
Client → nginx (80/443) → Node.js app (3000)
```

nginx receives the request and forwards it to the backend app.
You don't need to expose the app's port directly, which is also better for security.

## Basic Reverse Proxy Configuration

Create `/etc/nginx/sites-available/myapp`:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Create a symlink to enable it:

```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Node.js App Configuration

The app just needs to listen on localhost (127.0.0.1).

```js
const express = require('express');
const app = express();

app.listen(3000, '127.0.0.1', () => {
  console.log('Server running on port 3000');
});
```

Block direct access to port 3000 with the firewall if you don't want it exposed externally:

```bash
sudo ufw deny 3000
sudo ufw allow 80
sudo ufw allow 443
```

## WebSocket Proxy Configuration

WebSocket connections need extra headers:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Without the `Upgrade` and `Connection` headers, the WebSocket handshake will fail.

## Running Multiple Apps on the Same Server

You can route by domain or path:

```nginx
# Route by domain
server {
    listen 80;
    server_name app1.example.com;
    location / {
        proxy_pass http://localhost:3000;
    }
}

server {
    listen 80;
    server_name app2.example.com;
    location / {
        proxy_pass http://localhost:4000;
    }
}
```

```nginx
# Route by path
server {
    listen 80;
    server_name example.com;

    location /api/ {
        proxy_pass http://localhost:3000/;
    }

    location / {
        proxy_pass http://localhost:4000;
    }
}
```

## SSL (HTTPS) Setup

Run Certbot and it will automatically update your nginx config while keeping your `proxy_pass` settings intact:

```bash
sudo certbot --nginx -d example.com
```

## Common Pitfalls

- Forgetting `proxy_set_header Host $host;` means the backend can't get the hostname
- Without `proxy_http_version 1.1;`, WebSocket connections won't work
- A trailing slash in `proxy_pass http://localhost:3000/;` strips the location path prefix — behavior differs with and without it
- If your Node.js app is not listening on 127.0.0.1, nginx returns `502 Bad Gateway`
- Always run `nginx -t` to test config before reloading, or a typo will bring down production

## Related Articles

- [nginx Basic Configuration](/en/nginx-basic-config)
- [Fix nginx 502 Bad Gateway Error](/en/nginx-502-bad-gateway)
- [Setting Up SSL with Certbot on nginx](/en/nginx-ssl-certbot)
- [Setting Up Docker and nginx on a VPS](/en/vps-docker-setup)
- [Linux Firewall Setup with ufw](/en/linux-firewall-ufw)

## Recommended VPS / Cloud Hosting

If you're looking for high-performance cloud infrastructure, Cherry Servers offers developer-friendly VPS and dedicated servers optimized for AI, Web3, and production workloads.

<a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a>
