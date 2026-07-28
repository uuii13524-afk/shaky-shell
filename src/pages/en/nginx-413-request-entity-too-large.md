---
title: 'Fix "413 Request Entity Too Large" in nginx'
date: '2026-07-28'
category: 'nginx'
layout: '../../layouts/PostLayoutEn.astro'
description: 'nginx rejects a file upload to a reverse-proxied API with 413 Request Entity Too Large even though the backend accepts it directly. Here is the client_max_body_size cause and the fix.'
en_tags: ['nginx', '413', 'Request Entity Too Large', 'client_max_body_size']
---

## What I Was Trying to Do

I had a Node.js image upload API (Express + multer) running behind nginx as a reverse proxy on a VPS. It worked fine locally, so as a production sanity check I tried uploading a slightly larger image (about 15MB) with `curl`, and got rejected.

```bash
curl -X POST https://api.example.com/upload \
  -F "file=@./sample-photo.jpg"
```

```text
<html>
<head><title>413 Request Entity Too Large</title></head>
<body>
<center><h1>413 Request Entity Too Large</h1></center>
<hr><center>nginx/1.24.0 (Ubuntu)</center>
</body>
</html>
```

The same endpoint accepted a small (~1MB) test image without any problem — the only thing that changed was the file size. I hadn't touched the Express code at all, so at first I had no idea where the request was actually being rejected.

## Environment

- OS: Ubuntu 22.04.4 LTS (Sakura VPS)
- nginx: 1.24.0 (installed via `apt`)
- Backend: Node.js 20.11.1 + Express 4.19.2 + multer 1.4.5-lts.1, listening on port 3000
- Setup: nginx listens on 443 and forwards requests to the Express app via `proxy_pass`

## What I Tried

My first guess was that Express itself had a body size limit — I recalled `express.json()` and `express.urlencoded()` default to a fairly small limit. But I checked the multer config and hadn't set a `limits` option at all.

```js
const upload = multer({ dest: 'uploads/' });
```

To rule out the backend, I hit the Express app directly on port 3000, bypassing nginx entirely, from inside the VPS.

```bash
curl -X POST http://localhost:3000/upload \
  -F "file=@./sample-photo.jpg"
```

```text
{"status":"ok","filename":"1721958812345-sample-photo.jpg","size":15234871}
```

The same 15MB file uploaded fine without nginx in front of it. That confirmed Express and multer weren't the problem, and the request was being stopped somewhere in nginx. Next I checked nginx's error log.

```bash
sudo tail -n 5 /var/log/nginx/error.log
```

```text
2026/07/28 10:42:03 [error] 8821#8821: *14 client intended to send too large body: 15728694 bytes, client: 203.0.113.45, server: api.example.com, request: "POST /upload HTTP/1.1", host: "api.example.com"
```

The `client intended to send too large body` line made it clear: nginx was rejecting the request with 413 based on its own body size limit, before the request ever reached the upstream Express app.

## Why This Happens

nginx has a directive called `client_max_body_size` that caps the maximum size of a request body it will accept. It defaults to `1m` (1 megabyte) unless explicitly overridden. Any request body larger than that is rejected with `413 Request Entity Too Large` directly by nginx, before it's proxied to the upstream server. My 15MB upload was well over the default 1MB limit, and the earlier small test image had only succeeded because it happened to fit under it.

## Solution

### 1. Add `client_max_body_size` to the nginx config

```bash
sudo nano /etc/nginx/sites-available/api.example.com.conf
```

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    client_max_body_size 20m;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

I added `client_max_body_size 20m;` directly under the `server` block, giving some headroom above the largest image I expected to handle.

### 2. Test the config syntax

```bash
sudo nginx -t
```

```text
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

Always run `nginx -t` before reloading — a syntax error here can leave nginx unable to start back up.

### 3. Reload nginx

```bash
sudo systemctl reload nginx
```

`reload` re-reads the config without dropping existing connections, unlike `restart`.

### 4. Retry the upload

```bash
curl -X POST https://api.example.com/upload \
  -F "file=@./sample-photo.jpg"
```

```text
{"status":"ok","filename":"1721958933210-sample-photo.jpg","size":15234871}
```

No more 413 — the 15MB file made it through to Express and got a normal response.

## Gotchas

- I almost put the directive in the `http` block instead of the specific `server` block. Since this nginx config manages multiple `server_name`s, I scoped it to just the one server block so it wouldn't loosen the limit for unrelated sites.
- Setting `client_max_body_size 0;` removes the limit entirely, but that risks accepting arbitrarily huge uploads. I picked a concrete value (`20m`) just above the largest file I actually expected.
- This setup also sat behind Cloudflare, which has its own upload size cap (100MB on the free plan). Raising the nginx limit alone doesn't help if a request is already being blocked upstream by Cloudflare.
- I nearly skipped `nginx -t` before reloading — it's what caught a missing semicolon I'd typed by mistake.

## FAQ

**Q: Is it safe to just set `client_max_body_size` to something huge like `1000m`?**
Setting it far higher than necessary increases the risk of large uploads or abusive requests exhausting disk or memory. It's safer to set it just above the largest file your application is actually expected to accept.

**Q: I fixed the nginx config but I'm still getting 413.**
The backend itself may have its own body size limit (Express's body parsers, PHP's `upload_max_filesize`, etc.). Check the error log first to see whether the rejection is coming from nginx or from the application.

**Q: Does this work the same way for nginx running inside a Docker container?**
The same directive applies inside the container's `nginx.conf` or a file under `conf.d`. If that config is mounted from the host, you'll need to reload nginx inside the container (`nginx -s reload`) or restart the container for the change to take effect.

## Related Articles

- [How to Set Up nginx as a Reverse Proxy](/en/nginx-reverse-proxy)
- [Basic nginx Configuration File Syntax](/en/nginx-basic-config)
- [How to Check nginx Access Logs](/en/nginx-access-log)
- [How to Fix a 403 Forbidden Error in nginx](/en/nginx-403-forbidden)
- [How to Install Docker on a VPS and Build a Web Server](/en/vps-docker-setup)
