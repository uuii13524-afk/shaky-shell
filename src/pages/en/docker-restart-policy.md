---
title: 'Docker Restart Policy Explained: --restart Options for Containers'
date: '2026-07-01'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'restart policy', 'container operations']
description: 'Learn how to use docker run --restart to auto-restart containers. Covers no, on-failure, always, and unless-stopped, plus how to apply it to running containers.'
---

## Quick Answer

```bash
# Automatically start the container even after a server reboot
docker run -d --restart unless-stopped nginx

# Apply a restart policy to an already-running container
docker update --restart unless-stopped <container_name>
```

---

## What You're Trying to Do

Your container crashes or the server reboots, and the container doesn't come back up on its own. You want production services to automatically restart without manual intervention.

---

## Environment

- Docker Engine 24.x or later
- OS: Ubuntu 22.04 / CentOS / WSL2
- The `docker` service should be configured to start on boot via systemd

> **Note:** Restart policies only take effect while the Docker daemon itself is running. Make sure the daemon starts on boot with `systemctl enable docker`.

---

## Solution

### The Four Restart Policies

```bash
docker run -d --restart no <image>              # Never restart automatically (default)
docker run -d --restart on-failure <image>       # Restart only on non-zero exit code
docker run -d --restart on-failure:5 <image>     # Restart up to 5 times
docker run -d --restart always <image>           # Always restart, even after manual stop
docker run -d --restart unless-stopped <image>   # Always restart unless manually stopped
```

| Policy | Behavior |
|--------|----------|
| `no` | Never restarts automatically (default) |
| `on-failure[:count]` | Restarts only when the container exits with a non-zero code |
| `always` | Restarts no matter why it stopped — even comes back after a daemon restart if you had run `docker stop` |
| `unless-stopped` | Same as `always`, but skips restarting if you explicitly ran `docker stop` |

### Recommended for Production

For services that need to run continuously, like web servers or databases, `unless-stopped` is usually the easiest to reason about.

```bash
docker run -d --restart unless-stopped -p 80:80 nginx
```

With `always`, a container you intentionally stopped can come back after a daemon restart, which causes confusion during maintenance windows.

### Updating the Policy on a Running Container

You can apply a restart policy after the fact without recreating the container.

```bash
docker update --restart unless-stopped my-container
```

To update multiple containers at once:

```bash
docker update --restart unless-stopped $(docker ps -q)
```

### Setting It in docker-compose

```yaml
services:
  web:
    image: nginx
    restart: unless-stopped
```

Run `docker compose up -d` and this policy is applied automatically.

### Checking the Current Policy

```bash
docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' my-container
```

---

## Common Errors

### Container doesn't start after a server reboot even with a restart policy set

The Docker daemon itself may not be starting on boot.

```bash
sudo systemctl enable docker
sudo systemctl status docker
```

### `Error response from daemon: no such container`

The container name or ID is wrong. Check the exact name with `docker ps -a`.

```bash
docker ps -a
docker update --restart unless-stopped <correct_container_name>
```

### `on-failure` keeps restarting forever

Without a retry limit, Docker will keep retrying indefinitely on every failure. Set a count.

```bash
docker update --restart on-failure:3 my-container
```

### Container gets stuck in a restart loop (CrashLoop)

An application-level error can cause `on-failure` or `always` to loop endlessly. Check the logs.

```bash
docker logs --tail 50 my-container
```

---

## FAQ

**Q: What's the difference between `always` and `unless-stopped`?**  
`always` restarts the container after a daemon restart even if you had stopped it manually with `docker stop`. `unless-stopped` keeps it stopped in that case.

**Q: What's the default restart policy if I don't set `--restart`?**  
The default is `no`, meaning the container will not restart automatically.

**Q: In `docker-compose.yml`, should I use `restart: always` or `restart: unless-stopped`?**  
`unless-stopped` is recommended for production. It prevents containers from unexpectedly coming back after you intentionally stop them for maintenance.

**Q: How do I check the current restart policy of a container?**  
Run `docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' <container_name>`.

**Q: What happens once `on-failure` exceeds its retry count?**  
Docker stops trying to restart the container and it remains in a stopped state.

---

## Related Articles

- [docker compose down: Stop and Remove Containers, Networks, and Volumes](/en/docker-compose-down)
- [docker logs: View Container Logs](/en/docker-logs)
- [docker system prune: Clean Up Unused Docker Resources](/en/docker-system-prune)
- [docker exec: Open a Bash Shell Inside a Container](/en/docker-exec-bash)

## Recommended VPS / Hosting

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
