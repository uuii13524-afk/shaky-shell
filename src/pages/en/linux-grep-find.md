---
title: 'How to Search Files with grep and find on Linux'
date: '2026-05-16'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'grep', 'find', 'コマンド']
en_tags: ['Linux', 'grep', 'find', 'command']
description: 'How to use grep to search file contents and find to locate files on Linux. Covers useful flags and combining the two commands with pipes.'
---
## grep: Search Inside Files

```bash
grep "error" app.log              # Lines containing "error"
grep -r "keyword" src/            # Recursive search in a directory
grep -i "error" app.log           # Case-insensitive
grep -n "error" app.log           # Show line numbers
grep -A 3 -B 3 "error" app.log    # Show 3 lines of context
```

## find: Locate Files

```bash
find . -name "*.log"                # Search by extension
find . -type d -name "node_modules" # Find directories
find . -mtime -1                    # Modified within 1 day
```

## Combine find and grep

```bash
find . -name "*.js" | xargs grep "console.log"
```

## Common Pitfalls

- `grep -r` also searches `node_modules` — narrow the path to avoid slow results
- `find /` starts from the root filesystem and can be very slow

To monitor a log file in real time and filter with grep, combine with [Monitor Linux Logs in Real Time with tail -f](/en/linux-tail-log).

## Related Posts

- [Linux Basic Commands (ls/cd/mkdir/rm)](/en/linux-basic-commands)
- [Monitor Linux Logs in Real Time with tail -f](/en/linux-tail-log)
- [How to Fix "Permission Denied" on Linux](/en/linux-permission-denied)
- [Install WSL2 on Windows](/en/wsl2-install-windows)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
