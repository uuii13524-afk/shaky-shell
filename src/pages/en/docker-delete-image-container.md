---
title: 'How to Delete Docker Images and Containers (with Examples)'
date: '2026-06-26'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker rmi', 'docker rm', 'delete image', 'remove container']
description: 'How to delete Docker images and containers with docker rmi and docker rm. Covers single deletions, bulk removal, force delete, and common errors.'
---

## Quick Answer

```bash
# Delete a specific image
docker rmi IMAGE_NAME:TAG

# Delete a specific container
docker rm CONTAINER_ID

# Delete all stopped containers
docker container prune

# Delete all unused images
docker image prune -a
```

---

## How to Delete a Docker Image

### Delete by name and tag

```bash
docker rmi nginx:1.25
docker rmi ubuntu:22.04
```

### Delete by image ID

```bash
# Get the image ID first
docker images

# Delete by ID (first few chars is enough)
docker rmi a1b2c3
```

### Force delete (even if a container references it)

```bash
docker rmi -f IMAGE_ID
```

### Delete multiple images at once

```bash
docker rmi image1 image2 image3
```

### Delete all dangling images (`<none>`)

```bash
docker image prune
```

### Delete all unused images

```bash
docker image prune -a
```

---

## How to Delete a Docker Container

### Delete a stopped container

```bash
# List all containers first
docker ps -a

# Delete by ID or name
docker rm CONTAINER_ID
docker rm my-container
```

### Force delete a running container

```bash
docker rm -f CONTAINER_ID
```

### Delete all stopped containers

```bash
docker container prune
```

### Delete all containers (running and stopped)

```bash
docker rm -f $(docker ps -a -q)
```

---

## Delete Images and Containers Together

```bash
# Remove stopped containers, unused images, unused networks
docker system prune

# Also remove volumes
docker system prune --volumes

# Remove everything unused without confirmation
docker system prune -a -f
```

---

## Common Errors

### `unable to delete — image is being used by running container`

Stop or remove the container first, then delete the image:

```bash
docker rm -f CONTAINER_ID
docker rmi IMAGE_ID
```

Or force delete the image directly:

```bash
docker rmi -f IMAGE_ID
```

### `Error: No such image` / `Error: No such container`

The name or ID is wrong. List what exists:

```bash
docker images      # list images
docker ps -a       # list all containers
```

---

## FAQ

**Q: How do I delete a Docker image?**
`docker rmi IMAGE_NAME:TAG`. Use `docker images` to find the name and tag first.

**Q: How do I delete a Docker container?**
`docker rm CONTAINER_ID` for stopped containers. For running containers, use `docker rm -f CONTAINER_ID`.

**Q: How do I delete all Docker images?**
`docker image prune -a` removes all unused images. To force-remove everything: `docker rmi -f $(docker images -q)`.

**Q: Why can't I delete a Docker image?**
A container (running or stopped) is referencing that image. Remove the container first: `docker rm -f CONTAINER_ID`, then delete the image.

**Q: How do I delete all stopped containers?**
`docker container prune` removes all containers with status `exited`.

**Q: What is the difference between `docker rmi` and `docker image prune`?**
`docker rmi` targets a specific image by name or ID. `docker image prune` bulk-removes dangling or unused images.

---

## Related Articles

- [How to Clean Up Docker Images, Containers, and Volumes](/en/docker-image-cleanup)
- [Docker Basic Commands Cheat Sheet](/en/docker-basic-commands)
- [How to Use docker exec to Run Commands in a Container](/en/docker-exec-bash)
- [Persisting Data with Docker Volumes](/en/docker-volume-basics)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
