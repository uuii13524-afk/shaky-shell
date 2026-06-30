---
title: 'docker compose down: Stop and Remove Containers, Networks, and Volumes'
date: '2026-06-30'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker-compose', 'container cleanup']
description: 'Learn how to use docker compose down to stop and remove containers. Covers removing volumes and images with practical options and common error fixes.'
---

## Quick Answer

```bash
# Stop and remove containers and networks
docker compose down

# Also remove volumes
docker compose down -v

# Remove everything including images
docker compose down --rmi all -v
```

---

## What You're Trying to Do

You started services with `docker compose up` and now want to clean up. You're not sure whether to use `docker compose stop` or `docker compose down`, or how to also remove volumes and images.

---

## Environment

- Docker Engine 24.x or later
- Docker Compose v2 (`docker compose` command)
- OS: Ubuntu 22.04 / macOS / WSL2

> **Note:** The same options work with legacy `docker-compose` (v1).

---

## Solution

### Basic Usage

```bash
docker compose down
```

This single command does all of the following:

1. **Stops** running containers
2. **Removes** containers
3. **Removes** networks created by Compose

Volumes and images are **preserved** by default.

### Remove Volumes Too

```bash
docker compose down -v
# or
docker compose down --volumes
```

Adding `-v` removes the **named volumes** defined in your `docker-compose.yml`. Be careful — this deletes persistent data like database files.

### Remove Images Too

```bash
# Remove all images used by the Compose project
docker compose down --rmi all

# Remove only images built locally
docker compose down --rmi local
```

### Full Reset (Remove Everything)

```bash
docker compose down --rmi all -v
```

This removes containers, networks, volumes, and images in one command — a full development environment reset.

### Stop and Remove a Specific Service

```bash
# Remove only the web service container
docker compose down web
```

### Set a Custom Timeout

```bash
# Wait up to 60 seconds before forcibly stopping (default is 10)
docker compose down -t 60
```

---

## docker compose stop vs docker compose down

| Command | Stops containers | Removes containers | Removes networks |
|---------|-----------------|-------------------|-----------------|
| `docker compose stop` | ✅ | ❌ | ❌ |
| `docker compose down` | ✅ | ✅ | ✅ |

Use `stop` when you want to pause and resume later (`stop` → `start`).  
Use `down` when you want to fully clean up the environment.

---

## Common Errors

### `Error response from daemon: removal of container ... is already in progress`

Another process is already operating on that container. Wait a moment and retry.

```bash
# Force remove all containers if needed
docker rm -f $(docker ps -aq)
```

### `network ... has active endpoints`

Another container is still connected to the network.

```bash
# Check what's using the network
docker network inspect <network_name>

# Stop all containers first, then run down again
docker compose down
```

### `volume is in use`

The volume is attached to another container.

```bash
# Check which container is using the volume
docker ps -a --filter volume=<volume_name>

# Remove the container first, then clean up
docker compose down -v
```

### Permission denied (socket error)

```bash
sudo docker compose down
# or add your user to the docker group
sudo usermod -aG docker $USER
```

---

## FAQ

**Q: What is the difference between `docker compose down` and `docker compose rm`?**  
`down` stops running containers, then removes containers and networks all at once. `rm` only removes **already-stopped** containers without touching networks or doing any stopping.

**Q: I forgot to use `-v`. Can I remove volumes later?**  
Yes. Run `docker volume ls` to find the volume name, then `docker volume rm <name>` to delete it. To remove all unused volumes at once, use `docker volume prune`.

**Q: My data disappeared after running `down`. What happened?**  
If you used the `-v` flag, named volumes are deleted. Also, if your containers wrote data inside the container filesystem (not to a mounted volume), that data is gone when the container is removed.

**Q: Does `docker compose down` remove images?**  
No, not by default. Add `--rmi all` to also remove the images used by your Compose project.

**Q: How do I target a specific Compose file?**  
Use the `-f` flag to specify a file:

```bash
docker compose -f docker-compose.prod.yml down
```

**Q: Can I remove containers without stopping them first?**  
`docker compose down` handles the stop step automatically, so running containers are safely stopped before being removed.

---

## Related Articles

- [Getting Started with docker compose](/en/docker-compose-basic)
- [docker system prune: Clean Up Unused Docker Resources](/en/docker-system-prune)
- [Docker Volume Basics](/en/docker-volume-basics)
- [docker logs: View Container Logs](/en/docker-logs)

## Recommended VPS / Hosting

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
