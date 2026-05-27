---
title: 'Linux File Permissions Guide (chmod/chown)'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
---

## What I Wanted to Do

Understand and correctly set Linux file permissions.

## What Are Permissions?

Permissions define who can do what with a file or directory.

```
-rwxr-xr-x
```

| Character | Meaning |
|-----------|---------|
| r | Read (4) |
| w | Write (2) |
| x | Execute (1) |
| - | No permission (0) |

## chmod: Change Permissions

### Numeric mode

```bash
chmod 755 filename    # rwxr-xr-x
chmod 644 filename    # rw-r--r--
chmod 600 filename    # rw-------
```

### Common settings

```
755 → Web server directories
644 → Regular files
600 → SSH keys and config files
755 → Executable scripts
```

### Symbolic mode

```bash
chmod +x script.sh    # Add execute permission
chmod -x script.sh    # Remove execute permission
chmod u+w file.txt    # Add write for owner
```

## chown: Change Owner

```bash
chown username filename
chown username:groupname filename
chown -R username directory    # Recursive
```

## Key Points

- SSH keys must be `chmod 600` — SSH refuses connections otherwise
- Never set web server files to 777 — it's a security risk
- Be careful with `chmod -R` — it changes everything recursively

## Related Articles

- [Linux Permission Denied Fix](/en/linux-permission-denied)
- [SSH Key Setup for GitHub](/posts/ssh-key-github)
- [Linux SSH Basics](/posts/linux-ssh-basics)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
