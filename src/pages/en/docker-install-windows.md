---
title: 'How to Install Docker on Windows and Get It Running'
date: '2026-05-10'
category: 'Docker'
---

## What I Wanted to Do

Get Docker running on Windows. There are a few common pitfalls worth knowing before you start.

## Environment

- Windows 10 / 11 (64-bit)

## Steps

### 1. Install WSL2

Open PowerShell as Administrator and run:

```
wsl --install
```

Restart Windows when done.

### 2. Download Docker Desktop

Go to https://www.docker.com/products/docker-desktop and click "Download for Windows".

### 3. Install

Run the installer. Make sure "Use WSL 2 instead of Hyper-V" is checked. Restart Windows after installation.

### 4. Verify

```
docker --version
docker run hello-world
```

If you see "Hello from Docker!" the installation is working correctly.

## Common Issues

### Virtualization not enabled in BIOS

```
Hardware assisted virtualization and data execution protection must be enabled in the BIOS
```

Enable Intel VT-x or AMD-V in your BIOS settings.

### WSL2 not installed

```
wsl --install
wsl --update
```

Restart and try again.

## Basic Commands

```
docker ps           # List running containers
docker ps -a        # List all containers
docker images       # List images
docker stop ID      # Stop a container
docker rm ID        # Remove a container
```

## Related Articles

- [Docker Basic Commands Cheatsheet](/posts/docker-basic-commands)
- [How to Use docker-compose](/posts/docker-compose-basic)
- [How to Install WSL2 on Windows](/posts/wsl2-install-windows)
