---
title: 'Monitor Linux Logs in Real Time with tail -f'
date: '2026-05-17'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'tail', 'ログ監視', 'コマンド']
en_tags: ['Linux', 'tail', 'log monitoring', 'command']
description: 'How to use tail -f to monitor Linux log files in real time. Covers filtering with grep, monitoring Docker logs, and common log file paths.'
---
## Basic Usage

```bash
tail -f /var/log/nginx/error.log   # Monitor error log
tail -n 100 -f logfile             # Start from last 100 lines
```

Press `Ctrl + C` to stop.

## Filter for Errors Only with grep

```bash
tail -f /var/log/nginx/error.log | grep "error"
```

## Monitor Docker Container Logs

```bash
docker logs -f CONTAINER_ID
docker logs -f --tail 100 CONTAINER_ID
```

## Common Log File Locations

```
/var/log/nginx/error.log     # nginx error log
/var/log/syslog              # System log
/var/log/auth.log            # Authentication log
```

To filter log output with more advanced patterns, combine `tail -f` with [How to Search Files with grep and find on Linux](/en/linux-grep-find).

## Related Posts

- [Linux Basic Commands (ls/cd/mkdir/rm)](/en/linux-basic-commands)
- [How to Search Files with grep and find on Linux](/en/linux-grep-find)
- [nginx Basic Configuration File Guide](/en/nginx-basic-config)
- [Docker Basic Commands (run/stop/rm/ps)](/en/docker-basic-commands)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
