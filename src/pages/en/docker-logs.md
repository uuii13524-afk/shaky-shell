---
title: 'docker logs Command Guide: View, Follow, and Filter Container Logs'
date: '2026-06-25'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker logs', 'container', 'logs', 'debugging']
description: 'Complete guide to the docker logs command. Learn how to stream logs in real time (-f), limit output (--tail), add timestamps, filter by time, and extract errors.'
---

## Quick Answer

```bash
# Show all logs for a container
docker logs <container-name-or-id>

# Follow logs in real time (like tail -f)
docker logs -f <container-name>

# Show only the last 100 lines
docker logs --tail 100 <container-name>
```

---

## What You're Trying to Do

When a Docker container won't start, an app misbehaves, or something throws an error, you need to see what's happening inside. `docker logs` prints the standard output (stdout) and standard error (stderr) of a container — making it the go-to tool for debugging.

---

## Environment

- Docker Engine 24.x or later (Docker Desktop works the same way)
- OS: Linux / macOS / Windows (WSL2)

---

## Solution

### Basic: Print All Logs

```bash
docker logs my-container
```

You can also use the first few characters of a container ID:

```bash
docker logs a1b2c3d4
```

### Stream Logs in Real Time (-f / --follow)

```bash
docker logs -f my-container
```

Press `Ctrl + C` to stop. Useful right after deploying or restarting an app.

### Show Only the Last N Lines (--tail)

```bash
# Last 50 lines
docker logs --tail 50 my-container

# Last 100 lines, followed in real time
docker logs -f --tail 100 my-container
```

### Add Timestamps (-t / --timestamps)

```bash
docker logs -t my-container
```

Example output:
```
2026-06-25T08:30:01.123456789Z Server started on port 3000
2026-06-25T08:30:02.456789012Z Connected to database
```

### Filter by Time (--since / --until)

```bash
# Logs from the last hour
docker logs --since 1h my-container

# Logs from a specific time onward
docker logs --since "2026-06-25T08:00:00" my-container

# Logs up to a specific time
docker logs --until "2026-06-25T09:00:00" my-container

# Combine both
docker logs --since "2026-06-25T08:00:00" --until "2026-06-25T09:00:00" my-container
```

### Extract Error Logs (stderr)

```bash
# Merge stderr into stdout and grep for errors
docker logs my-container 2>&1 | grep -i error

# Match multiple patterns
docker logs my-container 2>&1 | grep "ERROR\|WARN\|Exception"
```

### Viewing Logs in a docker-compose Project

```bash
# Logs for a specific service
docker-compose logs app

# Follow all services
docker-compose logs -f

# Last 50 lines from all services
docker-compose logs --tail 50
```

---

## Common Errors

### `Error: No such container: xxx`

```
Error response from daemon: No such container: my-container
```

The container name or ID is wrong. List your containers first:

```bash
# Running containers
docker ps

# All containers including stopped ones
docker ps -a
```

### No Output Displayed

If the app writes logs to a file instead of stdout, `docker logs` shows nothing.

```bash
# Read a log file inside the container
docker exec my-container cat /var/log/app.log
```

Reconfiguring the app to write to stdout is the recommended long-term fix.

### `unknown flag: --tail`

You may be running an outdated Docker version:

```bash
docker --version
# Docker version 24.x.x or later recommended
```

### Too Many Logs to Read

```bash
# Page through with less
docker logs my-container 2>&1 | less

# Save to a file
docker logs my-container > container.log 2>&1
```

---

## FAQ

**Q: Can I view logs from a stopped container?**
Yes. Use `docker ps -a` to find its ID, then run `docker logs <ID>`. Logs persist on the host even after a container stops.

**Q: What's the difference between `docker logs -f` and `tail -f`?**
`docker logs -f` fetches logs through Docker's logging driver. `tail -f` watches a file directly. To monitor a file inside a container you would need `docker exec` combined with `tail -f`.

**Q: Is there a size or time limit on stored logs?**
The default driver (`json-file`) accumulates logs indefinitely. For production, add size limits in `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

**Q: Where does Docker physically store the log data?**
By default at `/var/lib/docker/containers/<container-id>/<container-id>-json.log` in JSON format.

**Q: Does the equivalent command work on Kubernetes?**
On Kubernetes use `kubectl logs <pod-name>`. Many options are the same — `-f` for follow and `--tail` for line limits.

**Q: What happens if I change the logging driver?**
Switching to `syslog`, `fluentd`, or another driver may disable `docker logs`. For production, consider a centralized logging stack such as Fluentd + Elasticsearch.

---

## Related Articles

- [docker exec: Enter a Running Container](/en/docker-exec-bash)
- [Docker Compose Basics](/en/docker-compose-basic)
- [Managing Docker Containers (ps / stop / rm)](/en/docker-delete-image-container)
- [Docker Networking Basics](/en/docker-network-basics)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
