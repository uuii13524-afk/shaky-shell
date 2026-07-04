---
title: 'kill Command Guide: How to Terminate Processes with SIGTERM and SIGKILL'
date: '2026-07-04'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Linux', 'kill', 'process management', 'SIGKILL', 'SIGTERM']
description: 'Learn how to terminate Linux processes with the kill command. Covers the difference between SIGTERM and SIGKILL, when to use pkill or killall, and how to fix "no such process" errors.'
---

## Quick Answer

```bash
# Send a normal termination request (SIGTERM)
kill 1234

# Force-kill the process (SIGKILL)
kill -9 1234

# Kill by process name instead of PID
pkill node
```

---

## What You're Trying to Do

A process is frozen and not responding, or a background command needs to be stopped, or something is still holding onto a port and needs to be shut down. `kill` sends a signal to a process ID — despite the name, it's not always about force-killing. The default behavior is to politely ask the process to exit.

---

## Environment

- OS: Linux (Ubuntu / CentOS / Debian, etc.)
- Useful commands: `kill -l`, `ps aux`, `pgrep`

---

## Solution

### 1. Find the PID of the Process

```bash
ps aux | grep node
```

```
user   1234  0.5  1.2  912345  45678 pts/0   Sl   10:00   0:03 node server.js
```

The number in the second column, `1234`, is the process ID (PID).

### 2. Send SIGTERM (Graceful Shutdown)

```bash
kill 1234
```

When no signal is specified, `kill` sends `SIGTERM (15)` by default. This asks the process to clean up (close files, drop connections) before exiting.

### 3. Send SIGKILL (Force Kill)

If the process doesn't respond to SIGTERM, force it to stop.

```bash
kill -9 1234
# or
kill -SIGKILL 1234
```

`SIGKILL` terminates the process immediately at the OS level — it can't be caught, ignored, or handled by the process, so it gets no chance to clean up. Use it only as a last resort.

### 4. Kill by Process Name (pkill / killall)

Looking up a PID every time gets tedious. You can target processes by name instead.

```bash
# Kill any process whose name partially matches
pkill node

# Kill a process with an exact name match
killall node
```

```bash
# Force-kill also works the same way
pkill -9 node
```

### 5. Kill Only a Specific User's Processes

```bash
pkill -u www-data
```

### 6. List Available Signals

```bash
kill -l
```

```
 1) SIGHUP       2) SIGINT       3) SIGQUIT      9) SIGKILL
15) SIGTERM     ...
```

---

## Common Errors

### `kill: (1234): No such process`

The PID you specified has already exited, or you got the PID wrong. Check again with `ps aux` or `pgrep`.

```bash
pgrep -a node
```

### `Operation not permitted`

You're trying to kill a process you don't own (owned by root or another user). Check your permissions.

```bash
sudo kill -9 1234
```

### A Zombie Process Survives `kill -9`

A zombie process (state `Z`) has already finished executing — it's just waiting for its parent to call `wait()` and reap it. `kill` can't remove it; you need to restart or terminate the parent process instead.

```bash
ps aux | grep 'Z'
```

### Killing Whatever Process Is Holding a Port

```bash
# Find and kill the process using port 3000
lsof -i:3000
kill -9 $(lsof -t -i:3000)
```

---

## FAQ

**Q: Is it okay to always use `kill -9`?**
Better to avoid it when possible. `SIGKILL` gives the process no chance to clean up, which can lead to corrupted files or inconsistent data. Try plain `kill` (SIGTERM) first, and only reach for `-9` if the process doesn't respond.

**Q: What's the difference between `kill` and `pkill`?**
`kill` sends a signal to a specific PID. `pkill` searches for matching processes by name or other criteria and can signal multiple processes at once.

**Q: Should I use `killall` or `pkill`?**
`killall` matches process names exactly, while `pkill` also supports regex-style pattern matching. `pkill` is more flexible if you need finer control over the match.

**Q: Are there other commonly used signals besides SIGTERM and SIGKILL?**
`SIGHUP (1)` is often used to tell a process to reload its configuration, and `SIGINT (2)` is what `Ctrl+C` sends.

**Q: What's the Windows equivalent?**
`taskkill /PID 1234 /F` behaves similarly to `kill -9`.

**Q: Do I need `kill` just to stop a background shell job?**
For jobs running in your current shell, you can check the job number with `jobs` and target it directly, e.g. `kill %1`.

---

## Related Articles

- [Linux Process Management Commands (ps / top / kill)](/en/linux-process-management)
- [docker exec: Enter a Running Container](/en/docker-exec-bash)
- [Fixing "Permission Denied" Errors on Linux](/en/linux-permission-denied)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
