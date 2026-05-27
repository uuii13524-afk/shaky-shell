---
title: 'Linux Process Management (ps/kill/top)'
date: '2026-05-19'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'プロセス管理', 'ps', 'kill', 'top']
en_tags: ['Linux', 'process management', 'ps', 'kill', 'top']
description: 'How to check and kill Linux processes using ps, kill, top, and pkill. Includes how to identify which process is using a port.'
---
## What I Wanted to Do

A process was hanging and I needed to identify and kill it without rebooting the server.

## Check Running Processes

```bash
ps aux                    # List all processes
ps aux | grep nginx       # Filter by process name
top                       # Real-time monitor (press q to quit)
```

## Kill a Process

```bash
kill PID                  # Request graceful shutdown
kill -9 PID               # Force kill
pkill nginx               # Kill by process name
```

## Find Which Process Is Using a Port

```bash
lsof -i :8080
ss -tlnp | grep 8080
```

## Common Pitfalls

- If `kill` alone doesn't work, use `kill -9` — but treat it as a last resort
- For services like nginx or Docker, using `systemctl stop` is safer than killing the process directly

For managing services via systemd, see [Manage Services with systemd (start/stop/enable/status)](/en/linux-systemd-service).

## Related Posts

- [Linux Basic Commands (ls/cd/mkdir/rm)](/en/linux-basic-commands)
- [Linux File Permissions Explained (chmod/chown)](/en/linux-file-permissions)
- [How to Fix "Permission Denied" on Linux](/en/linux-permission-denied)
- [Install WSL2 on Windows](/en/wsl2-install-windows)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
