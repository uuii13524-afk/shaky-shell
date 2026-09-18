---
title: 'Fix: Cannot Connect to the Docker Daemon After a Server Reboot'
date: '2026-09-18'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
description: 'After rebooting a VPS, docker ps fails with Cannot connect to the Docker daemon. Here is how to confirm docker.service is inactive and fix it permanently with systemctl enable --now.'
en_tags: ['Docker', 'systemd', 'Cannot connect to the Docker daemon']
---

## What I Was Trying to Do

I installed Docker with `apt` on a fresh Ubuntu 24.04 VPS and started a few containers to verify everything worked. `docker ps` and `docker run` both worked fine at that point.

A few days later I ran `sudo reboot` to apply a kernel update. After SSHing back in, `docker ps` failed immediately.

```bash
docker ps
```

```text
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

Every container management command that had worked before the reboot was now broken, so my first instinct was that the Docker installation itself had gotten corrupted, and I considered reinstalling it.

## Environment

- OS: Ubuntu 24.04.1 LTS (Sakura VPS)
- Docker Engine: 27.1.1
- Docker Compose: v2.29.1
- Install method: `sudo apt install docker.io`
- Login user: `deploy` (has `sudo`, already in the `docker` group)

## What I Tried

My first guess was a permissions problem, since it reminded me of a `docker.sock` permission error I'd seen before. But the message this time wasn't `permission denied` — it was a connection failure — so running it with `sudo` didn't change anything.

```bash
sudo docker ps
```

```text
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

Since `sudo` made no difference, I concluded this probably wasn't a permissions issue at all, but that the Docker daemon itself wasn't running. Next I checked whether the socket file even existed.

```bash
ls -la /var/run/docker.sock
```

```text
ls: cannot access '/var/run/docker.sock': No such file or directory
```

The socket file didn't exist at all, which meant the daemon had either never started or had failed to start. That's when I stopped thinking about reinstalling and switched to checking the service's status instead.

## Root Cause

I checked docker.service with `systemctl status`.

```bash
sudo systemctl status docker
```

```text
○ docker.service - Docker Application Container Engine
     Loaded: loaded (/usr/lib/systemd/system/docker.service; disabled; preset: enabled)
     Active: inactive (dead)
```

It showed `disabled`, and `Active: inactive (dead)`. Right after `apt install docker.io`, the package's postinstall script starts docker.service immediately, which is why `docker` commands worked fine right after installation. But that immediate start is separate from enabling the service to start automatically at boot (`systemctl enable`). Because that step hadn't happened, docker.service never came back up after `reboot`, and without the service running, `docker.sock` was never created either.

In other words, the problem wasn't that Docker was broken — it was that the Docker service had never been configured to start automatically on boot. The fact that `docker` commands work right after `apt install` and the fact that docker.service is enabled at boot are two separate things, and missing that distinction would have led me to waste time reinstalling Docker for no reason.

## How I Fixed It

### 1. Check docker.service's current state

```bash
sudo systemctl status docker
```

```text
○ docker.service - Docker Application Container Engine
     Loaded: loaded (/usr/lib/systemd/system/docker.service; disabled; preset: enabled)
     Active: inactive (dead)
```

Confirmed both `disabled` and `inactive (dead)` — the service was neither auto-starting nor currently running.

### 2. Start docker.service and enable it for future boots

```bash
sudo systemctl enable --now docker
```

```text
Synchronizing state of docker.service with SxS service manager...
Created symlink /etc/systemd/system/multi-user.target.wants/docker.service → /usr/lib/systemd/system/docker.service.
```

`enable --now` starts the service immediately and sets it to start automatically on every future boot, in a single command. Running only `start` would fix the immediate problem but leave the same failure waiting after the next reboot.

### 3. Recheck the service status

```bash
sudo systemctl status docker
```

```text
● docker.service - Docker Application Container Engine
     Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; preset: enabled)
     Active: active (running) since Fri 2026-09-18 10:12:03 UTC; 5s ago
```

Confirmed it was now `enabled` and `active (running)`.

### 4. Confirm the socket file exists

```bash
ls -la /var/run/docker.sock
```

```text
srw-rw---- 1 root docker 0 Sep 18 10:12 /var/run/docker.sock
```

The socket file that didn't exist before was now present.

## Verify It Works

`docker ps` now ran with no permission or connection error.

```bash
docker ps
```

```text
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

To be extra sure, I rebooted the server again and confirmed the problem didn't come back.

```bash
sudo reboot
```

```bash
# after logging back in
docker ps
```

```text
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

`docker ps` responded without error after the second reboot as well.

## Takeaways

- `Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?` is not a permission error (`permission denied`) — it means the daemon itself isn't running, or the socket doesn't exist. If adding `sudo` changes nothing, suspect this instead.
- The fact that `docker` commands work right after `apt install docker.io` only means the postinstall script started the service once — it says nothing about whether the service is enabled to start on boot. That gap tends to surface only after the next reboot.
- `sudo systemctl enable --now docker` sets up both "start it now" and "start it automatically next boot" in one step. It's worth making a habit of using `enable --now` instead of just `start` for any systemd-managed service you rely on (nginx, postgresql, etc.) to avoid the same surprise after a reboot.

## FAQ

**Q: Does `enable --now` always fix a missing `docker.sock`?**
In most cases, yes, as long as the Docker Engine installation itself isn't broken. If `systemctl status docker` shows `failed` with a specific error, check `journalctl -u docker --no-pager` for more detail — a misconfigured `/etc/docker/daemon.json` is a common separate cause.

**Q: Why doesn't `apt install` enable the service automatically?**
Starting a service right after install is common postinstall behavior on Debian/Ubuntu packages, but enabling it at boot (systemd's `enable`) is tracked as a separate flag, and behavior can vary by distribution and package version. The safest approach is to explicitly check with `systemctl is-enabled docker` after installing.

**Q: Does this also affect containers that are supposed to auto-restart via Docker Compose?**
Yes. If docker.service itself isn't running, nothing starts — including containers configured with `restart: always`. On any server that gets rebooted as part of normal operations, it's worth adding a check for docker.service's enabled state to your deployment checklist.

## Related Articles

- [How to Fix Docker "Permission Denied" on docker.sock](/en/docker-permission-denied)
- [How to Use docker system prune to Free Up Disk Space](/en/docker-system-prune)
- [How to Manage Services with systemd (start/stop/enable/status)](/en/linux-systemd-service)
- [Fix "System has not been booted with systemd" When Starting Docker](/en/docker-systemd-not-booted)
- [Docker Basic Commands Cheatsheet (run/stop/rm/ps)](/en/docker-basic-commands)
