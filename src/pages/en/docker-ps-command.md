---
title: 'docker ps Command Guide: Listing, Filtering, and Formatting Containers'
date: '2026-07-06'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker ps', 'container management']
description: 'Learn how to list running and stopped containers with docker ps, including the -a, --filter, --format, and size options, plus common errors.'
---

## Quick Answer

```bash
# List running containers
docker ps

# List all containers, including stopped ones
docker ps -a
```

---

## What You're Trying to Do

You want to check which containers are currently running, remember the name of a container you stopped earlier, or narrow the list down to containers started from a specific image. `docker ps` is the command you reach for first in all of these cases.

By default it only shows running containers, which trips a lot of people up into thinking a container has "disappeared" when it's simply stopped. Knowing the right combination of options makes container management much smoother.

---

## Environment

- Docker: verified on 20.10 and later
- OS: Linux / macOS / Windows (WSL2)

---

## Solution

### 1. List Running Containers

```bash
docker ps
```

```
CONTAINER ID   IMAGE     COMMAND                  STATUS         PORTS                    NAMES
a1b2c3d4e5f6   nginx     "/docker-entrypoint.…"   Up 2 hours     0.0.0.0:80->80/tcp       my-nginx
```

By default, only containers in the `Up` state are shown.

### 2. Include Stopped Containers

```bash
docker ps -a
```

This also lists containers in the `Exited` state. If a container seems to have vanished, check with `-a` first.

### 3. Limit the Number of Results

```bash
# Show only the most recently created container
docker ps -l

# Show the 3 most recently created containers
docker ps -n 3
```

### 4. Get Only Container IDs

```bash
docker ps -aq
```

This is commonly used in scripts for bulk operations, like removing or stopping multiple containers at once.

```bash
# Remove all stopped containers
docker rm $(docker ps -aq -f status=exited)
```

### 5. Filter With `--filter`

```bash
# Only containers started from a specific image
docker ps -a --filter "ancestor=nginx"

# Filter by name
docker ps -a --filter "name=my-nginx"

# Filter by status
docker ps -a --filter "status=exited"
```

### 6. Customize Output With `--format`

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

```
NAMES       STATUS         PORTS
my-nginx    Up 2 hours     0.0.0.0:80->80/tcp
```

Using a Go template lets you show only the columns you need, which keeps the often-too-wide `docker ps` output readable.

### 7. Show Container Disk Size

```bash
docker ps -s
```

This adds a `SIZE` column showing how much disk space each container is using — handy when you're tracking down disk usage.

---

## Common Errors

### The Container Doesn't Show Up in the List

`docker ps` only lists running containers by default. If it's stopped, add `-a`:

```bash
docker ps -a
```

### `docker: command not found`

Docker isn't installed, or it isn't on your `PATH`. Check the install:

```bash
docker --version
```

### `Cannot connect to the Docker daemon`

The Docker daemon isn't running. Start it based on your OS:

```bash
# Linux (systemd)
sudo systemctl start docker

# macOS / Windows
# Start Docker Desktop
```

### `--filter` Returns Zero Results

This is usually a typo in the filter key or value. `ancestor` expects an image name, `name` expects a container name, and `status` expects a value like `running`, `exited`, or `paused`. Double-check the value you passed.

---

## FAQ

**Q: What's the difference between `docker ps` and `docker container ls`?**
They return identical results. `docker container ls` is the newer subcommand naming, while `docker ps` is the original, still-supported alias.

**Q: How do I show only stopped containers?**
Use `docker ps -a --filter "status=exited"`.

**Q: How can I list just the container names?**
Run `docker ps --format "{{.Names}}"` to print one name per line.

**Q: The `docker ps` output is too wide to read — what can I do?**
Use the `--format` option with a table template to show only the columns you actually need.

**Q: Can I combine multiple filters?**
Yes, repeating `--filter` combines them with AND logic. For example: `docker ps -a --filter "status=exited" --filter "ancestor=nginx"`

**Q: Does this also show containers started with docker compose?**
Yes, `docker ps` shows them too, but `docker compose ps` groups them by project, which is easier to read.

---

## Related Articles

- [docker cp Command Guide](/en/docker-cp)
- [docker exec: Enter a Running Container](/en/docker-exec-bash)
- [How to Use the docker logs Command](/en/docker-logs)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
