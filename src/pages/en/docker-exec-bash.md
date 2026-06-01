---
title: 'How to Run Commands Inside a Docker Container with docker exec'
date: '2026-06-02'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Docker', 'docker exec', 'コンテナ', 'bash', 'デバッグ']
en_tags: ['Docker', 'docker exec', 'container', 'bash', 'debugging']
description: 'Learn how to use docker exec to enter a running container, run one-off commands, check logs, and debug your Docker environment.'
---
## What I Wanted to Do

I wanted to get inside a running Docker container and poke around — check files, run commands, look at logs.
I kept Googling this every time I needed to debug, so I wrote it down.

## Basic docker exec Usage

### Enter a container with bash

```bash
docker exec -it <container-name-or-id> bash
```

The `-i` flag keeps stdin open (interactive), and `-t` allocates a pseudo-TTY.
Get the container name with `docker ps`.

```bash
docker ps
# CONTAINER ID   IMAGE     COMMAND   NAMES
# a1b2c3d4e5f6   nginx     ...       my-nginx
docker exec -it my-nginx bash
```

### Use sh if bash isn't available

Alpine-based images often don't have bash installed.

```bash
docker exec -it <container-name> sh
```

### Run a single command without entering the container

```bash
docker exec <container-name> cat /etc/nginx/nginx.conf
docker exec <container-name> ls -la /var/log/nginx/
```

### Check environment variables

```bash
docker exec <container-name> env
```

## Using docker exec with docker-compose

With docker-compose, you reference the service name instead of the container name.

```bash
docker-compose exec web bash
docker-compose exec db psql -U postgres
```

The key difference: `docker-compose exec` uses the service name from `docker-compose.yml`, not the container name.

### Run as a specific user

```bash
# Enter as root (useful for permission debugging)
docker exec -it -u root <container-name> bash

# Run as a different user
docker exec -it -u www-data <container-name> bash
```

## Common Debugging Patterns

### Tail a log file live

```bash
docker exec <container-name> tail -f /var/log/nginx/error.log
```

### Check running processes

```bash
docker exec <container-name> ps aux
```

### Test network connectivity between containers

```bash
docker exec <container-name> curl -v http://other-container:3000
```

## Pitfalls I Hit

- Got `bash: not found` — switched to `sh`. Alpine images don't ship with bash
- Forgot `-it` when entering a shell — the session exited immediately. Always add both flags when going interactive
- Tried to run `docker exec` on a stopped container — it fails. Start it first with `docker start`
- Used `docker-compose exec` with the wrong service name — got `no such service`. Check names with `docker-compose ps`
- Created files as root inside the container, then couldn't write to them from the host. Use `-u` to match UIDs

## Related Articles

- [Docker Basic Commands Cheatsheet (run/stop/rm/ps)](/en/docker-basic-commands)
- [How to Use docker-compose: A Practical Guide](/en/docker-compose-basic)
- [Dockerfile Basics: FROM, RUN, COPY, CMD, EXPOSE](/en/docker-dockerfile-basics)
- [Docker Network Basics: bridge, host, and none](/en/docker-network-basics)
- [How to Persist Data with Docker Volumes](/en/docker-volume-basics)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
