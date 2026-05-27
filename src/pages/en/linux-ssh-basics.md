---
title: 'SSH Basics on Linux (How to Connect to a VPS)'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'SSH', 'VPS', 'サーバー接続']
en_tags: ['Linux', 'SSH', 'VPS', 'remote server']
description: 'Learn the basics of SSH connections on Linux: connecting to a VPS, specifying ports, using key authentication, and configuring ~/.ssh/config.'
---
## What I Wanted to Do

I needed to connect to a VPS via SSH and wanted to understand the key options and security settings.

## Basic SSH Connection

```bash
ssh username@IP_address
ssh root@192.168.1.1
ssh root@example.com
```

## Specify a Port

```bash
ssh -p 2222 root@example.com
```

## Connect with an SSH Key

```bash
ssh -i ~/.ssh/id_ed25519 root@example.com
```

## Simplify with ~/.ssh/config

Typing options every time is tedious. Add a host block to `~/.ssh/config`:

```
Host myserver
  HostName 192.168.1.1
  User root
  Port 22
  IdentityFile ~/.ssh/id_ed25519
```

After this, just run:

```bash
ssh myserver
```

## Useful SSH Options

```bash
ssh -v root@example.com                        # Verbose output for debugging
ssh -L 8080:localhost:80 root@example.com      # Port forwarding
scp file.txt root@example.com:/tmp/            # Copy a file to remote
```

## Security Settings

### Disable Root Login

```bash
nano /etc/ssh/sshd_config
# Change: PermitRootLogin no
systemctl restart sshd
```

### Disable Password Authentication

```bash
# /etc/ssh/sshd_config
PasswordAuthentication no
```

## Common Pitfalls

- If connection fails, check that port 22 is open in the firewall
- SSH key permissions must be `600` — SSH ignores the key otherwise (`chmod 600 ~/.ssh/id_ed25519`)
- VPS hosts display a fingerprint prompt on the first connection — this is normal

For firewall setup, see [Linux UFW Firewall Basics](/en/linux-firewall-ufw).

## Related Posts

- [Linux File Permissions Explained (chmod/chown)](/en/linux-file-permissions)
- [How to Fix "Permission Denied" on Linux](/en/linux-permission-denied)
- [Linux Basic Commands (ls/cd/mkdir/rm)](/en/linux-basic-commands)
- [Set Up Docker on a VPS](/en/vps-docker-setup)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
