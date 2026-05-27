---
title: 'Docker Basic Commands Cheatsheet (run/stop/rm/ps)'
date: '2026-05-12'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
---

## Container Operations

```bash
docker run -d -p 8080:80 --name myapp nginx
docker ps
docker ps -a
docker stop myapp
docker rm myapp
docker exec -it myapp bash
docker logs -f myapp
```

## Image Operations

```bash
docker images
docker pull nginx
docker rmi image-id
docker build -t myapp .
```

## Cleanup

```bash
docker system prune
```

## Key Points

- Without `-d`, container runs in foreground
- Port format: `-p host-port:container-port`

## Related Articles

- [How to Install Docker on Windows](/en/docker-install-windows)
- [How to Use docker-compose](/en/docker-compose-basic)
- [nginx 502 Bad Gateway Fix](/en/nginx-502-bad-gateway)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
