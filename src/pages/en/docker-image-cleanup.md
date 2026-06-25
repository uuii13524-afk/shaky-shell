---
title: 'How to Clean Up Docker Images, Containers, and Volumes (Prune Guide)'
date: '2026-06-06'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Docker', 'ディスク管理', 'docker system prune', 'イメージ削除', 'コンテナ削除']
en_tags: ['Docker', 'disk cleanup', 'docker system prune', 'image removal', 'container cleanup']
description: 'Remove unused Docker images, containers, volumes, and build cache with docker image prune, docker system prune, and docker rmi. Includes cron automation and FAQ.'
---

## Quick Answer

```bash
# Remove everything unused (images, containers, networks)
docker system prune -a

# Remove unused images only
docker image prune -a

# Remove a specific image
docker rmi IMAGE_ID
```

Run `docker system df` first to see what's actually taking up space.

---

## Check Disk Usage First

```bash
docker system df
```

Sample output:

```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          23        5         8.2GB     6.1GB (74%)
Containers      12        3         142MB     98MB (69%)
Local Volumes   8         4         2.3GB     1.1GB (47%)
Build Cache     0         0         0B        0B
```

The `RECLAIMABLE` column shows how much space you can recover.

---

## Remove All Unused Docker Resources at Once

```bash
# Remove stopped containers, unused images, unused networks
docker system prune

# Also remove unused volumes (WARNING: deletes data)
docker system prune --volumes

# Skip the confirmation prompt
docker system prune -a -f
```

`docker system prune -a` removes all images not used by a running container — not just dangling ones.

---

## Remove Docker Images

```bash
# Remove dangling images only (<none>:<none>)
docker image prune

# Remove ALL unused images
docker image prune -a

# Remove a specific image by ID or name
docker rmi nginx:1.25
docker rmi IMAGE_ID

# Force remove (even if tagged or referenced)
docker rmi -f IMAGE_ID
```

Repeated builds without tagging produce `<none>` images that accumulate silently. These are usually the biggest disk hogs.

### Remove Images Older Than a Specific Time

```bash
# Remove images unused for more than 24 hours
docker image prune -a --filter "until=24h"

# Remove images unused for more than 7 days
docker image prune -a --filter "until=168h"
```

---

## Remove Docker Containers

```bash
# Remove all stopped containers
docker container prune

# Remove a specific container
docker rm CONTAINER_ID

# Force remove a running container
docker rm -f CONTAINER_ID

# List stopped containers before removing
docker ps -a --filter status=exited

# Remove all stopped containers at once
docker rm $(docker ps -a -q --filter status=exited)
```

---

## Remove Docker Volumes

```bash
# Remove all unused volumes
docker volume prune

# List volumes first
docker volume ls

# Remove a specific volume by name
docker volume rm VOLUME_NAME
```

Be careful: unused volumes that contain database data will be permanently deleted.

---

## Remove Build Cache

Build cache accumulates on CI/CD systems and can reach several GB.

```bash
# Remove all build cache
docker builder prune -f

# Remove only cache older than 48 hours
docker builder prune --filter "until=48h"
```

---

## Automate Cleanup with Cron

```bash
# Edit crontab
crontab -e

# Run docker image prune every Sunday at 2am
0 2 * * 0 docker image prune -af >> /var/log/docker-cleanup.log 2>&1
```

---

## Common Pitfalls

- `docker system prune` skips images used by running containers, but removes images used by **stopped** containers
- `docker system prune --volumes` before `docker-compose down` can delete volumes still referenced by compose
- `docker image prune -a` means Docker must re-pull all images on next run — avoid on production
- `--volumes` removes database data — only use on dev environments

---

## FAQ

**Q: What is the docker command to remove unused images?**
`docker image prune -a` removes all unused images. Without `-a`, only dangling (`<none>`) images are removed.

**Q: How do I remove all Docker images at once?**
`docker rmi $(docker images -q)`. This fails for images used by running containers — add `-f` to force.

**Q: What is the difference between `docker image prune` and `docker image prune -a`?**
Without `-a`, only dangling (untagged `<none>`) images are removed. With `-a`, all images not used by a running container are removed.

**Q: How do I remove a Docker image by name?**
`docker rmi IMAGE_NAME:TAG`, for example `docker rmi nginx:1.24`.

**Q: Does `docker system prune` delete volumes?**
Not by default. Add the `--volumes` flag explicitly: `docker system prune --volumes`.

**Q: How do I see what Docker is using for disk space?**
`docker system df` for a summary. `docker system df -v` for per-image/container detail.

---

## Related Articles

- [How to Delete Docker Images and Containers](/en/docker-delete-image-container)
- [Docker Basic Commands Cheat Sheet](/en/docker-basic-commands)
- [Persisting Data with Docker Volumes](/en/docker-volume-basics)
- [Getting Started with docker-compose](/en/docker-compose-basic)
- [Setting Up Docker on a VPS for Production](/en/vps-docker-setup)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
