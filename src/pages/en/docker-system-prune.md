---
title: 'How to Use docker system prune to Free Up Disk Space'
date: '2026-06-29'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker system prune', 'disk space', 'cleanup', 'remove containers']
description: 'Learn how to use docker system prune to remove stopped containers, unused images, volumes, and build cache. Covers all options with practical examples.'
---

## Quick Answer

```bash
# Remove stopped containers, unused networks, and dangling images
docker system prune

# Remove everything including all unused images and volumes (use with caution)
docker system prune -a --volumes
```

---

## What You're Trying to Do

After prolonged Docker usage, stopped containers and unused images accumulate and eat up disk space. Running `df -h` and finding almost no free space is a common trigger for reaching for `docker system prune`. This guide covers every option and shows you exactly what gets deleted.

---

## Environment

- OS: Ubuntu 22.04 / macOS Ventura
- Docker: 24.x or later

---

## Solution

### Basic Usage

```bash
docker system prune
```

This removes:

- Stopped containers (status: `Exited`)
- Networks not used by any container
- Dangling images (untagged, unreferenced)
- Build cache

To skip the confirmation prompt:

```bash
docker system prune -f
```

### Remove All Unused Images

```bash
docker system prune -a
```

The `-a` / `--all` flag extends deletion to all images not referenced by any container — not just dangling ones. Useful for reclaiming large amounts of disk space in development environments.

### Include Volumes

```bash
docker system prune -a --volumes
```

**Warning:** `--volumes` also deletes named volumes, which may contain database data or other persistent state. Verify what volumes exist before running this.

### Preview What Will Be Deleted

```bash
# List stopped containers
docker ps -a --filter "status=exited"

# List dangling images
docker images -f "dangling=true"

# List volumes
docker volume ls
```

### Check Disk Usage After Pruning

```bash
docker system df
```

| Type | SIZE | RECLAIMABLE |
|------|------|-------------|
| Images | 3.2GB | 1.1GB |
| Containers | 0B | 0B |
| Volumes | 500MB | 200MB |
| Build Cache | 800MB | 800MB |

The `RECLAIMABLE` column shows how much space you can actually recover.

---

## Common Errors

### `Error response from daemon: conflict`

Resources in use by running containers are skipped, not deleted. This is expected behavior — not an error.

### `permission denied`

```bash
sudo docker system prune
```

On Linux, if your user isn't in the `docker` group, you'll need `sudo`.

### Accidentally Deleted a Volume

If you ran `--volumes` and lost data without a backup, recovery is extremely difficult. Always run `docker volume inspect <name>` to check the mount path and back up important data to the host before pruning.

---

## FAQ

**Q: Will running containers be affected?**
No. `docker system prune` only targets stopped resources. Running containers, the images they use, and their volumes are left untouched.

**Q: What's the difference between `docker image prune` and `docker system prune`?**
`docker image prune` removes only images. `docker system prune` also removes stopped containers, unused networks, and build cache — a broader sweep in a single command.

**Q: Can I automate this on a schedule?**
Yes — add it to cron:

```bash
# Run every Sunday at 1 AM (no confirmation prompt)
0 1 * * 0 docker system prune -f >> /var/log/docker-prune.log 2>&1
```

**Q: How do I remove only the build cache?**

```bash
docker builder prune
```

This removes the build cache without touching containers or images.

**Q: What's the difference between using `-a` and not using it?**
Without `-a`, only dangling images (untagged) are removed. With `-a`, all images not referenced by any container are removed — including images you pulled but haven't run yet. Be careful with `-a` in shared environments.

**Q: Does this work on Windows with Docker Desktop?**
Yes. Run the same commands from PowerShell or a WSL2 terminal.

---

## Related Articles

- [docker image cleanup — Remove Unused Docker Images](/en/docker-image-cleanup)
- [docker logs — View Container Logs](/en/docker-logs)
- [Docker Volume Basics — Persist Data in Containers](/en/docker-volume-basics)
- [Docker Network Basics — Understand Container Networking](/en/docker-network-basics)

## Recommended VPS / Hosting

Looking to run Docker in production? These services are solid choices:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
