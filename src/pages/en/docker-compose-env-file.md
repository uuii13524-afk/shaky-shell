---
title: 'How to Manage Environment Variables with .env Files in docker-compose'
date: '2026-06-03'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Docker', 'docker-compose', '環境変数', '.env']
en_tags: ['Docker', 'docker-compose', 'environment variables', '.env file']
description: 'How to use .env files in docker-compose to manage environment variables safely without hardcoding passwords or API keys.'
---
## What I Wanted to Do

I had database passwords and API keys hardcoded in docker-compose.yml and was afraid to push them to GitHub.
Heard that .env files could handle this cleanly, so I tried it out.

## Basic Usage of .env Files

Put a `.env` file in the same directory as docker-compose.yml — it gets loaded automatically.

```
# .env
MYSQL_ROOT_PASSWORD=secret123
MYSQL_DATABASE=myapp
APP_PORT=3000
```

```yaml
# docker-compose.yml
version: '3'
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
    ports:
      - "3306:3306"
  app:
    build: .
    ports:
      - "${APP_PORT}:3000"
```

The values from `.env` get substituted into `${VARIABLE_NAME}` placeholders. Add `.env` to `.gitignore` so it never gets committed.

## Passing Variables into Containers with env_file

In addition to `environment`, you can use `env_file` to pass an entire file into the container.

```yaml
services:
  app:
    image: node:18
    env_file:
      - .env
      - .env.local
```

Loading multiple files works well: put shared config in `.env` and local overrides in `.env.local`.

## How to Verify the Configuration

```bash
# See the final compose config after variable expansion
docker compose config

# Check environment variables inside a running container
docker exec -it <container_name> env
```

Running `docker compose config` shows the YAML with all variables replaced by their actual values — useful to catch mistakes before deploying.

## Gotchas

- `.env` is auto-loaded and expands `${VAR}` in the YAML, but files listed under `env_file` only get passed into the container and won't expand YAML placeholders
- Values with spaces need quotes: `MY_VAR="hello world"`
- Forgot to add `.env` to `.gitignore` and accidentally pushed database credentials to GitHub
- After changing `.env`, you need to restart the container for changes to take effect — `docker compose up` alone isn't enough
- `docker compose config` is the quickest way to catch a wrong or missing variable before it causes a runtime error

## Related Articles

- [How to Use docker-compose: A Practical Guide](/posts/docker-compose-basic)
- [How to Persist Data with Docker Volumes](/posts/docker-volume-basics)
- [Dockerfile Basics: FROM, RUN, COPY, CMD, EXPOSE](/posts/docker-dockerfile-basics)
- [How to Run Commands Inside a Docker Container with docker exec](/posts/docker-exec-bash)
- [Docker Network Basics: bridge, host, and none](/posts/docker-network-basics)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
