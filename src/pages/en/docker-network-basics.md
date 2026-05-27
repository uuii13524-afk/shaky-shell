---
title: 'Docker Network Basics: bridge, host, and none'
date: '2026-05-21'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Understand Docker bridge, host, and none networks. Covers custom networks and docker-compose network configuration with practical examples.'
---

## What I Wanted to Do

Understand how to configure networking between Docker containers. Network settings become critical when running multiple containers with docker-compose.

## Network Types

### bridge (Default)

```bash
docker run -d --network bridge nginx
```

- The default network mode
- Containers can communicate with each other via IP address
- Runs in a separate network space from the host

### host

```bash
docker run -d --network host nginx
```

- Uses the host machine's network directly
- No port mapping needed
- Linux only (behavior differs on Mac and Windows)

### none

```bash
docker run -d --network none nginx
```

- No network at all
- Completely isolated from external communication

## Creating a Custom Network

```bash
docker network create mynetwork
docker run -d --network mynetwork --name app1 nginx
docker run -d --network mynetwork --name app2 nginx
```

Containers on the same network can communicate using container names.

```bash
# Connect from app1 to app2
curl http://app2
```

## Network Configuration in docker-compose

```yaml
services:
  web:
    image: nginx
    networks:
      - frontend
  db:
    image: mysql:8
    networks:
      - backend
  app:
    image: myapp
    networks:
      - frontend
      - backend

networks:
  frontend:
  backend:
```

## Commonly Used Commands

```bash
docker network ls                    # List networks
docker network inspect mynetwork     # Inspect network details
docker network create mynetwork      # Create a network
docker network rm mynetwork          # Remove a network
docker network connect mynetwork <container>  # Add container to network
```

## Key Points

- docker-compose automatically creates a custom network
- Containers must be on the same network to communicate by name
- nginx 502 errors are often caused by incorrect network configuration

If you encounter nginx 502 errors, check [nginx 502 Bad Gateway: Causes and Fixes](/en/nginx-502-bad-gateway) for hostname configuration issues.

## Related Articles

- [How to Use docker-compose](/en/docker-compose-basic)
- [Docker Basic Commands Cheatsheet](/en/docker-basic-commands)
- [nginx 502 Bad Gateway: Causes and Fixes](/en/nginx-502-bad-gateway)
- [How to Persist Data with Docker Volumes](/en/docker-volume-basics)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
