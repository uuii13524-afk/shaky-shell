---
title: 'How to Check Disk Usage on Linux (df and du)'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Learn how to check disk usage on Linux with df and du commands. Covers checking server free space and identifying large files clearly.'
---

## What I Wanted to Do

I wanted to check disk usage on a Linux server.
Using df and du, you can check the disk free space and folder sizes.

## df: Check Overall Disk Usage

```bash
df -h                    # Display in human-readable format
df -h /                  # Show root only
df -h /var               # Specify a particular path
```

### Example output

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   20G   28G  42% /
```

## du: Check Folder Size

```bash
du -sh foldername        # Total size of a folder
du -sh /*                # Each folder directly under root
du -sh /var/log/*        # Contents of the log folder
du -h --max-depth=1 /var # Show only one level deep
```

## Handling a Full Disk

### Find large files

```bash
find / -size +100M -type f 2>/dev/null
```

### Delete log files

```bash
sudo journalctl --vacuum-size=100M    # Trim systemd logs to 100MB or less
sudo find /var/log -name "*.log" -mtime +30 -delete  # Delete logs older than 30 days
```

### Remove unused Docker data

```bash
docker system prune -a
```

## Common Pitfalls

- `df` checks the whole filesystem; `du` checks a specific folder's size
- The `-h` option displays sizes in human-readable format (GB/MB)
- When using Docker, `/var/lib/docker` tends to grow large

If your VPS is running low on RAM, you can ease memory pressure by adding swap space using [How to Set Up Swap on Linux](/en/linux-swap-setup).

## Related Articles

- [Essential Linux Commands (ls/cd/mkdir/rm) Cheat Sheet](/en/linux-basic-commands)
- [How to Monitor Logs in Real Time with tail -f on Linux](/en/linux-tail-log)
- [Docker Basic Commands Cheat Sheet](/en/docker-basic-commands)
- [How to Set Up Docker on a VPS for Production](/en/vps-docker-setup)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
