---
title: 'Set Up Docker on a VPS (Ubuntu)'
date: '2026-05-21'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Docker', 'VPS', 'Linux', 'Ubuntu', 'docker-compose']
en_tags: ['Docker', 'VPS', 'Linux', 'Ubuntu', 'docker-compose']
description: 'Step-by-step guide to installing Docker and Docker Compose on a VPS running Ubuntu 22.04, including user permissions and firewall setup.'
---
## What I Wanted to Do

I had a VPS (Ubuntu 22.04) and wanted to run my app in Docker on it — the same way I develop locally.

## Environment

- Ubuntu 22.04 LTS (VPS)
- Docker + Docker Compose

## Steps

### 1. Connect to the VPS via SSH

```bash
ssh root@YOUR_VPS_IP
```

### 2. Update the System

```bash
apt update && apt upgrade -y
```

### 3. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
```

### 4. Verify the Installation

```bash
docker --version
docker run hello-world
```

### 5. Install Docker Compose

```bash
apt install docker-compose-plugin -y
docker compose version
```

### 6. Allow a Non-root User to Run Docker

```bash
usermod -aG docker YOUR_USERNAME
```

Log out and back in for the change to take effect.

## Security Settings

### Disable Root SSH Login

```bash
nano /etc/ssh/sshd_config
# Change: PermitRootLogin no
systemctl restart sshd
```

### Set Up the Firewall

```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

## Common Pitfalls

- `curl | sh` installs the latest stable Docker version automatically
- Running Docker as root is a security risk — always create a non-root user
- UFW and Docker can conflict; Docker may bypass UFW rules on some setups

For creating a non-root user, see [Manage Linux Users (useradd/userdel)](/en/linux-user-management).

## Related Posts

- [Install Docker on Windows](/en/docker-install-windows)
- [Docker Compose Basics](/en/docker-compose-basic)
- [Docker Basic Commands (run/stop/rm/ps)](/en/docker-basic-commands)
- [How to Fix "Permission Denied" on Linux](/en/linux-permission-denied)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
