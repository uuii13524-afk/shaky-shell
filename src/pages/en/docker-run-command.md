---
title: 'docker run Command Guide: Key Options and Common Errors'
date: '2026-07-11'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker run', 'troubleshooting']
description: 'Learn the docker run command syntax and key options like -d, -p, -v, --name, and --rm, plus fixes for common errors such as containers exiting immediately or port conflicts.'
---

## Quick Answer

```bash
# Start in the background with a port and volume mapped
docker run -d --name my-container -p 8080:80 -v /host/path:/container/path nginx
```

---

## What You're Trying to Do

You've pulled an image with `docker pull` but aren't sure how to actually run it as a container. Or you ran `docker run` and the container exited immediately, or a port conflict threw an error. This is where people usually start working through `docker run`'s options one by one.

`docker run` creates a container from an image and starts it — it's the single most fundamental and frequently used Docker command. Its behavior changes significantly depending on which options you combine, so it's worth knowing the common patterns cold.

---

## Environment

- Docker: verified on 20.10 and later
- OS: Linux / macOS / Windows (WSL2)

---

## Solution

### 1. Basic Syntax

```bash
docker run [options] <image-name> [command]
```

If the image isn't available locally, `docker pull` runs automatically before the container starts.

### 2. Running in the Background (-d)

```bash
docker run -d nginx
```

Without `-d` (`--detach`), the container runs in the foreground and ties up your terminal.

### 3. Naming a Container (--name)

```bash
docker run -d --name my-nginx nginx
```

If you skip `--name`, Docker assigns a random name automatically. Naming your containers makes them much easier to work with in `docker ps` and `docker logs`.

### 4. Publishing a Port (-p)

```bash
docker run -d -p 8080:80 nginx
```

The format is `-p <host-port>:<container-port>`. Requests to port `8080` on the host get forwarded to port `80` inside the container.

### 5. Mounting a Volume (-v)

```bash
docker run -d -v /host/path:/container/path nginx
```

This mounts a host directory into the container — commonly used for data persistence or sharing config files. For a named volume:

```bash
docker run -d -v my-volume:/container/path nginx
```

### 6. Passing Environment Variables (-e)

```bash
docker run -d -e NODE_ENV=production -e PORT=3000 my-app
```

### 7. Auto-removing the Container on Exit (--rm)

```bash
docker run --rm -it ubuntu bash
```

Useful for throwaway containers you use for a quick check and don't want left behind after they stop.

### 8. Getting an Interactive Shell (-it)

```bash
docker run -it ubuntu bash
```

Combining `-i` (keep stdin open) and `-t` (allocate a pseudo-terminal) gives you an interactive shell inside the container.

### 9. A Common Combination

```bash
docker run -d --name my-app --restart unless-stopped -p 3000:3000 -v ./data:/app/data -e NODE_ENV=production my-app:latest
```

---

## Common Errors

### The Container Exits Immediately

```
$ docker ps
(nothing shown)
```

When the main process started by `docker run` exits, the container stops too. If the base image only provides `bash` or `sh` with nothing keeping it running in the foreground, it exits right away. Check the last output before it stopped:

```bash
docker logs my-container
docker ps -a
```

### `Error response from daemon: driver failed programming external connectivity`

This happens when the host port you specified is already in use by another process.

```bash
# Check what's using the port
lsof -i :8080

# Re-run with a different port
docker run -d -p 8081:80 nginx
```

### `Unable to find image 'xxx:latest' locally`

Usually a typo in the image name or tag, or the image genuinely doesn't exist locally or in the registry. If the name is valid, Docker pulls it automatically; if it's wrong, the pull fails.

```bash
docker images
docker search <image-name>
```

### `docker: Error response from daemon: Conflict. The container name "/my-app" is already in use`

A container with that name already exists. Remove it or pick a different name.

```bash
docker rm my-app
# or
docker run -d --name my-app-2 nginx
```

### Volume-mounted Files Aren't Showing Up

Usually a path typo or a misunderstood relative path. Use an absolute path, or `$(pwd)`, to be safe.

```bash
docker run -d -v $(pwd)/data:/app/data my-app
```

---

## FAQ

**Q: What's the difference between `docker run` and `docker start`?**
`docker run` creates a new container from an image and starts it. `docker start` restarts a container that already exists (in a stopped state).

**Q: What's the difference between `docker run` and `docker create`?**
`docker create` only creates the container without starting it. `docker run` is effectively `docker create` followed by `docker start`.

**Q: Can I start multiple containers from the same image?**
Yes. Skip `--name` or give each one a different name, and you can run as many containers as you want from the same image.

**Q: What does uppercase `-P` do instead of `-p 8080:80`?**
`-P` (uppercase) automatically publishes every port listed in the Dockerfile's `EXPOSE` to a random host port.

**Q: Can I change options after a container is started?**
No. Options like `-p` and `-v` can only be set at container creation time. To change them, you need to remove the container and recreate it.

---

## Related Articles

- [docker exec: Getting a Bash Shell Inside a Container](/en/docker-exec-bash)
- [docker ps Command Guide](/en/docker-ps-command)
- [docker inspect Command Guide](/en/docker-inspect-command)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
