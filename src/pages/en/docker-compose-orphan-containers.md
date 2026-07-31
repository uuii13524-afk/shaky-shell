---
title: 'Fix "Found orphan containers" Warning in docker compose'
date: '2026-07-31'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
description: 'docker compose up/down prints "Found orphan containers" and a container for a service you deleted from compose.yaml keeps running. Here is why, and how to clean it up safely with --remove-orphans.'
en_tags: ['Docker', 'Docker Compose', 'orphan containers']
---

## What I Was Trying to Do

I had a project called `myapp` with three services in `compose.yaml`: `web`, `worker`, and `redis`. We decided to move `worker` to a separate host, so I removed its definition from `compose.yaml` and ran `docker compose up -d` to bring up the remaining services.

```bash
docker compose up -d
```

```text
[+] Running 3/3
 ✔ Container myapp-redis-1  Started
 ✔ Container myapp-web-1    Started
WARN[0000] Found orphan containers ([myapp-worker-1]) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up.
```

The command didn't fail — `web` and `redis` started fine — but I got a warning about the service I had just deleted. Checking further, the `worker` container was still running.

```bash
docker ps --filter "label=com.docker.compose.project=myapp" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
```

```text
NAMES              IMAGE              STATUS
myapp-web-1        myapp-web:latest   Up 5 seconds
myapp-redis-1      redis:7            Up 5 seconds
myapp-worker-1     myapp-worker:old   Up 3 days
```

Removing the service definition from `compose.yaml` apparently didn't stop the existing container by itself.

## Environment

- OS: Ubuntu 22.04.4 LTS
- Docker Engine: 26.1.3
- Docker Compose: v2.27.0 (the `docker compose` plugin, not the legacy standalone `docker-compose` binary)
- Project name: `myapp`, derived automatically from the directory name (`COMPOSE_PROJECT_NAME` not set)
- Removed service: `worker` (deleted from `compose.yaml`, being moved to a separate host)

## What I Tried

My first assumption was that `docker compose down` would clean up every container tied to the project.

```bash
docker compose down
```

```text
[+] Running 2/2
 ✔ Container myapp-web-1    Removed
 ✔ Container myapp-redis-1  Removed
```

`web` and `redis` were removed, but nothing happened to `worker`. Checking `docker ps` again, `myapp-worker-1` was still running.

```bash
docker ps --filter "label=com.docker.compose.project=myapp"
```

```text
CONTAINER ID   IMAGE               COMMAND      STATUS
7f1a2b3c4d5e   myapp-worker:old    "node worker.js"   Up 3 days
```

`down` only acts on the services currently listed in `compose.yaml` — `worker`, having been removed from the file, was outside its scope. I confirmed I could remove it manually with `docker rm -f`, but that meant repeating manual cleanup every time a service was retired. I wanted a proper fix instead.

## Why This Happens

Docker Compose tags every container it creates with `com.docker.compose.project` (the project name) and `com.docker.compose.service` (the service name). When you run `docker compose up` or `docker compose down`, Compose compares the service names currently defined in `compose.yaml` against the containers that actually carry that project's label.

Any container that carries the project label but whose service name is no longer in `compose.yaml` — `worker`, in this case — gets flagged as an "orphan container." Compose warns about it but **does not remove it by default**, for both `up` and `down`. This is a deliberate safety default: it prevents Compose from silently deleting a running container (and any data attached to it) just because its entry was removed from the file, intentionally or by mistake. Nothing was broken here — it was Compose behaving as designed.

## Solution

### 1. List every container tied to the project

```bash
docker ps -a --filter "label=com.docker.compose.project=myapp" --format "table {{.Names}}\t{{.Label \"com.docker.compose.service\"}}\t{{.Status}}"
```

Check for any service name that no longer appears in `compose.yaml`.

### 2. Check whether the orphan container has a named volume attached

Before removing anything, confirm whether it's using a named volume. Volumes aren't deleted along with the container, but it's worth checking both directions before you decide.

```bash
docker inspect myapp-worker-1 --format '{{ range .Mounts }}{{ .Name }} {{ end }}'
```

### 3. Re-run with `--remove-orphans`

Once you've confirmed it's safe to remove, add `--remove-orphans`.

```bash
docker compose up -d --remove-orphans
```

```text
[+] Running 2/2
 ✔ Container myapp-redis-1  Started
 ✔ Container myapp-web-1    Started
[+] Removing orphan containers
 ✔ Container myapp-worker-1  Removed
```

The same flag works with `down`.

```bash
docker compose down --remove-orphans
```

### 4. Remove any now-unneeded named volumes separately (if applicable)

Volumes survive orphan container removal, so clean up anything you've confirmed is no longer needed.

```bash
docker volume ls --filter "label=com.docker.compose.project=myapp"
docker volume rm myapp_worker-data
```

## Verify It Works

```bash
docker compose up -d --remove-orphans
docker ps --filter "label=com.docker.compose.project=myapp"
```

```text
NAMES            IMAGE              STATUS
myapp-web-1      myapp-web:latest   Up 10 seconds
myapp-redis-1    redis:7            Up 10 seconds
```

The `WARN` line is gone, and `docker ps` no longer lists anything related to `worker`.

## Gotchas

- I assumed `docker compose down` cleaned up the whole project, but it only touches services **currently defined in `compose.yaml`**. Anything removed from the file is out of its scope.
- `--remove-orphans` deletes containers immediately, with no confirmation prompt. If you split your setup across multiple `compose.yaml` files with `-f` but share the same project name, containers from a file you didn't mean to touch can get flagged as "orphans" too — so check `docker ps` before running it, not after.
- Named volumes survive even after the container using them is removed. That's reassuring — you won't lose data by accident — but it also means leftover volumes quietly eat disk space unless you clean them up with `docker volume rm` once you're sure they're no longer needed.

## FAQ

**Q: Is it safe to always run with `--remove-orphans`?**
Generally yes for a single `compose.yaml` under one project name. But if you combine multiple files with `-f` under the same project name, it can remove containers from a file you didn't intend to touch — check `docker ps` first.

**Q: Why doesn't Docker Compose remove orphan containers automatically?**
It's a safety default. If a service definition were removed from the file by mistake, auto-removing its container could destroy a running workload or data without warning.

**Q: What happens to a named volume the orphan container was using?**
It isn't deleted automatically. Once you've confirmed it's no longer needed, remove it separately with `docker volume rm` or `docker volume prune`.

## Related Articles

- [Basic docker compose Commands](/en/docker-compose-basic)
- [How docker compose down Works](/en/docker-compose-down)
- [Checking Logs with docker compose logs](/en/docker-compose-logs)
- [Cleaning Up with docker system prune](/en/docker-system-prune)
- [How to Remove Unused Docker Images](/en/docker-image-cleanup)
