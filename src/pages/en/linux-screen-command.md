---
title: 'How to Keep SSH Sessions Alive with the screen Command on Linux'
date: '2026-06-01'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'screen', 'SSH', 'VPS', 'サーバー管理']
en_tags: ['Linux', 'screen', 'SSH', 'VPS', 'server management']
description: 'Learn how to use the Linux screen command to keep processes running after SSH disconnects. Covers session management, key bindings, and common pitfalls.'
---
## What I Wanted to Do

I wanted to run a long process on my VPS and close the terminal without killing it.
Since closing the SSH connection kills the process, I used `screen` to persist the session.

## Installing screen

```bash
# Ubuntu/Debian
sudo apt install screen

# CentOS/RHEL
sudo yum install screen
```

Check if it's already installed with `screen --version`.

## Basic Usage

### Start a New Session

```bash
screen
```

A new session starts immediately. Naming it makes things easier to manage later.

```bash
screen -S mysession
```

### Detach a Session (Send It to the Background)

Press `Ctrl + A` then `D`.

```
[detached from 12345.mysession]
```

This message means detach was successful. Even after closing the SSH connection, any process running inside the session will continue.

### Reattach to an Existing Session

```bash
# List sessions
screen -ls
```

```
There is a screen on:
        12345.mysession (Detached)
1 Socket in /run/screen/S-user.
```

```bash
# Reattach by session name
screen -r mysession

# Or by ID
screen -r 12345
```

### End a Session

Run `exit` inside the session, or press `Ctrl + D`.

## Common Key Bindings

| Action | Keys |
|--------|------|
| Detach | `Ctrl + A` → `D` |
| Create new window | `Ctrl + A` → `C` |
| List windows | `Ctrl + A` → `"` |
| Next window | `Ctrl + A` → `N` |
| Previous window | `Ctrl + A` → `P` |
| Force kill session | `Ctrl + A` → `K` |

## Managing Multiple Sessions

```bash
# List all sessions
screen -ls

# Force quit a specific session (when you can't attach to it)
screen -S mysession -X quit
```

If you get an error reattaching to a detached session, use `-d -r`:

```bash
# Detach any other client and reattach
screen -d -r mysession
```

## Pitfalls

- If `screen -r` says the session isn't found, try using the ID instead of the name
- After reconnecting via SSH you may find the session listed as `(Attached)` — use `screen -d -r` in that case
- On shared VPS environments, `screen -ls` only shows your own sessions
- Nesting screen inside screen causes key binding conflicts — avoid it
- For long-term use, `tmux` offers more features and is worth considering

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
