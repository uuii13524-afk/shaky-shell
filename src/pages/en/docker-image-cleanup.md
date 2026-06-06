---
title: 'How to Remove Unused Docker Images, Containers, and Volumes to Free Up Disk Space'
date: '2026-06-06'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Docker', 'ディスク管理', 'docker system prune', 'イメージ削除', 'コンテナ削除']
en_tags: ['Docker', 'disk cleanup', 'docker system prune', 'image removal', 'container cleanup']
description: 'Learn how to clean up unused Docker images, containers, and volumes with docker system prune to reclaim disk space on your VPS or local machine.'
---
## What I Wanted to Do
After running Docker on a VPS for a few months, the disk usage spiked and deployments started failing.
Running `df -h` showed `/var` was nearly full — the culprit was a pile of accumulated Docker images and build cache.

## Check Current Disk Usage First

Before deleting anything, check what's taking up space.

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

The `RECLAIMABLE` column shows how much can be freed. Check this before deciding what to delete.

## Delete Everything at Once (docker system prune)

The fastest way to clean up is using `docker system prune`.

```bash
# Remove stopped containers, unused images, and unused networks
docker system prune

# Also remove volumes (WARNING: data will be lost)
docker system prune --volumes

# Skip the confirmation prompt
docker system prune -f
```

Be careful with `--volumes` — it can wipe database data. Double-check that volumes are truly unused before running it.

## Remove Images Only

```bash
# Remove dangling (untagged) images only
docker image prune

# Remove all unused images
docker image prune -a

# Remove a specific image
docker rmi IMAGE_ID

# Force remove (even if tagged)
docker rmi -f IMAGE_ID
```

Repeatedly building images creates `<none>` tagged images that accumulate silently. These are often the biggest disk hogs.

## Remove Containers Only

```bash
# Remove all stopped containers
docker container prune

# Remove a specific container
docker rm CONTAINER_ID

# Force remove a running container
docker rm -f CONTAINER_ID

# List stopped containers before removing
docker ps -a --filter status=exited
```

## Remove Volumes Only

```bash
# Remove all unused volumes
docker volume prune

# List volumes first, then remove by name
docker volume ls
docker volume rm VOLUME_NAME
```

## Remove Build Cache

Build cache can grow to several GB on CI/CD systems that build frequently.

```bash
# Remove all build cache
docker builder prune

# Skip confirmation
docker builder prune -f
```

## Common Pitfalls
- `docker system prune` won't delete images used by running containers, but it will delete images used by stopped containers
- Running `docker system prune` without `docker-compose down` first can delete volumes managed by docker-compose
- The `--volumes` flag removes database data too — use with extreme caution on production
- `docker image prune -a` removes all unused images, meaning Docker will need to pull them again on next run
- Setting up a cron job to run `docker image prune -f` periodically is a simple way to prevent disk pressure

## Related Articles
- [Docker Basic Commands Cheat Sheet](/en/docker-basic-commands)
- [Persisting Data with Docker Volumes](/en/docker-volume-basics)
- [Getting Started with docker-compose](/en/docker-compose-basic)
- [Setting Up Docker on a VPS for Production](/en/vps-docker-setup)
- [Dockerfile Basics](/en/docker-dockerfile-basics)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
