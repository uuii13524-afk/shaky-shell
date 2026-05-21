---
title: 'How to Install WSL2 on Windows'
date: '2026-05-11'
category: 'Windows'
layout: '../../layouts/PostLayoutEn.astro'
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
