---
title: 'nginx 502 Bad Gateway: Causes and How to Fix It'
date: '2026-05-20'
category: 'nginx'
layout: '../../layouts/PostLayoutEn.astro'
---

## Symptoms

```
502 Bad Gateway
nginx/1.xx.x
```

## Cause 1: Backend Service Is Not Running

```bash
systemctl status your-app
docker ps
systemctl start your-app
```

## Cause 2: Wrong Port in nginx Config

```nginx
# Correct
proxy_pass http://localhost:3000;
```

## Cause 3: Wrong Hostname in Docker Environment

```nginx
# Wrong
proxy_pass http://localhost:3000;

# Correct (use the service name)
proxy_pass http://app:3000;
```

## Check the Error Log

```bash
tail -f /var/log/nginx/error.log
```

## Key Points

- In Docker, use service names instead of `localhost`
- The backend not running is the most common cause

## Related Articles

- [Docker Basic Commands](/en/docker-basic-commands)
- [How to Use docker-compose](/en/docker-compose-basic)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
