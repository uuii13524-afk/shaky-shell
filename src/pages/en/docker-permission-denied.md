---
title: 'How to Fix Docker "Permission Denied" on docker.sock'
date: '2026-07-18'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
description: 'docker.sock returns permission denied when running docker ps without sudo. Why chmod 666 resets after reboot, and the usermod -aG docker fix that persists.'
ja_tags: ['Docker', 'permission denied', 'docker.sock', 'usermod']
en_tags: ['Docker', 'permission denied', 'docker.sock', 'usermod']
---

## What I Was Trying to Do

I'd just installed Docker on a fresh VPS using the official `get.docker.com` script and wanted to confirm it worked by running `docker ps` without `sudo`. Instead of a container list, I got this:

```text
docker: permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.45/containers/json": dial unix /var/run/docker.sock: connect: permission denied
```

`docker version` had already shown both a `Client:` and `Server:` block with matching version numbers, so the install itself clearly hadn't failed. I couldn't figure out why a plain `docker ps` would fail when the daemon was obviously running.

## Environment

- OS: Ubuntu 22.04.4 LTS (Sakura VPS)
- Docker Engine: 26.1.4
- Docker Compose: v2.27.0
- Login user: `deploy` (has `sudo`, but isn't root)
- Install method: official `get.docker.com` convenience script

## What I Tried

My first instinct was to just prefix every command with `sudo`. That worked fine interactively, but it broke later when a GitHub Actions self-hosted runner running as `deploy` tried to call `docker compose up` as part of an automated deploy — the runner script had no way to answer a `sudo` password prompt, and the job just hung.

Thinking I'd found the real fix, I went straight for the socket's file permissions:

```bash
sudo chmod 666 /var/run/docker.sock
docker ps
```

```text
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS   PORTS   NAMES
```

`docker ps` ran without `sudo` and I moved on, assuming it was fixed. The next day I rebooted the VPS for an unrelated kernel update, and the exact same `permission denied` error came right back. The `chmod` change only applied to that one socket file — every time dockerd restarts, systemd recreates the socket with its default ownership and mode, wiping out the manual change.

## Why This Happens

The Docker daemon listens on the Unix socket `/var/run/docker.sock`, which is created owned by `root:docker` with mode `660` — readable and writable only by the owner and members of the `docker` group. If your login user isn't in that group, only processes running as root (i.e. through `sudo`) can talk to the socket, so anything else gets `permission denied`. Manually `chmod`-ing the socket only changes that specific file instance; since it's managed by a systemd socket unit, dockerd recreates it with the default `root:docker 660` permissions on every restart, so the fix never survives a reboot.

## Solution

### 1. Add your user to the docker group

```bash
sudo usermod -aG docker $USER
```

This command itself succeeds silently, but your current shell session still doesn't know about the new group membership yet.

### 2. Apply the group change to your session

Log out and back in, or use `newgrp` to pick up the change without ending the session.

```bash
newgrp docker
groups
```

```text
deploy sudo docker
```

Once `docker` shows up in the output of `groups`, the current shell is running with the group membership applied. Group membership for a login shell is resolved at login time, so `usermod` alone doesn't affect an already-open session — you need to either start a new session or force one with `newgrp`.

### 3. Confirm it works without sudo

```bash
docker ps
```

```text
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS   PORTS   NAMES
```

If `docker ps` completes without `sudo` and without an error, the socket permissions are correctly resolved through group membership. Unlike the `chmod` approach, this survives dockerd and systemd restarts, since it doesn't depend on the socket's file mode at all.

## Gotchas

- Right after running `usermod -aG docker $USER`, I ran `docker ps` in the same terminal and assumed the fix hadn't worked. Group membership for a shell is fixed at login time, so it doesn't take effect in a session that was already open.
- The `chmod 666 /var/run/docker.sock` fix looked like it worked, but the error came right back after rebooting the VPS the next day — dockerd recreated the socket with its default `660` permissions on restart.
- I later learned that being in the `docker` group is effectively equivalent to having root on the host. Anyone in that group can start a container that bind-mounts the host filesystem, which is a well-known privilege escalation path.
- Our GitHub Actions self-hosted runner, running as `deploy`, had already started before I ran `usermod`. The group change didn't take effect for the runner's own process until I restarted the runner service itself.

## FAQ

**Q: Is it safe to add my user to the docker group?**
Anyone in the `docker` group can launch a container with the host filesystem bind-mounted, which is effectively equivalent to root access on the host. It's a common and reasonable setup for a personal dev box or a dedicated test VPS, but on a server shared by multiple people you should think carefully about who gets that membership.

**Q: I don't want to reboot the server. Can I make this take effect right now?**
Run `newgrp docker` to apply the group change immediately in that one shell session. It won't affect other open terminals or SSH sessions, so for a permanent fix across all sessions you still need to log out and back in eventually.

**Q: Does this same fix apply to Docker Desktop on WSL2?**
Not always. When you're using Docker Desktop's WSL2 integration, `/var/run/docker.sock` inside WSL is often proxied from the Docker Desktop engine running on Windows, so running `usermod` inside WSL may not fix anything. In that case, enable the relevant distro under Docker Desktop's Settings > Resources > WSL Integration instead.

## Related Articles

- [How to List Containers with docker ps](/en/docker-ps-command)
- [How to Get a Bash Shell Inside a Running Container with docker exec](/en/docker-exec-bash)
- [Linux User Management Commands Cheat Sheet](/en/linux-user-management)
- [How to Fix Permission Denied Errors on Linux](/en/linux-permission-denied)
- [How to Install Docker on a VPS and Set Up a Web Server](/en/vps-docker-setup)
