---
title: 'Linux Basic Commands Cheatsheet (ls/cd/mkdir/rm)'
date: '2026-05-10'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
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
