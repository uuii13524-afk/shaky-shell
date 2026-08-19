---
title: 'Linux Permission Denied Error: Causes and Fixes'
date: '2026-05-14'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Fixes "bash: ./script.sh: Permission denied" on Linux by running chmod +x, using sudo for root-only commands, or fixing ownership with chown.'
---

## Symptoms

```
Permission denied
bash: ./script.sh: Permission denied
```

## Cause 1: Missing Execute Permission

```bash
chmod +x script.sh
./script.sh
```

## Cause 2: Requires Root Privileges

```bash
sudo your-command
```

## Cause 3: Wrong File Owner

```bash
sudo chown username:groupname filename
```

## chmod Quick Reference

```bash
chmod 755 file    # Owner: rwx, Others: r-x
chmod 644 file    # Owner: rw-, Others: r--
chmod +x file     # Add execute permission
```

## Related Articles

- [Linux Basic Commands](/en/linux-basic-commands)
- [How to Install WSL2 on Windows](/en/wsl2-install-windows)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
