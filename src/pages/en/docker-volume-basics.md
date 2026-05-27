---
title: 'How to Persist Data with Docker Volumes'
date: '2026-05-16'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Learn how to use Docker volumes to persist container data. Covers creating, mounting, and managing volumes with practical docker-compose examples.'
---

## What Are Volumes?

A mechanism for saving Docker container data to the host machine. Data persists even after the container is deleted.

## Named Volumes (Recommended)

```bash
docker run -d -v mydata:/var/lib/mysql mysql:8
```

## Configuration in docker-compose

```yaml
services:
  db:
    image: mysql:8
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

## Volume Commands

```bash
docker volume ls
docker volume create mydata
docker volume rm mydata
docker volume prune
```

## Key Points

- `docker compose down -v` also deletes volumes — be careful
- Deleting a container without a volume wipes all its data

For docker-compose setups that use volumes, see [How to Use docker-compose](/en/docker-compose-basic) for a complete overview.

## Related Articles

- [Docker Basic Commands Cheatsheet](/en/docker-basic-commands)
- [How to Use docker-compose](/en/docker-compose-basic)
- [Dockerfile Basics: FROM, RUN, COPY, CMD, EXPOSE](/en/docker-dockerfile-basics)
- [How to Install Docker on Windows](/en/docker-install-windows)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
