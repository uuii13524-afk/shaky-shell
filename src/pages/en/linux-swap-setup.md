---
title: 'How to Set Up Swap on Linux (swapfile, enable, check)'
date: '2026-05-24'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'swap', 'VPS']
en_tags: ['Linux', 'swap', 'VPS']
---

## What I Wanted to Do

My VPS only had 1GB of RAM, and running Docker or Node.js would trigger the OOM Killer and kill my processes.
I needed to add swap space to relieve the memory pressure.

## What Is Swap?

Swap is a mechanism that uses part of the disk as a substitute for RAM when physical memory runs out.
It's slower than RAM, but much better than having processes killed unexpectedly.

## Create a Swap File

```bash
# Create a 2GB swap file (bs=1M × count=2048)
sudo dd if=/dev/zero of=/swapfile bs=1M count=2048

# Set permissions (readable/writable by root only)
sudo chmod 600 /swapfile

# Format it as swap space
sudo mkswap /swapfile
```

## Enable the Swap

```bash
# Enable swap
sudo swapon /swapfile

# Confirm it's active
sudo swapon --show
```

You should see output like this:

```
NAME      TYPE SIZE USED PRIO
/swapfile file   2G   0B   -2
```

## Check Swap Usage

```bash
# Memory and swap usage overview
free -h
```

```
              total        used        free      shared  buff/cache   available
Mem:          980Mi       400Mi       100Mi        10Mi       480Mi       450Mi
Swap:         2.0Gi         0B       2.0Gi
```

```bash
# More detailed info
cat /proc/meminfo | grep -i swap
```

## Make Swap Persist After Reboot

Without this step, swap will be disabled after a reboot. Add an entry to `/etc/fstab` to make it permanent.

```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Verify the entry was added:

```bash
cat /etc/fstab | grep swap
```

```
/swapfile none swap sw 0 0
```

## Tune swappiness

`swappiness` controls how aggressively the kernel uses swap (range: 0–100).
VPS servers often default to 60, but a lower value is recommended for server workloads.

```bash
# Check current value
cat /proc/sys/vm/swappiness

# Change temporarily (resets on reboot)
sudo sysctl vm.swappiness=10

# Persist the change
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## Remove Swap When No Longer Needed

```bash
# Disable swap
sudo swapoff /swapfile

# Delete the file
sudo rm /swapfile

# Also remove the line from /etc/fstab
sudo vim /etc/fstab
```

## Common Pitfalls

- Forgetting `chmod 600` will cause `mkswap` to fail
- Without the `/etc/fstab` entry, swap disappears every time you reboot
- A good swap size is 1–2x your RAM (e.g., 2GB swap for a 1GB RAM VPS)
- On SSD-based VPS, lower `swappiness` to around 10 to reduce write wear
- If the Swap line in `free -h` still shows `0`, `swapon` did not succeed

## Related Posts

- [Linux Basic Commands (ls/cd/mkdir/rm)](/en/linux-basic-commands)
- [Linux File Permissions Explained (chmod/chown)](/en/linux-file-permissions)
- [Linux Process Management (ps/kill/top)](/en/linux-process-management)
- [Set Up Docker on a VPS](/en/vps-docker-setup)

## Recommended VPS Services

If you want to build a production environment on a VPS, these services are worth checking out.

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
