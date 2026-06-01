---
title: 'How to Fix the Docker "Port Already in Use" Error'
date: '2026-05-14'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Fix the Docker port already allocated error. Learn how to find which process is using a port and release it on Windows, Mac, and Linux.'
---

## Symptom

```
Error response from daemon: Bind for 0.0.0.0:8080 failed: port is already allocated
```

## Solutions

### Use a Different Port

```bash
docker run -d -p 8081:80 nginx
```

### Find and Release the Port in Use

**Windows**

```
netstat -ano | findstr :8080
```

Then terminate the relevant process in Task Manager.

**Mac/Linux**

```bash
lsof -i :8080
kill -9 PID
```

### Stop a Running Docker Container

```bash
docker ps
docker stop <container-id>
```

## Key Points

- A previously started container often lingers and occupies the port
- Use `docker ps -a` to see stopped containers as well

For identifying and terminating the process using a port, [How to Check and Kill Linux Processes (ps/kill)](/en/linux-process-management) is also a useful reference.

## Related Articles

- [Docker Basic Commands Cheatsheet](/en/docker-basic-commands)
- [How to Use docker-compose](/en/docker-compose-basic)
- [nginx 502 Bad Gateway: Causes and Fixes](/en/nginx-502-bad-gateway)
- [How to Check and Kill Linux Processes (ps/kill)](/en/linux-process-management)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
