---
title: 'docker stats Command Guide: Monitor Container CPU and Memory Usage in Real Time'
date: '2026-07-03'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker stats', 'container', 'resource monitoring', 'performance']
description: 'Learn how to monitor container CPU, memory, and network usage in real time with docker stats. Covers custom formatting, filtering by container, and logging output over time.'
---

## Quick Answer

```bash
# Show live resource usage for all containers
docker stats

# Show only a specific container
docker stats my-container

# Grab a single snapshot instead of streaming
docker stats --no-stream
```

---

## What You're Trying to Do

A container feels slow, or the host's CPU or memory seems maxed out, and you need to know exactly which container is responsible. `docker stats` shows per-container CPU usage, memory usage, network I/O, and disk I/O in real time — it's the Docker equivalent of `top` or `htop`.

---

## Environment

- Docker Engine 24.x or later (Docker Desktop works the same way)
- OS: Linux / macOS / Windows (WSL2)

---

## Solution

### Basic: Show Usage for All Containers

```bash
docker stats
```

Example output:
```
CONTAINER ID   NAME           CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O
a1b2c3d4e5f6   web-app        2.34%     120.5MiB / 1.944GiB   6.05%     1.2MB / 850kB     0B / 0B
b2c3d4e5f6a1   db             15.67%    512.3MiB / 1.944GiB   25.72%    3.4MB / 2.1MB     45MB / 12MB
```

Press `Ctrl + C` to exit. By default the display refreshes every 1-2 seconds.

### Show Only Specific Containers

```bash
docker stats web-app db
```

Pass multiple container names or IDs separated by spaces.

### Grab a Single Snapshot (--no-stream)

Useful in scripts where you want one reading instead of continuous monitoring.

```bash
docker stats --no-stream
```

### Customize the Output Columns (--format)

Use a Go template to control which fields are printed.

```bash
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

Example output:
```
NAME       CPU %     MEM USAGE / LIMIT
web-app    2.34%     120.5MiB / 1.944GiB
db         15.67%    512.3MiB / 1.944GiB
```

### Output as JSON (for Scripting)

```bash
docker stats --no-stream --format "{{json .}}"
```

Combine with `jq` to extract specific fields.

```bash
docker stats --no-stream --format "{{json .}}" | jq -r '.Name + ": " + .CPUPerc'
```

### Log Usage at a Regular Interval

```bash
while true; do
  docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}}" >> stats.csv
  sleep 60
done
```

---

## Common Errors

### Numbers Stay at `0.00%` and Never Change

The container may be nearly idle, or you only checked without `--no-stream` for a split second. Put some load on it first.

```bash
# Generate load inside the container, then check
docker exec my-container stress --cpu 2 --timeout 30s
docker stats my-container
```

### `MEM LIMIT` Looks Too High or Too Low

Unless you set an explicit limit with `docker run --memory`, the displayed limit is the host's total available memory.

```bash
# Start a container with an explicit memory limit
docker run --memory="512m" --name my-container my-image
```

### `docker stats` Feels Slow

With a large number of running containers, the live display can lag. Narrow the scope to speed it up.

```bash
docker stats $(docker ps --format "{{.Names}}" | grep app)
```

### CPU Percentage Goes Above 100% on Windows/WSL2

This is expected when a container uses multiple CPU cores — CPU% is reported per core (e.g., up to 400% on a 4-core host), not capped at 100%.

---

## FAQ

**Q: What's the difference between `docker stats` and `docker top`?**
`docker stats` shows aggregate CPU, memory, and I/O metrics for a container in real time. `docker top` lists the processes currently running inside a container — a different purpose entirely.

**Q: Can I see stats for stopped containers?**
No. `docker stats` only reports on running containers; stopped containers don't appear.

**Q: Why can CPU usage exceed 100%?**
CPU% in `docker stats` is calculated against the host's total logical cores, so fully utilizing multiple cores can push it well past 100% (e.g., up to 400% on 4 cores).

**Q: Does this work with docker-compose projects?**
Yes. `docker stats` treats containers started by Docker Compose the same as any other container. Pass the specific container name if you only want one service.

**Q: How do I actually cap resource usage instead of just watching it?**
Use `--cpus` and `--memory` when starting the container.

```bash
docker run --cpus="1.5" --memory="1g" my-image
```

**Q: Is there an equivalent for Kubernetes?**
`kubectl top pod` shows similar per-pod CPU and memory usage (requires the metrics-server add-on).

---

## Related Articles

- [docker logs Command Guide: View, Follow, and Filter Container Logs](/en/docker-logs)
- [docker exec: Enter a Running Container](/en/docker-exec-bash)
- [Managing Docker Containers (ps / stop / rm)](/en/docker-delete-image-container)
- [Reclaim Disk Space with docker system prune](/en/docker-system-prune)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
