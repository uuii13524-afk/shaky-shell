---
title: 'How to Sync and Backup Files with rsync'
date: '2026-05-25'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'rsync', 'バックアップ', 'SSH']
en_tags: ['Linux', 'rsync', 'backup', 'SSH']
---

## What I Wanted to Do

I needed to back up files from a VPS to my local machine.
`scp` copies everything every time, so I switched to `rsync`, which only transfers the parts that changed.

## Basic Usage

```bash
rsync -av source/ destination/
```

- `-a`: Archive mode — preserves permissions, timestamps, and symlinks
- `-v`: Verbose — shows which files are being transferred

### Local-to-Local Copy

```bash
rsync -av /var/www/html/ /backup/html/
```

Watch the trailing slash: `source/` (with slash) copies the directory's contents; `source` (without slash) copies the directory itself into the destination.

## Syncing with a Remote Server

### Local → Remote

```bash
rsync -av -e ssh /var/www/html/ user@example.com:/var/www/html/
```

### Remote → Local (backup)

```bash
rsync -av -e ssh user@example.com:/var/www/html/ /backup/html/
```

## Useful Options

```bash
# Mirror deletions (remove files in destination that no longer exist in source)
rsync -av --delete /var/www/html/ /backup/html/

# Dry run — preview what would happen without actually copying
rsync -av --dry-run /var/www/html/ /backup/html/

# Compress during transfer (saves bandwidth over SSH)
rsync -avz -e ssh user@example.com:/var/www/ /backup/

# Exclude specific files or directories
rsync -av --exclude='*.log' --exclude='.git' /var/www/html/ /backup/html/

# Show transfer progress
rsync -av --progress /var/www/html/ /backup/html/
```

## Automated Backups with Cron

```bash
crontab -e
```

```
# Run backup every day at 2 AM
0 2 * * * rsync -az -e ssh user@example.com:/var/www/html/ /backup/html/ >> /var/log/rsync.log 2>&1
```

## Common Pitfalls

- The trailing slash on the source path changes behavior — always double-check it before running
- `--delete` is powerful; run with `--dry-run` first to see what would be deleted
- Cron-based rsync over SSH requires key-based authentication — a password prompt will silently hang the job
- rsync skips files that haven't changed, so it's inherently incremental with no extra config needed

## Related Articles

- [Linux File Permissions Explained](/en/linux-file-permissions)
- [Linux User Management](/en/linux-user-management)
- [Managing Linux Services with systemd](/en/linux-systemd-service)
- [Essential Linux Commands](/en/linux-basic-commands)

## Recommended VPS Services

If you're building a production environment on a VPS, these services are worth checking out:

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
