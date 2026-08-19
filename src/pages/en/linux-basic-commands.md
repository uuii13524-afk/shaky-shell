---
title: 'Linux Basic Commands Cheatsheet (ls/cd/mkdir/rm)'
date: '2026-05-10'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
description: 'A cheatsheet for core Linux commands like ls, cd, mkdir, rm -rf, cp, and mv, including why rm -rf folder/ is irreversible and must be used carefully.'
---

## View Files

```bash
ls -la
pwd
```

## Navigate

```bash
cd /home/user
cd ..
cd ~
```

## Create

```bash
mkdir newfolder
touch newfile.txt
```

## Delete

```bash
rm file.txt
rm -rf folder/    # Force delete — irreversible!
```

## Copy and Move

```bash
cp file.txt backup.txt
mv file.txt /tmp/
mv old.txt new.txt
```

## View File Contents

```bash
cat file.txt
tail -f logfile.log
```

## Key Points

- `rm -rf` is irreversible
- Linux filenames are case-sensitive
- Use `Tab` for auto-completion

## Related Articles

- [Linux Permission Denied Fix](/en/linux-permission-denied)
- [How to Install Docker on Windows](/en/docker-install-windows)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
