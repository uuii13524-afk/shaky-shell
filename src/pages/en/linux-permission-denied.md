---
title: 'Linux Permission Denied Error: Causes and Fixes'
date: '2026-05-14'
category: 'Linux'
---

## Symptoms

```
Permission denied
bash: ./script.sh: Permission denied
mkdir: cannot create directory: Permission denied
```

## Cause 1: Missing Execute Permission

The file doesn't have the execute bit set.

### Check

```bash
ls -la script.sh
# -rw-r--r-- means no execute permission
```

### Fix

```bash
chmod +x script.sh
./script.sh
```

## Cause 2: Requires Root Privileges

System files and directories like `/etc/` require elevated permissions.

### Fix

```bash
sudo your-command
sudo mkdir /var/myapp
```

## Cause 3: Wrong File Owner

```bash
ls -la filename    # Check who owns the file
sudo chown username:groupname filename
```

## chmod Quick Reference

```bash
chmod 755 file    # Owner: rwx, Others: r-x
chmod 644 file    # Owner: rw-, Others: r--
chmod +x file     # Add execute permission
chmod -x file     # Remove execute permission
```

## Key Points

- Files in WSL2 coming from Windows can cause permission issues
- Avoid overusing `sudo` for security reasons
- Permission issues are common inside Docker containers

## Related Articles

- [Linux Basic Commands (ls/cd/mkdir/rm)](/posts/linux-basic-commands)
- [How to Install WSL2 on Windows](/posts/wsl2-install-windows)
- [How to Search Files with grep and find](/posts/linux-grep-find)
