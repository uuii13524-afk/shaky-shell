---
title: 'How to Add and Remove Users on Linux (useradd/userdel)'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Create a non-root Linux user with useradd -m, set a password, add them to the sudo group with usermod -aG sudo, and remove users safely with userdel -r.'
---

## What I Wanted to Do

Add a non-root user to a VPS. Working as root is a security risk, so creating a regular user is best practice.

## Add a User

```bash
useradd -m username       # Create user with home directory
passwd username           # Set password
```

## Add User to sudo Group

```bash
usermod -aG sudo username
```

## Check Users

```bash
cat /etc/passwd           # List all users
id username               # Check user ID
groups username           # Check group membership
```

## Delete a User

```bash
userdel username          # Delete user
userdel -r username       # Delete user and home directory
```

## Key Points

- Without `-m`, no home directory is created
- User must be in the `sudo` group to use sudo
- Always create a sudo user before disabling root login

## Related Articles

- [Linux SSH Basics](/posts/linux-ssh-basics)
- [How to Install Docker on a VPS](/posts/vps-docker-setup)
- [Linux Permission Denied Fix](/en/linux-permission-denied)
- [Linux Basic Commands](/en/linux-basic-commands)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
