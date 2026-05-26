---
title: 'How to Install Docker on Windows and Get It Running'
date: '2026-05-10'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
---

## Environment

- Windows 10 / 11 (64-bit)

## Steps

### 1. Install WSL2

```
wsl --install
```

Restart Windows when done.

### 2. Download Docker Desktop

Go to https://www.docker.com/products/docker-desktop and click "Download for Windows".

### 3. Install

Make sure "Use WSL 2 instead of Hyper-V" is checked. Restart after installation.

### 4. Verify

```
docker --version
docker run hello-world
```

## Common Issues

### Virtualization not enabled in BIOS

Enable Intel VT-x or AMD-V in your BIOS settings.

### WSL2 not installed

```
wsl --install
wsl --update
```

## Basic Commands

```
docker ps           # List running containers
docker ps -a        # List all containers
docker stop ID      # Stop a container
docker rm ID        # Remove a container
```

## Related Articles

- [Docker Basic Commands Cheatsheet](/en/docker-basic-commands)
- [How to Use docker-compose](/en/docker-compose-basic)
- [How to Install WSL2 on Windows](/en/wsl2-install-windows)


## Recommended VPS / Cloud Hosting

If you're looking for high-performance cloud infrastructure, Cherry Servers offers developer-friendly VPS and dedicated servers optimized for AI, Web3, and production workloads.

<a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a>