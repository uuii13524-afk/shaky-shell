---
title: 'docker exec: Run Commands Inside a Container (with Examples)'
date: '2026-06-02'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Docker', 'docker exec', 'コンテナ', 'bash', 'デバッグ']
en_tags: ['Docker', 'docker exec', 'container', 'bash', 'debugging']
description: 'How to use docker exec to enter a running container, run one-off commands, pass env vars, and debug with practical examples for bash, sh, and docker-compose.'
---

## Quick Answer

```bash
# Enter a running container with bash
docker exec -it CONTAINER_NAME bash

# Enter with sh (Alpine images without bash)
docker exec -it CONTAINER_NAME sh

# Run a single command without entering
docker exec CONTAINER_NAME cat /etc/nginx/nginx.conf
```

Get your container name from `docker ps`.

---

## Basic docker exec Syntax

```
docker exec [OPTIONS] CONTAINER COMMAND [ARG...]
```

| Option | Description |
|---|---|
| `-i` | Keep stdin open (interactive) |
| `-t` | Allocate a pseudo-TTY (terminal) |
| `-u` | Run as a specific user |
| `-e` | Set an environment variable |
| `-w` | Set the working directory |

Always combine `-i` and `-t` as `-it` when opening an interactive shell. Without `-t`, you get no prompt. Without `-i`, input is immediately closed.

---

## Enter a Container Shell

### bash (default for most images)

```bash
docker exec -it my-nginx bash
```

### sh (Alpine-based images)

Alpine images don't ship with bash. Use `sh`:

```bash
docker exec -it my-alpine sh
```

### Enter as root for debugging

```bash
docker exec -it -u root my-container bash
```

### Enter as a specific user

```bash
docker exec -it -u www-data my-container bash
```

---

## Run a Single Command

```bash
# Read a config file
docker exec my-nginx cat /etc/nginx/nginx.conf

# List files
docker exec my-app ls -la /var/log/

# Check environment variables
docker exec my-app env

# Check running processes
docker exec my-app ps aux
```

---

## Set Environment Variables

```bash
# Pass an env var to the command
docker exec -e DEBUG=true my-app node debug.js

# Pass multiple env vars
docker exec -e NODE_ENV=production -e PORT=8080 my-app node app.js
```

---

## Set Working Directory

```bash
docker exec -w /app my-container ls
```

---

## Using docker exec with docker-compose

Use the **service name** from `docker-compose.yml`, not the container name:

```bash
# Enter the web service
docker-compose exec web bash

# Connect to PostgreSQL
docker-compose exec db psql -U postgres

# Run a migration
docker-compose exec web rails db:migrate
```

Check service names with `docker-compose ps`.

---

## Common Debugging Patterns

### Tail a log file live

```bash
docker exec my-nginx tail -f /var/log/nginx/error.log
```

### Test network connectivity between containers

```bash
docker exec my-app curl -v http://db:5432
docker exec my-app ping redis
```

### Check open ports inside the container

```bash
docker exec my-container ss -tlnp
```

---

## Common Errors

### `bash: not found`

The image doesn't include bash. Use `sh`:

```bash
docker exec -it my-container sh
```

### `the input device is not a TTY`

You're missing `-t`. Always use `-it` for interactive sessions.

### `cannot exec in a stopped container`

Start the container first:

```bash
docker start CONTAINER_NAME
docker exec -it CONTAINER_NAME bash
```

---

## docker exec vs docker run

| | `docker exec` | `docker run` |
|---|---|---|
| Target | Running container | Creates a new container |
| Use case | Debug live container | Start a fresh container |
| State | Uses existing state | Starts clean |

---

## FAQ

**Q: What does `docker exec -it` mean?**
`-i` keeps stdin open, `-t` allocates a terminal. Together they make the session interactive.

**Q: How do I run a command in a Docker container?**
`docker exec CONTAINER_NAME COMMAND`. Example: `docker exec my-app ls /var/log`.

**Q: How do I enter a running Docker container?**
`docker exec -it CONTAINER_NAME bash` (or `sh` for Alpine images).

**Q: Why does `docker exec bash` give "bash: not found"?**
The image is Alpine-based and doesn't include bash. Use `sh` instead.

**Q: Can I run docker exec on a stopped container?**
No. Start the container first with `docker start CONTAINER_NAME`.

**Q: What is the difference between docker exec and docker attach?**
`docker exec` creates a new process inside the container. `docker attach` connects to the main process (PID 1). Use `exec` for debugging.

---

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
