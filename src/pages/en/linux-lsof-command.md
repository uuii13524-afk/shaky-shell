---
title: 'lsof Command Guide: Finding Which Process Is Using a Port or File'
date: '2026-07-08'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Linux', 'lsof', 'process management']
description: 'Learn how to use lsof to find which process is holding a port or file open, troubleshoot port conflicts and busy files, plus installation and common errors.'
---

## Quick Answer

```bash
# Find the process using a specific port
lsof -i :8080

# Find the process holding a specific file open
lsof /var/log/app.log
```

---

## What You're Trying to Do

You tried to start a server and got `Address already in use`, or tried to delete a file and got `Device or resource busy`, with no way to tell which process is holding the port or file. That's exactly what `lsof` (LiSt Open Files) is for.

---

## Environment

- OS: Ubuntu 22.04 LTS / CentOS Stream 9 / macOS
- lsof: verified on 4.94 and later

---

## Solution

### 1. Check It's Installed

```bash
lsof -v
```

If it isn't installed:

```bash
# Ubuntu / Debian
sudo apt install lsof

# CentOS / RHEL
sudo dnf install lsof
```

### 2. Find the Process Using a Port

```bash
lsof -i :8080
```

```
COMMAND   PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
node     3142   user   22u  IPv4  85432      0t0  TCP *:8080 (LISTEN)
```

Once you have the PID, terminate it:

```bash
kill -9 3142
```

### 3. Find the Process Holding a File Open

```bash
lsof /var/log/app.log
```

Useful when a process still holds a stale file handle after log rotation.

### 4. List All Files Opened by a Process

```bash
lsof -p 3142
```

Given a PID, this lists every file and socket that process currently has open.

### 5. Find What's Open Under a Directory

```bash
lsof +D /var/www/html
```

Handy when a disk or mount won't unmount and you need to know why.

### 6. Find Files Opened by a Specific User

```bash
lsof -u www-data
```

### 7. Filter by TCP/UDP Connection State

```bash
# LISTEN state only
lsof -i -sTCP:LISTEN

# Connections to a specific host only
lsof -i @192.168.1.10
```

---

## Common Errors

### `lsof: command not found`

Some distributions don't include it by default. Install it via your package manager:

```bash
sudo apt install lsof
```

### `lsof: WARNING: can't stat() ... file system`

This warning usually appears with NFS mounts or other filesystems when permissions are insufficient. It rarely affects the actual output, but running with `sudo lsof` often clears it.

### No Output at All

A regular user can't see another user's process information. Run it with `sudo`:

```bash
sudo lsof -i :8080
```

### `lsof` Runs Extremely Slowly

With many network mounts (like NFS), `lsof` scans every mount and can be slow. Narrow the scope with options like `-i` and `-c`:

```bash
lsof -i :8080 -a -c node
```

---

## FAQ

**Q: What's the difference between `lsof` and `netstat`?**
`netstat` focuses on network connections. `lsof` is more general — it covers not just network sockets but also regular files, directories, and devices, anything currently "open."

**Q: When should I use `ss` instead?**
If you only need to check port usage, `ss -tulpn` is faster. Use `lsof` when you also need to map open files back to specific processes.

**Q: Why does output disappear without elevated permissions?**
Viewing information about processes you don't own requires root privileges. Use `sudo lsof`.

**Q: How do I find out why a file won't delete?**
Run `lsof <file-path>`, then either terminate the PID it lists or wait for that process to exit normally before deleting.

**Q: Does this work the same way on macOS?**
Yes. macOS ships with `lsof` built in, and the options are nearly identical.

---

## Related Articles

- [Fixing "Port Already in Use" Errors in Docker](/en/docker-port-already-in-use)
- [Checking and Killing Processes on Linux (ps/kill)](/en/linux-process-management)
- [linux kill Command Guide](/en/linux-kill-command)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
