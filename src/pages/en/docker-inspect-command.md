---
title: 'docker inspect Command Guide: Viewing Container and Image Details'
date: '2026-07-09'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker inspect', 'troubleshooting']
description: 'Learn how to use docker inspect to view detailed container and image info such as IP address, environment variables, mounts, and health checks, including --format and jq usage.'
---

## Quick Answer

```bash
# Show full JSON details for a container
docker inspect <container-name-or-id>

# Extract a single field (IP address example)
docker inspect -f '{{.NetworkSettings.IPAddress}}' <container-name>
```

---

## What You're Trying to Do

You want to know what's actually going on inside a container: its IP address, which volumes are mounted, or some other detail that `docker ps` and `docker logs` simply don't show. This is usually the point where people discover `docker inspect`.

`docker inspect` dumps the full configuration of a Docker-managed object — a container, image, network, or volume — as JSON. Because there's so much data, the real skill is knowing how to filter down to the field you actually need.

---

## Environment

- Docker: verified on 20.10 and later
- OS: Linux / macOS / Windows (WSL2)

---

## Solution

### 1. Basic Syntax

```bash
docker inspect <container-name-or-id>
docker inspect <image-name-or-id>
```

As long as the container name and image name don't collide, `docker inspect` automatically figures out what type of object you mean. To be explicit, use `--type`.

```bash
docker inspect --type container <name>
docker inspect --type image <name>
```

### 2. Checking the IP Address

```bash
docker inspect -f '{{.NetworkSettings.IPAddress}}' <container-name>
```

If the container is attached to a custom network (created with `docker network create`) instead of the default bridge, use this instead:

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container-name>
```

### 3. Checking Environment Variables

```bash
docker inspect -f '{{.Config.Env}}' <container-name>
```

### 4. Checking Mounted Volumes

```bash
docker inspect -f '{{.Mounts}}' <container-name>
```

For a more readable view, pipe the full JSON into `jq`:

```bash
docker inspect <container-name> | jq '.[0].Mounts'
```

### 5. Checking Health Check Status

```bash
docker inspect -f '{{.State.Health.Status}}' <container-name>
```

Returns `healthy`, `unhealthy`, or `starting`. Images without a `HEALTHCHECK` defined return `<no value>`.

### 6. Checking the Exit Code

```bash
docker inspect -f '{{.State.ExitCode}}' <container-name>
```

Checking the exit code is usually the first step when investigating why a container crashed.

### 7. Inspecting Multiple Containers at Once

```bash
docker inspect -f '{{.Name}}: {{.State.Status}}' $(docker ps -aq)
```

---

## Common Errors

### `Error: No such object: <name>`

Usually a typo in the container or image name, or the object has already been removed. Verify the exact name first.

```bash
docker ps -a
docker inspect <correct-name>
```

### `template: :1: unexpected "}" in operand`

A syntax error in the Go template passed to `-f` (`--format`) — check that your `{{ }}` braces are balanced and the field path is correct.

```bash
# Wrong
docker inspect -f '{{.NetworkSettings.IPAddress' <container-name>

# Correct
docker inspect -f '{{.NetworkSettings.IPAddress}}' <container-name>
```

### Output Is an Empty `[]`

This happens when no container/image name was provided, or when none of the names you specified matched anything. Double-check your arguments.

### The JSON Output Is Too Long to Read

`docker inspect` output is deeply nested and can be overwhelming to read raw. Use `jq` or `--format` to narrow it down to just the fields you need.

```bash
docker inspect <container-name> | jq '.[0] | {Name, State, NetworkSettings}'
```

---

## FAQ

**Q: What's the difference between `docker inspect` and `docker stats`?**
`docker inspect` shows a static snapshot of configuration data (IP address, environment variables, mounts, etc.). `docker stats` shows live resource usage like CPU and memory — they serve different purposes.

**Q: Can I use `docker inspect` on a stopped container?**
Yes. Configuration data and the last exit code (`State.ExitCode`) are still available for stopped containers, though some network details won't be populated while it's stopped.

**Q: What's the difference between `--format` and `-f`?**
None — `-f` is just the short form of `--format`.

**Q: What can `docker inspect` tell me about an image?**
Layer composition, default environment variables, the `CMD`/`ENTRYPOINT`, exposed ports, and creation timestamp, among other details.

**Q: Does `docker inspect` work on networks and volumes too?**
Yes. You can also run it as a resource-specific subcommand, like `docker network inspect <network-name>` or `docker volume inspect <volume-name>`.

---

## Related Articles

- [docker logs Command Guide](/en/docker-logs)
- [Docker Networking Basics](/en/docker-network-basics)
- [docker ps Command Guide](/en/docker-ps-command)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
