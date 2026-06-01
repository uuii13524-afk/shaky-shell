---
title: 'How to Compress and Extract Files with tar and zip on Linux'
date: '2026-05-26'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'tar', 'zip', 'コマンド', 'ファイル操作']
en_tags: ['Linux', 'tar', 'zip', 'command', 'file operation']
---

## What I wanted to do

I wanted to archive files on a server for backup and compress logs to save disk space.
Both tar and zip come up all the time, but I kept looking up the options every single time.

## Basic tar commands

### Create an archive (no compression)

```bash
tar -cvf archive.tar ./mydir
```

- `-c` : create
- `-v` : verbose output
- `-f` : specify the filename

### Create with gzip compression (.tar.gz)

```bash
tar -czvf archive.tar.gz ./mydir
```

### Create with bzip2 compression (.tar.bz2)

```bash
tar -cjvf archive.tar.bz2 ./mydir
```

## Extracting with tar

```bash
# Extract a .tar file
tar -xvf archive.tar

# Extract a .tar.gz file
tar -xzvf archive.tar.gz

# Extract a .tar.bz2 file
tar -xjvf archive.tar.bz2

# Extract to a specific directory
tar -xzvf archive.tar.gz -C /tmp/
```

## List archive contents without extracting

```bash
tar -tzvf archive.tar.gz
```

## Basic zip commands

```bash
# Compress files
zip archive.zip file1.txt file2.txt

# Compress a directory recursively
zip -r archive.zip ./mydir

# Set compression level (0-9, default is 6)
zip -r -9 archive.zip ./mydir
```

## Extracting with unzip

```bash
# Extract to current directory
unzip archive.zip

# Extract to a specific directory
unzip archive.zip -d /tmp/output

# List contents without extracting
unzip -l archive.zip
```

## Common patterns

### Archive logs with a date stamp

```bash
tar -czvf "logs-$(date +%Y%m%d).tar.gz" /var/log/nginx/
```

### Exclude specific files or directories

```bash
tar -czvf archive.tar.gz ./mydir --exclude='*.log' --exclude='node_modules'
```

### Check compression ratio

```bash
ls -lh archive.tar.gz
du -sh ./mydir
```

## Gotchas

- The `-f` flag in `tar` must come last in the option string — the filename immediately follows `-f`
- Forgetting `-r` in `zip -r` means the directory contents won't be included
- `.tar.gz` and `.tgz` are the same format, so either extension works fine with the same options
- `unzip` may not be installed on a fresh Linux server — install it with `apt install unzip`
- Using absolute paths with `tar` can cause files to extract to unexpected locations; be aware of leading `/` in paths

## Related articles

- [Linux Basic Commands (ls/cd/mkdir/rm)](/en/linux-basic-commands)
- [How to Sync and Backup Files with rsync](/en/linux-rsync)
- [Linux SSH Basics: How to Connect to a VPS](/en/linux-ssh-basics)
- [How to Fix Permission Denied Error on Linux](/en/linux-permission-denied)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
