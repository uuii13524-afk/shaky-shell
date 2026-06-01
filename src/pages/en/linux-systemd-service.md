---
title: 'How to Manage Services with systemd (start/stop/enable/status)'
date: '2026-05-24'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'systemd', 'サービス管理']
en_tags: ['Linux', 'systemd', 'service management']
---

## What I Wanted to Do

I wanted to restart nginx or Docker and configure them to start automatically on boot.
On Linux, systemd handles starting, stopping, and enabling services.

## Basic Commands

```bash
# Start a service
sudo systemctl start nginx

# Stop a service
sudo systemctl stop nginx

# Restart a service
sudo systemctl restart nginx

# Reload config without stopping
sudo systemctl reload nginx
```

## Checking Service Status

```bash
sudo systemctl status nginx
```

Output looks like this:

```
● nginx.service - A high performance web server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled)
     Active: active (running) since ...
```

- `active (running)` → service is running
- `inactive (dead)` → service is stopped
- `failed` → service failed to start

## Enabling Auto-Start on Boot

Use `enable` to start a service automatically when the OS boots.

```bash
# Enable auto-start
sudo systemctl enable nginx

# Disable auto-start
sudo systemctl disable nginx

# Check current auto-start status
sudo systemctl is-enabled nginx
```

If it shows `enabled`, auto-start is configured.

## Checking Logs with journalctl

```bash
# View service logs
sudo journalctl -u nginx

# Show only the latest 50 lines
sudo journalctl -u nginx -n 50

# Follow logs in real time
sudo journalctl -u nginx -f

# Show only today's logs
sudo journalctl -u nginx --since today
```

## Creating a Custom Service

You can register your own script as a systemd service.

```bash
sudo vim /etc/systemd/system/myapp.service
```

```ini
[Unit]
Description=My Application
After=network.target

[Service]
ExecStart=/home/user/myapp/start.sh
Restart=always
User=user
WorkingDirectory=/home/user/myapp

[Install]
WantedBy=multi-user.target
```

After creating the file, reload the daemon and start the service.

```bash
# Reload systemd to pick up the new config
sudo systemctl daemon-reload

# Enable and start the service in one step
sudo systemctl enable --now myapp
```

## Useful Commands Summary

```bash
# List all services and their status
sudo systemctl list-units --type=service

# Show only failed services
sudo systemctl --failed

# View the service definition file
sudo systemctl cat nginx
```

## Common Pitfalls

- `enable` alone does not start the service — also run `start`, or use `enable --now`
- Always run `daemon-reload` after adding or modifying a custom service file
- Use full paths in `ExecStart` (e.g. `/usr/bin/python3`)
- `Restart=always` makes the service restart automatically after a crash
- If logs fill up disk space, clean them with `journalctl --vacuum-time=7d`

## Related Articles

- [Linux Basic Commands (ls/cd/mkdir/rm)](/posts/linux-basic-commands)
- [Linux Process Management (ps/kill/top)](/posts/linux-process-management)
- [How to Set Up Cron Jobs on Linux](/posts/linux-cron-setup)
- [nginx Basic Config File Setup](/posts/nginx-basic-config)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
