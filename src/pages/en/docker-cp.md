---
title: 'docker cp Command Guide: Copying Files Between Host and Container'
date: '2026-07-05'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker cp', 'file copy', 'container']
description: 'Learn how to copy files and directories between the host and a Docker container with docker cp, including stopped containers and common permission errors.'
---

## Quick Answer

```bash
# Copy from host to container
docker cp ./local-file.txt my-container:/app/file.txt

# Copy from container to host
docker cp my-container:/app/file.txt ./local-file.txt
```

---

## What You're Trying to Do

Sometimes you just need to drop a single config file into a running container, or pull a log file or DB dump out of one, without rebuilding the whole image. `docker cp` copies files and directories between the host and a container, making it ideal for quick, one-off transfers that don't require changing the Dockerfile or rebuilding.

---

## Environment

- Docker: verified on 20.10 and later
- OS: Linux / macOS / Windows (WSL2)

---

## Solution

### 1. Find the Container Name or ID

```bash
docker ps
```

```
CONTAINER ID   IMAGE     NAMES
a1b2c3d4e5f6   nginx     my-container
```

Use the value in the `NAMES` column (`my-container`) or the `CONTAINER ID`.

### 2. Copy From Host to Container

```bash
docker cp ./config.yml my-container:/etc/app/config.yml
```

The destination directory (`/etc/app/` in this example) must already exist inside the container, or the copy will fail.

### 3. Copy From Container to Host

```bash
docker cp my-container:/var/log/app.log ./app.log
```

This is the pattern you'll use most often to pull log files or database dumps out to the host.

### 4. Copy an Entire Directory

```bash
# Host to container (whole directory)
docker cp ./dist my-container:/usr/share/nginx/html

# Container to host (whole directory)
docker cp my-container:/app/logs ./logs
```

The same `docker cp` command works for both files and directories.

### 5. Copy to a Stopped Container

```bash
docker ps -a
docker cp ./config.yml stopped-container:/etc/app/config.yml
```

`docker cp` works even if the container isn't running, since it operates directly on the container's filesystem rather than on a live process.

### 6. Finding Container Names in docker-compose

```bash
docker compose ps
```

Containers started with `docker compose` are often named like `project_service_1`. Check the exact name with `docker ps` or `docker compose ps` before copying.

---

## Common Errors

### `Error: No such container:path: my-container:/app/file.txt`

The source path doesn't exist inside the container. Check it directly:

```bash
docker exec -it my-container ls /app
```

### `lstat /path/to/local-file: no such file or directory`

The source path on the host is wrong. If you're using a relative path, double-check your current directory.

```bash
pwd
ls -la ./local-file.txt
```

### Destination Directory Doesn't Exist

```
Error response from daemon: ... no such file or directory
```

`docker cp` fails if the destination directory doesn't already exist inside the container. Create it first:

```bash
docker exec my-container mkdir -p /etc/app
docker cp ./config.yml my-container:/etc/app/config.yml
```

### Copied File Ends Up Owned by root

`docker cp` often copies files in as root by default, which can cause permission errors if the app runs as a different user.

```bash
docker exec my-container chown appuser:appuser /app/file.txt
```

---

## FAQ

**Q: Does `docker cp` work on a stopped container?**
Yes. It accesses the container's filesystem directly, so it works whether or not the container is running.

**Q: Can I use wildcards (`*`)?**
No, `docker cp` doesn't support wildcards directly. To copy multiple files, copy the whole containing directory, or combine it with `tar`.

**Q: How are symbolic links handled?**
By default, `docker cp` copies the symlink itself rather than the file it points to. Use the `-L` flag if you want to follow the link and copy the target.

**Q: When should I use `docker cp` vs. a bind mount (`-v`)?**
Use a bind mount if you need files to stay continuously in sync. `docker cp` is better suited for a one-time, temporary transfer.

**Q: Does it work with `docker-compose` setups?**
Yes. Check the container name with `docker compose ps` first, then use `docker cp` the same way as usual.

**Q: What happens if the container stops mid-copy?**
The copy is handled directly by the Docker daemon against the filesystem, so it's fairly resilient to state changes, but it's best practice to let a copy finish before performing other operations on the container.

---

## Related Articles

- [docker exec: Enter a Running Container](/en/docker-exec-bash)
- [Docker Volumes: The Basics](/en/docker-volume-basics)
- [How to Use the docker logs Command](/en/docker-logs)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
