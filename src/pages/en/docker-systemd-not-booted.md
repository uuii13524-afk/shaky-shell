---
title: 'Fix "System has not been booted with systemd" When Starting Docker'
date: '2026-07-29'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
description: 'systemctl start docker fails with "System has not been booted with systemd as init system" on a lightweight VPS. Here is why PID 1 is not systemd on some hosts, and how to start dockerd directly instead.'
en_tags: ['Docker', 'systemd', 'dockerd', 'PID 1']
---

## What I Was Trying to Do

I installed Docker on a budget VPS plan following the official steps, then ran `docker ps` to check it worked. Instead, I got a connection error to the daemon.

```bash
docker ps
```

```text
failed to connect to the docker API at unix:///var/run/docker.sock; check if the path is correct and if the daemon is running: dial unix /var/run/docker.sock: connect: no such file or directory
```

Assuming the daemon simply wasn't running yet, I tried starting it with `systemctl`, which failed with a completely different error.

```bash
systemctl start docker
```

```text
System has not been booted with systemd as init system (PID 1). Can't operate.
Failed to connect to bus: Host is down
```

The install itself had completed without any errors, and `docker --version` printed the correct client version. But the command to actually start the service wasn't even accepted, which was confusing at first.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Host: a budget VPS plan (LXC-based container virtualization, not full KVM virtualization)
- Docker: 29.3.1 (installed via the official install script)
- init: PID 1 is not systemd, but the container's own launcher process

## What I Tried

First I tried `service` (the SysVinit-style wrapper) instead of `systemctl`, in case that would work differently.

```bash
service docker start
```

```text
* Docker is not running
```

```bash
service docker status
```

```text
* Docker is not running
```

`service` ran without throwing an error, but Docker was in fact not running afterward. So I checked what was actually running as PID 1 on this box.

```bash
ps -p 1 -o pid,comm
```

```text
    PID COMMAND
      1 tini
```

PID 1 was `tini` (a minimal init process), not `systemd`. That explained the "System has not been booted with systemd" message. This VPS plan uses container-based virtualization rather than full KVM virtualization, and reuses the host's own init process instead of running its own systemd instance — so systemd simply wasn't present, or at least wasn't running as PID 1.

## Why This Happens

`systemctl` and `service` work by sending commands to the systemd init process (PID 1) over its control socket. On this host, PID 1 was `tini`, and systemd wasn't running at all, so `systemctl start docker` failed immediately with "can't operate, this isn't systemd." The Docker package itself — the `dockerd` binary, the CLI, and the `docker.service` unit file — had been installed correctly by the official install script. The problem wasn't a broken install; it was that the mechanism meant to launch that service file (systemd) didn't exist in this environment. In other words, the root cause was the VPS plan's virtualization type, not anything wrong with the Docker installation steps.

## Solution

### 1. Check whether PID 1 is actually systemd

```bash
ps -p 1 -o comm=
```

If this returns anything other than `systemd` (such as `tini` or `init`), Docker cannot be managed through `systemctl`/`service` on this host at all.

### 2. Start dockerd directly

Skip systemd entirely and launch `dockerd` as a background process.

```bash
dockerd > /var/log/dockerd.log 2>&1 &
```

Wait a few seconds, then check the tail of the log for the line confirming the daemon is listening.

```bash
tail -5 /var/log/dockerd.log
```

```text
time="2026-07-29T00:10:25.601757834Z" level=info msg="Docker daemon" commit=f78c987 containerd-snapshotter=true storage-driver=overlayfs version=29.3.1
time="2026-07-29T00:10:25.640565695Z" level=info msg="Daemon has completed initialization"
time="2026-07-29T00:10:25.640910959Z" level=info msg="API listen on /var/run/docker.sock"
```

### 3. Verify it works

```bash
docker ps
```

```text
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

An empty container list with no connection error means the daemon is reachable again.

### 4. Make it survive a reboot

Backgrounding it with `&` only lasts until the server restarts — you'd have to run `dockerd` by hand again after every reboot. For anything long-running, register `dockerd` with a process manager like supervisord if the environment supports one, or add the start command to whatever boot script the host uses (an `/etc/rc.local`-style script), so it launches automatically on boot.

## Gotchas

- `service docker start` exited without an error, which briefly made me think it had worked. It hadn't — it silently no-oped because systemd wasn't detected. Checking `service docker status` right after was what caught it.
- Because the install script printed success messages, I re-ran the Docker installation itself several times before realizing the problem was the init system, not the install.
- Running `dockerd` in the foreground and then disconnecting the SSH session killed it along with the daemon. Backgrounding with `&` (or using `nohup`/`disown`) is necessary to keep it alive after logging out.

## FAQ

**Q: Does this same error show up on WSL?**
Yes — WSL1, or a WSL2 distro without systemd support enabled, has the same problem since PID 1 isn't systemd there either. If systemd support is enabled in WSL2, `systemctl` works normally.

**Q: Is running `dockerd` directly like this safe for production use?**
For anything that needs to stay up, manage it with a proper process manager (like supervisord) so it doesn't die when an SSH session ends. A bare `&` launch is fine for verification or temporary use, not for a production daemon.

**Q: Are there other limitations running Docker on this kind of container-based VPS?**
Because container-based virtualization shares parts of the kernel with the host, networking and cgroup behavior can differ from a full KVM VPS. In this case `docker ps` worked fine afterward, but depending on the host, additional configuration may still be needed.

## Related Articles

- [How to Install Docker on a VPS and Build a Web Server](/en/vps-docker-setup)
- [Basic Docker Commands Cheat Sheet](/en/docker-basic-commands)
- [Fixing "Permission Denied" with the docker Command](/en/docker-permission-denied)
- [Basic Usage of docker-compose](/en/docker-compose-basic)
- [How to Clean Up Unused Docker Images](/en/docker-image-cleanup)
