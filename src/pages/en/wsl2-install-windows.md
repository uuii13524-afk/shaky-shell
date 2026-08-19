---
title: 'How to Install WSL2 on Windows'
date: '2026-05-11'
category: 'Windows'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Install WSL2 on Windows with wsl --install, set up your Ubuntu username and password, and access Windows files from Linux via /mnt/c/Users/username/.'
---

## Steps

### 1. Install WSL2

```
wsl --install
```

Restart Windows when done.

### 2. Initial Setup

After restarting, Ubuntu launches. Set a username and password.

### 3. Verify

```
wsl
```

## Useful Commands

```
wsl --shutdown
wsl --update
wsl --list --verbose
```

## Access Files Between Windows and Linux

From WSL2:

```bash
cd /mnt/c/Users/username/
```

## Related Articles

- [How to Install Docker on Windows](/en/docker-install-windows)
- [Linux Basic Commands](/en/linux-basic-commands)
- [Linux Permission Denied Fix](/en/linux-permission-denied)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
