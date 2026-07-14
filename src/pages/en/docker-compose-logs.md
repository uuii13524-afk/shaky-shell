---
title: 'docker compose logs: View and Follow Logs Across Multiple Services'
date: '2026-07-14'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker-compose', 'logs']
description: 'Learn how to use docker compose logs to view logs from all your services at once. Covers real-time following, filtering by service, and common error fixes.'
---

## Quick Answer

```bash
# Show logs from all services
docker compose logs

# Follow logs in real time
docker compose logs -f

# Show the last 100 lines for a specific service
docker compose logs -f --tail=100 web
```

---

## What You're Trying to Do

You started services with `docker compose up -d` and now can't tell whether a container crashed or is still running. With multiple services running, it's hard to figure out which container a log line even came from.

---

## Environment

- Docker Engine 24.x or later
- Docker Compose v2 (`docker compose` command)
- OS: Ubuntu 22.04 / macOS / WSL2

> **Note:** The same options work with legacy `docker-compose` (v1).

---

## Solution

### Basic Usage

```bash
docker compose logs
```

This shows stdout/stderr from **every service** defined in your `docker-compose.yml`. Each line is prefixed with a color-coded service name, so you can immediately tell which container it came from.

### Follow Logs in Real Time

```bash
docker compose logs -f
# or
docker compose logs --follow
```

Like `tail -f`, this streams new log output as it happens. Press Ctrl+C to stop.

### Filter to a Specific Service

```bash
docker compose logs web
docker compose logs web db
```

Pass one or more service names to narrow the output to just those services.

### Show Only Recent Logs

```bash
docker compose logs --tail=100 web
docker compose logs -f --tail=50
```

`--tail` limits how many lines are shown — useful when there's a huge backlog of past logs.

### Add Timestamps

```bash
docker compose logs -t
# or
docker compose logs --timestamps
```

Each line gets a timestamp, which is helpful when correlating with logs from other systems.

### Show Logs Since a Given Time

```bash
docker compose logs --since 2026-07-14T09:00:00
docker compose logs --since 30m
```

`--since` accepts an absolute timestamp or a relative duration like `30m` (30 minutes ago) or `2h` (2 hours ago) — handy for narrowing down when an incident started.

---

## docker logs vs docker compose logs

| Command | Target | Use case |
|---------|--------|----------|
| `docker logs <container>` | A single container | Check logs by container name/ID directly |
| `docker compose logs [service]` | One or more services managed by Compose | Check logs across services by name |

When you're running multiple containers together, `docker compose logs` is far more convenient since you don't need to look up container IDs each time.

---

## Common Errors

### No Logs Show Up at All

```bash
# Check whether the containers are actually running
docker compose ps

# Check for a typo in the service name
docker compose config --services
```

Either the container isn't running yet, or you've specified the wrong service name.

### `no such service: web`

You referenced a service name that isn't defined in `docker-compose.yml`.

```bash
docker compose config --services
```

Run this to see the correct service names.

### Logs Appear to Be Stuck on Old Output

```bash
docker compose logs -f --tail=0
```

`--tail=0` skips past history entirely and only waits for new log lines going forward, so you're not overwhelmed by a large buffered backlog.

### App Logs Are Delayed Due to Buffering

If your Node.js or Python app buffers stdout, log lines can appear in delayed batches instead of immediately.

```dockerfile
# Node.js example
ENV NODE_OPTIONS="--unhandled-rejections=strict"
```

```dockerfile
# Python example (disable buffering)
ENV PYTHONUNBUFFERED=1
```

---

## FAQ

**Q: What's the difference between `docker compose logs` and `docker compose logs -f`?**  
`docker compose logs` prints everything up to the current point and exits. Adding `-f` (`--follow`) keeps streaming new log output in real time.

**Q: Can I turn off the colored output?**  
Use the `--no-color` flag — useful when redirecting logs to a file.

```bash
docker compose logs --no-color > app.log
```

**Q: Can I still see logs after removing a container?**  
No. Removing a container deletes its logs too. If you need long-term retention, configure a logging driver other than the default `json-file` (such as `syslog` or `fluentd`), or have your app write logs to a file or ship them externally.

**Q: How do I filter for a specific error message?**  
Combine it with `grep`:

```bash
docker compose logs | grep -i error
```

**Q: There's too much log output flooding my terminal.**  
Limit it with `--tail`, or pipe it through `less` to page through it.

```bash
docker compose logs --tail=200 | less
```

---

## Related Articles

- [docker compose down: Stop and Remove Containers, Networks, and Volumes](/en/docker-compose-down)
- [docker logs: View Container Logs](/en/docker-logs)
- [Getting Started with docker compose](/en/docker-compose-basic)
- [docker ps: List Running Containers](/en/docker-ps-command)

## Recommended VPS / Hosting

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
