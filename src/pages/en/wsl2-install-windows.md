---
title: 'How to Install WSL2 on Windows'
date: '2026-05-11'
category: 'Windows'
---

## What I Wanted to Do

Run Linux commands directly on Windows without a virtual machine.
WSL2 (Windows Subsystem for Linux 2) makes this possible.

## Requirements

- Windows 10 version 2004 or later
- Windows 11

## Steps

### 1. Install WSL2

Open PowerShell as Administrator and run:

```
wsl --install
```

This automatically installs WSL2 and Ubuntu. Restart Windows when done.

### 2. Initial Ubuntu Setup

After restarting, Ubuntu launches automatically. Set a username and password (this is your Linux password — remember it).

### 3. Verify

```
wsl
```

Or launch "Ubuntu" from the Start menu. If a Linux terminal opens, you're done.

## Useful WSL Commands

```
wsl --shutdown         # Stop WSL
wsl --update           # Update WSL
wsl --list --verbose   # List installed distributions
```

## Common Issues

### Virtualization not enabled in BIOS

```
Please enable the Virtual Machine Platform Windows feature
and ensure virtualization is enabled in the BIOS.
```

Enable Intel VT-x or AMD-V in BIOS settings.

### Windows needs updating

WSL2 requires a recent version of Windows. Run Windows Update first, then retry.

## Accessing Files Between Windows and Linux

From WSL2, access Windows files:

```bash
cd /mnt/c/Users/username/
```

From Windows Explorer, access WSL2 files by typing in the address bar:

```
\\wsl$\Ubuntu\home\username
```

## Key Points

- WSL2 is faster and more compatible than WSL1
- Docker Desktop on Windows uses WSL2 as its backend
- After installing WSL2, Ubuntu appears automatically in Windows Terminal

## Related Articles

- [How to Install Docker on Windows](/en/docker-install-windows)
- [Linux Basic Commands Cheatsheet](/en/linux-basic-commands)
- [Linux Permission Denied Error Fix](/en/linux-permission-denied)
