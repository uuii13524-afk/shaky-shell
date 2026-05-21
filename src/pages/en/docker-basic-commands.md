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
