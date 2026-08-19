---
title: 'Linux UFW Firewall Setup Basics'
date: '2026-05-22'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Shows how to configure UFW on a VPS with sudo ufw allow ssh before sudo ufw enable, so you do not lock yourself out, plus port rules and ufw reset.'
ja_tags: ['Linux', 'UFW', 'ファイアウォール', 'セキュリティ', 'VPS']
en_tags: ['Linux', 'UFW', 'Firewall', 'Security', 'VPS']
---

## What I wanted to do

After spinning up a VPS, I wanted to close unnecessary ports and harden security.
UFW (Uncomplicated Firewall) turned out to have very intuitive commands.

## Installing and enabling UFW

```bash
# Ubuntu usually has it pre-installed
sudo apt install ufw

# Check status
sudo ufw status
```

Always allow SSH before enabling UFW. Skip this and you'll lose access to your VPS.

```bash
sudo ufw allow ssh      # Allow port 22
sudo ufw enable         # Enable UFW
```

## Allowing and denying ports

```bash
# Specify by port number
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8080

# Specify by service name
sudo ufw allow http
sudo ufw allow https

# Allow only from a specific IP address
sudo ufw allow from 192.168.1.100 to any port 22
```

## Checking and deleting rules

```bash
# List rules with numbers
sudo ufw status numbered

# Delete by number
sudo ufw delete 3

# Delete by specifying the rule directly
sudo ufw delete allow 8080
```

## Resetting UFW

When you want to start over.

```bash
sudo ufw reset
```

After a reset, you need to re-configure starting from SSH allow rules.

## Setting up common ports together

```bash
# Web server
sudo ufw allow 80
sudo ufw allow 443

# SSH (if you changed the default port)
sudo ufw allow 2222

# nginx + Node.js setup (keep 3000 local only)
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 3000
```

## Checking the current configuration

```bash
sudo ufw status verbose
```

```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
```

## Gotchas

- Always run `ufw allow ssh` before `ufw enable` — forget this and you'll lock yourself out
- Port number and service name are equivalent (`allow 22` and `allow ssh` do the same thing)
- `ufw reset` wipes SSH rules too, so be careful
- When using Docker, UFW rules can be bypassed by Docker (you may need to configure the `DOCKER-USER` chain)
- The default policy is to deny all incoming traffic, so explicitly allow only the ports you need

## Related Articles

- [Linux SSH Basics](/posts/linux-ssh-basics)
- [Linux Basic Commands](/posts/linux-basic-commands)
- [Setting Up Docker on a VPS](/posts/vps-docker-setup)
- [nginx Basic Configuration](/posts/nginx-basic-config)
- [Linux File Permissions Basics](/posts/linux-file-permissions)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
