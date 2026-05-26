---
title: 'How to Use docker-compose: A Practical Guide'
date: '2026-05-12'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
---

## Basic docker-compose.yml

```yaml
version: '3'
services:
  web:
    image: nginx
    ports:
      - "8080:80"
  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: password
```

## Essential Commands

```bash
docker compose up -d
docker compose down
docker compose ps
docker compose logs -f
docker compose exec web bash
```

## Persist Data with Volumes

```yaml
services:
  db:
    image: mysql:8
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

## Key Points

- `docker compose down -v` also removes volumes — use with caution
- Use named volumes for data you want to keep

## Related Articles

- [Docker Basic Commands](/en/docker-basic-commands)
- [How to Install Docker on Windows](/en/docker-install-windows)
- [nginx 502 Bad Gateway Fix](/en/nginx-502-bad-gateway)


## Recommended VPS / Cloud Hosting

If you're looking for high-performance cloud infrastructure, Cherry Servers offers developer-friendly VPS and dedicated servers optimized for AI, Web3, and production workloads.

<a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a>