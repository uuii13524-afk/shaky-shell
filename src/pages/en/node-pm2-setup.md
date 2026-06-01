---
title: 'How to Keep Node.js Apps Running in Production with PM2'
date: '2026-05-31'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Node.js', 'PM2', 'VPS', 'Linux', 'プロセス管理']
en_tags: ['Node.js', 'PM2', 'VPS', 'Linux', 'process management']
description: 'How to keep Node.js apps running on a VPS using PM2. Covers installation, startup, auto-start on server reboot, log management, and ecosystem config.'
---
## What I Wanted to Do

Node.js apps kept stopping every time I disconnected from SSH on my VPS. I needed PM2 to keep them running in the background.

## Install PM2

```bash
npm install -g pm2
```

If you're using nvm, make sure you're on the right Node.js version before installing globally.

## Start Your App

```bash
pm2 start app.js
# or with a name
pm2 start app.js --name myapp
```

Using `--name` makes it easier to manage later.

## Common Commands

```bash
# List all running processes
pm2 list

# View logs
pm2 logs
pm2 logs myapp

# Restart
pm2 restart myapp

# Stop
pm2 stop myapp

# Remove from PM2
pm2 delete myapp
```

`pm2 list` also shows CPU and memory usage at a glance.

## Auto-Start After Server Reboot

```bash
pm2 startup
```

This outputs a command — copy and run it:

```bash
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu
```

Then save the current process list:

```bash
pm2 save
```

Now PM2 and your registered apps will start automatically on reboot.

## Managing Config with ecosystem.config.js

When running multiple apps or setting environment variables, a config file keeps things organized.

```js
module.exports = {
  apps: [{
    name: 'myapp',
    script: './app.js',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log'
  }]
};
```

```bash
pm2 start ecosystem.config.js
```

## Common Pitfalls

- If you use nvm, PM2 may fail to find the Node.js binary after `pm2 startup` — add the correct PATH to the startup command to fix it
- Forgetting `pm2 save` means your process list is lost after a reboot
- Logs pile up fast — install `pm2-logrotate` to handle rotation automatically
- When using nginx as a reverse proxy, make sure the PORT matches in both configs
- Don't mix root and non-root users with PM2 startup — it references the home directory of the running user

## Related Posts

- [Manage Node.js Versions with nvm](/en/node-version-management-nvm)
- [nginx Reverse Proxy Setup for Node.js Apps](/en/nginx-reverse-proxy)
- [Managing Services with systemd](/en/linux-systemd-service)
- [How to Check and Kill Processes in Linux](/en/linux-process-management)
- [Setting Up Docker on a VPS](/en/vps-docker-setup)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
