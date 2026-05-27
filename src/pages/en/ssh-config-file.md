---
title: 'How to Use ~/.ssh/config to Simplify SSH Connections'
date: '2026-05-27'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['ssh', 'linux', 'サーバー', '設定ファイル', 'VPS']
en_tags: ['ssh', 'linux', 'server', 'config', 'VPS']
description: 'Learn how to configure ~/.ssh/config with host aliases and IdentityFile settings to manage multiple servers with short SSH commands.'
---
## What I Wanted to Do

Managing multiple VPS and bastion servers meant typing long commands every time — `ssh -i ~/.ssh/id_rsa ubuntu@203.0.113.10`. Setting up `~/.ssh/config` lets you connect with just `ssh myserver`.

## Basic ~/.ssh/config Setup

### Create the File

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/config
chmod 600 ~/.ssh/config
```

The config file must have `600` permissions — SSH ignores it otherwise.

### Define a Host Alias

Add the following to `~/.ssh/config`:

```
Host myserver
    HostName 203.0.113.10
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

Now connect with a short command:

```bash
ssh myserver
```

## Managing Multiple Servers

```
Host web
    HostName 203.0.113.10
    User ubuntu
    IdentityFile ~/.ssh/id_rsa

Host db
    HostName 203.0.113.20
    User ubuntu
    Port 2222
    IdentityFile ~/.ssh/id_db_rsa

Host github
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_github_rsa
```

Now `ssh web` or `ssh db` is all you need.

## Global Settings with Host *

```
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    AddKeysToAgent yes
```

- `ServerAliveInterval` — sends keepalive packets to prevent dropped connections
- `AddKeysToAgent` — automatically adds keys to the SSH agent

## Bastion/Jump Host via ProxyJump

```
Host bastion
    HostName 203.0.113.1
    User ubuntu
    IdentityFile ~/.ssh/id_rsa

Host internal
    HostName 10.0.0.10
    User ubuntu
    IdentityFile ~/.ssh/id_rsa
    ProxyJump bastion
```

```bash
ssh internal
# Connects through bastion automatically
```

## Common Pitfalls

- Config file permissions must be `600` — `644` causes SSH to silently ignore it
- `IdentityFile` paths should start with `~` or be absolute paths
- Host alias names are case-insensitive
- Omitting `Port` defaults to port 22
- Aliases work with `scp` and `rsync` too: `scp myserver:/path/file .`

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
