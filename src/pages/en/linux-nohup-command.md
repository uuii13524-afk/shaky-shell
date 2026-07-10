---
title: 'nohup Command Guide: Keep Processes Running After SSH Disconnects'
date: '2026-07-10'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Linux', 'nohup', 'SSH', 'background process']
description: 'Learn how to use nohup to keep a process running after your SSH session ends, including output redirection, combining it with & and disown, and common errors.'
---

## Quick Answer

```bash
# Run a command with nohup and send it to the background
nohup ./long-running-script.sh &

# Redirect output explicitly
nohup ./long-running-script.sh > output.log 2>&1 &
```

---

## What You're Trying to Do

You connected to a VPS over SSH, kicked off a long-running task, and it died the moment the connection dropped — this is exactly the problem `nohup` was built to solve.

When an SSH session ends, any process started in it normally receives a `SIGHUP` (hang up) signal and terminates along with it. `nohup` — short for "no hang up" — launches a command in a way that ignores `SIGHUP`, so the process keeps running even after you log out.

---

## Environment

- OS: Linux (verified on Ubuntu, CentOS, Debian, and other major distributions)
- Shell: bash / zsh

---

## Solution

### 1. Basic Syntax

```bash
nohup <command>
```

This alone ignores `SIGHUP`, but the command still runs in the foreground and blocks your terminal, so you'll usually add `&` to send it to the background too.

```bash
nohup ./long-running-script.sh &
```

### 2. Redirecting Output

If you run `nohup` without `&`, stdout and stderr are automatically written to `nohup.out` in the current directory.

```bash
nohup ./long-running-script.sh &
cat nohup.out
```

To control where output goes, use explicit redirection.

```bash
# Combine stdout and stderr into one file
nohup ./long-running-script.sh > output.log 2>&1 &

# Split stdout and stderr
nohup ./long-running-script.sh > stdout.log 2> stderr.log &

# Discard all output
nohup ./long-running-script.sh > /dev/null 2>&1 &
```

### 3. Checking the Process ID

When run in the background, the process ID is printed immediately.

```bash
nohup ./long-running-script.sh &
[1] 12345
```

To check later, use `jobs -l` or `ps`.

```bash
jobs -l
ps aux | grep long-running-script
```

### 4. Killing the Process

```bash
kill 12345
```

Force-kill with `-9` if needed.

```bash
kill -9 12345
```

### 5. Combining with disown

`nohup` ignores `SIGHUP`, but depending on your shell configuration, the job may still be tracked by the shell itself. To fully detach it from the shell, combine it with `disown`.

```bash
nohup ./long-running-script.sh &
disown
```

Now the process stays alive even if the shell that launched it exits, since it's no longer in the shell's job table.

### 6. Applying nohup to an Already-Running Process

You can't retroactively attach `nohup` to a process that's already running. In that case, use `disown` alone, or consider switching to a terminal multiplexer like `screen` or `tmux`.

```bash
# Detach a running job from the shell (not a full substitute for nohup)
disown -h %1
```

---

## Common Errors

### `nohup: ignoring input and appending output to 'nohup.out'`

This isn't an error — it's the normal message shown when you don't redirect output explicitly. It just means stdin is ignored and output is being appended to `nohup.out`.

### `nohup: failed to run command: No such file or directory`

Usually means the script or command wasn't found, or it isn't executable. Check the path and permissions.

```bash
ls -l ./long-running-script.sh
chmod +x ./long-running-script.sh
```

### `nohup.out` Keeps Growing

If a process produces a lot of output without redirection, `nohup.out` can grow indefinitely. Redirect to `/dev/null` if you don't need it, or set up log rotation with something like `logrotate`.

### The Process Still Dies After SSH Disconnects

If you forgot the trailing `&`, the command stays in the foreground and still terminates when you close the SSH connection, `nohup` or not. Double-check that you actually backgrounded it.

---

## FAQ

**Q: What's the difference between `nohup` and `screen` / `tmux`?**
`nohup` simply makes one command ignore `SIGHUP`. `screen` and `tmux` persist an entire session, letting you reattach and interact with it later. Use `screen` / `tmux` for long interactive work, and `nohup` for one-off batch jobs.

**Q: Is `nohup command &` the same as `command & disown`?**
Similar, but not identical. `nohup` makes the process ignore the `SIGHUP` signal itself, while `disown` removes it from the shell's job table. For maximum safety, combine both.

**Q: How do I check whether a process started with `nohup` has finished?**
Run `ps aux | grep <process-name>` to see if it's still running, or check the log file. If you need the exit code, have the script write it to the log itself on completion.

**Q: Can I use `nohup` instead of a systemd service?**
It's fine for temporary or ad hoc tasks. But if you need auto-start on boot, automatic restarts, and proper log management in production, defining a `systemd` service is the more reliable approach.

**Q: Why does my process still die even though I used `nohup`?**
Common causes include forgetting the `&`, the whole process group being killed together, or the server itself being rebooted. Check the process tree with `ps -ef --forest` to investigate.

---

## Related Articles

- [How to Keep SSH Sessions Alive with the screen Command on Linux](/en/linux-screen-command)
- [Managing systemd Services (start/stop/enable/status)](/en/linux-systemd-service)
- [Checking and Killing Processes on Linux (ps/kill)](/en/linux-process-management)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
