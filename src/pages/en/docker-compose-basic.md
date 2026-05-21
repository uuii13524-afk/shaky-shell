---
title: 'How to Use docker-compose: A Practical Guide'
date: '2026-05-12'
category: 'Docker'
---

## What I Wanted to Do

Start and stop multiple Docker containers with a single command instead of running them individually.

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
      MYSQL_DATABASE: mydb
```

## Essential Commands

```bash
docker compose up           # Start containers
docker compose up -d        # Start in background
docker compose down         # Stop and remove containers
docker compose ps           # Check status
docker compose logs -f      # Follow logs
docker compose exec web bash  # Enter a container shell
docker compose build        # Build images
docker compose restart      # Restart containers
```

## Persist Data with Volumes

Without volumes, data disappears when containers are removed.

```yaml
services:
  db:
    image: mysql:8
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

## Load Environment Variables from .env

```yaml
services:
  web:
    image: nginx
    env_file:
      - .env
```

## Set Startup Order

```yaml
services:
  web:
    image: nginx
    depends_on:
      - db
  db:
    image: mysql:8
```

Note: `depends_on` controls startup order but doesn't wait for the service to be ready.

## Key Points

- Use `docker compose` (with space) — `docker-compose` (with hyphen) is the old version
- `docker compose down` removes containers but keeps volumes
- `docker compose down -v` also removes volumes — use with caution
- Use named volumes for any data you want to keep

## Related Articles

- [Docker Basic Commands Cheatsheet](/en/docker-basic-commands)
- [How to Install Docker on Windows](/en/docker-install-windows)
- [nginx 502 Bad Gateway Fix](/en/nginx-502-bad-gateway)
