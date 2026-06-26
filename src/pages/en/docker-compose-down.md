---
title: 'docker compose down: How to Stop and Remove Containers, Networks, and Volumes'
date: '2026-06-26'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker-compose', 'container management']
description: 'Learn how to use docker compose down with --volumes and --rmi options to cleanly remove containers, networks, and volumes from your Docker Compose project.'
---

## Quick Answer

```bash
# Stop and remove containers and networks
docker compose down

# Also remove named volumes (data will be deleted)
docker compose down --volumes

# Also remove images
docker compose down --rmi all
```

---

## What You're Trying to Do

You started multiple containers with `docker compose up` and now want to stop and clean them all up at once. Running `docker stop` on each container individually is tedious — `docker compose down` handles everything in one command.

---

## Environment

- Docker 24.x or later
- Docker Compose V2 (`docker compose` command)
- OS: Ubuntu 22.04 / macOS

> **Note:** `docker-compose` (with hyphen) is Compose V1. The current standard is `docker compose` (with space) V2.

---

## Solution

### Basic: Remove Containers and Networks

```bash
docker compose down
```

Run this in the directory containing your `docker-compose.yml`.

Example output:

```
[+] Running 3/3
 ✔ Container myapp-web-1    Removed
 ✔ Container myapp-db-1     Removed
 ✔ Network myapp_default    Removed
```

This stops and removes all containers and the automatically created network. **Named volumes are preserved.**

---

### Also Remove Volumes

```bash
docker compose down --volumes
# Short form
docker compose down -v
```

This also removes named volumes defined in the `volumes:` section. **Warning: database data will be lost.**

---

### Also Remove Images

```bash
# Remove all images used by the compose project
docker compose down --rmi all

# Remove only locally built images (keep pulled images)
docker compose down --rmi local
```

---

### Combining Options

```bash
# Remove containers, networks, volumes, and images
docker compose down --volumes --rmi all
```

---

### Specify a Custom Compose File

```bash
docker compose -f docker-compose.prod.yml down
```

---

## Common Errors

### `no configuration file provided: not found`

```
no configuration file provided: not found
```

**Cause:** You ran the command in a directory without `docker-compose.yml`.  
**Fix:** Navigate to the correct directory first.

```bash
ls docker-compose.yml  # Verify the file exists
```

---

### `volume is in use`

```
Error response from daemon: remove myapp_db_data: volume is in use
```

**Cause:** Another container is using the volume.  
**Fix:** Stop and remove the container that's using it first.

```bash
docker ps -a  # Check all containers
docker rm -f <container-id>
docker compose down --volumes
```

---

### `permission denied`

**Cause:** No permission to access the Docker daemon.  
**Fix:** Use `sudo` or add your user to the `docker` group.

```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## FAQ

**Q: What's the difference between `docker compose stop` and `docker compose down`?**  
`stop` halts containers but keeps them. `down` stops and removes them. Use `stop` → `start` for restarts; use `down` → `up` for a full reset.

**Q: Will `docker compose down` delete my database data?**  
Not unless you add `--volumes`. Named volumes (like `db_data`) persist by default. Adding `-v` will delete them permanently.

**Q: After `docker compose down`, can I restore the state with `docker compose up`?**  
Containers will be recreated, but if you deleted volumes with `--volumes`, the data is gone. Images remain locally so no re-download is needed.

**Q: Can I down just one specific service?**  
`down` acts on the whole project. To stop a single service use `docker compose stop <service>` instead.

**Q: What's the difference between `docker compose down` and `docker system prune`?**  
`down` targets only the resources of your compose project. `system prune` removes all unused resources system-wide. Use `down` to avoid accidentally deleting unrelated resources.

---

## Related Articles

- [docker compose up: Basic Usage Guide](/en/docker-compose-basic)
- [How to View Docker Container Logs](/en/docker-logs)
- [Docker Volume Basics](/en/docker-volume-basics)
- [How to Delete Docker Images and Containers](/en/docker-delete-image-container)
- [Docker Image Cleanup](/en/docker-image-cleanup)

## Recommended VPS / Hosting

If you want to run Docker in a production environment, check out these VPS providers:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
