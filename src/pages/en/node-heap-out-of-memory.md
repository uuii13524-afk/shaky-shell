---
title: 'How to Fix "JavaScript Heap Out of Memory" in Node.js'
date: '2026-07-21'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'A Next.js build on a 1GB VPS died with JavaScript heap out of memory. A 2GB swap file plus NODE_OPTIONS=--max-old-space-size=1536 fixed it for good.'
ja_tags: ['Node.js', 'heap out of memory', 'メモリ不足', 'VPS']
en_tags: ['Node.js', 'heap out of memory', 'memory', 'VPS']
---

## What I Was Trying to Do

I'd moved a Next.js project onto a cheap 1GB-RAM VPS and kicked off a production build with `npm run build`. On my local machine the same build finishes in under three minutes. On the VPS, it stalled for a while and then died with this:

```text
<--- Last few GCs --->
[12345:0x55f8e2a1b000]    45231 ms: Mark-sweep 987.3 (1024.0) -> 980.1 (1024.0) MB, 1245.6 / 0.0 ms  (average mu = 0.123, current mu = 0.045) allocation failure; scavenge might not succeed

<--- JS stacktrace --->

FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory
 1: 0xb01110 node::Abort() [node]
 2: 0xa1b8f4 node::OOMErrorHandler(char const*, v8::OOMDetails const&) [node]
 3: 0xcf5a20 v8::Utils::ReportOOMFailure(v8::internal::Isolate*, char const*, bool) [node]
Aborted (core dumped)
```

The local machine and the VPS were running the exact same Node.js version and the exact same `package-lock.json`, so my first guess was that something in the codebase itself was the problem.

## Environment

- OS: Ubuntu 22.04.4 LTS (1GB RAM VPS plan)
- Node.js: v20.11.1
- npm: 10.2.4
- Framework: Next.js 14.1.0
- Swap: none configured (default state right after provisioning)

## What I Tried

My first suspicion was corrupted dependencies. I deleted `node_modules` and `package-lock.json`, reinstalled from scratch, and ran the build again.

```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

The install finished cleanly, but the build crashed at the exact same point — the `Collecting page data` phase — with the same `JavaScript heap out of memory` error. That ruled out dependency corruption; the actual problem was that the build simply didn't have enough memory available to it.

Next I checked available memory with `free -h`.

```bash
free -h
```

```text
               total        used        free      shared  buff/cache   available
Mem:           973Mi       210Mi        98Mi        1.0Mi       664Mi        620Mi
Swap:             0B          0B          0B
```

Physical memory was just under 1GB, and swap was at 0B. Next.js spins up several parallel Node.js processes while collecting page data during a build, so as soon as physical memory ran out, the OS couldn't allocate any more and the build process crashed.

## Why This Happens

The V8 engine that Node.js runs on has a default upper limit on the "old space" heap — the region subject to garbage collection. That limit is computed automatically from the Node.js version and the system's physical memory, and on 64-bit systems it commonly lands somewhere around 2GB. As heap usage approaches that limit, V8 repeatedly runs garbage collection (mark-compact) trying to reclaim unused memory. When reclaiming no longer frees enough space — a state V8 reports as "Ineffective mark-compacts" — it decides the heap can't grow any further and aborts the process. In my case, the process hit a wall well before reaching V8's own heap limit: it ran into the OS-level constraint of just 1GB of physical RAM. With swap at 0B, the moment physical memory was exhausted, the Linux kernel couldn't satisfy any further allocation, and the Node.js process went down in an OOM state.

## Solution

### 1. Create a swap file

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

```bash
free -h
```

```text
               total        used        free      shared  buff/cache   available
Mem:           973Mi       215Mi        90Mi        1.0Mi       667Mi        615Mi
Swap:          2.0Gi          0B       2.0Gi
```

When physical memory runs low, the OS can now treat space on disk as virtual memory, so the build process isn't an immediate target for the OOM killer.

### 2. Make the swap file survive a reboot

```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

`swapon` alone only affects the current boot — the swap gets disabled again on reboot. Registering it in `/etc/fstab` makes it mount automatically every time the machine starts.

### 3. Cap V8's heap explicitly with NODE_OPTIONS

```bash
export NODE_OPTIONS="--max-old-space-size=1536"
npm run build
```

```text
   ▲ Next.js 14.1.0

   Creating an optimized production build ...
 ✓ Compiled successfully
 ✓ Collecting page data
 ✓ Generating static pages (12/12)
```

`--max-old-space-size` sets V8's heap ceiling in megabytes. Picking a value that comfortably fits within your physical memory plus swap helps avoid the process getting killed by the OOM killer from unbounded memory growth.

## Gotchas

- Right after creating the swap file, `free -h` showed it correctly — but after rebooting the VPS for an unrelated reason, `Swap: 0B` was back. I'd forgotten to add the entry to `/etc/fstab`.
- I tried setting `--max-old-space-size` to something like 4096 (4GB), well above actual RAM. The build ran further, but eventually `dmesg` showed an `Out of memory: Killed process` entry and the process got killed anyway. Raising the heap ceiling can't make memory exceed physical RAM plus swap.
- When building inside a Docker container, adding swap on the host didn't help — the container's own `--memory` limit from `docker run` took precedence, and the same error came back. The container's memory limit needed adjusting too.
- I'd been running `npm run build` in the background with `&`, which made it hard to tell that the process had actually been killed by the OOM killer rather than just finishing weirdly. Running it in the foreground and reading the error output directly made the cause obvious much faster.

## FAQ

**Q: What's the minimum amount of memory needed to fix a Node.js heap out of memory error?**
It depends on the project, but for a mid-sized frontend build like Next.js or Nuxt, aiming for 2GB or more combined physical memory and swap tends to be stable. Check your current total with `free -h`, and either add swap or upgrade your VPS's memory plan if it's short.

**Q: Why does node heap out of memory only happen inside a Docker container?**
A Docker container can have its own memory ceiling, separate from the host, set via the `--memory` flag or `mem_limit` in `docker-compose.yml`. No matter how much free memory the host has, once the container hits its own limit, the Node.js process inside it gets killed by the OOM killer. Check the current limit with `docker inspect <container-name> | grep -i memory`.

**Q: Doesn't using swap slow things down due to disk I/O?**
Swap is significantly slower to access than physical memory, so you don't want a workload that's constantly swapping heavily. As a safety net for a temporary memory spike like a build, though, it's rarely a practical problem. If you notice swap being used constantly rather than occasionally, check activity with `vmstat 1` and consider adding real memory instead.

## Related Articles

- [How to Create and Configure a Swap File on Linux](/en/linux-swap-setup)
- [How to Install Docker on a VPS and Set Up a Web Server](/en/vps-docker-setup)
- [How to Clear the npm Cache](/en/npm-cache-clear)
- [How to Manage Node.js Versions with nvm](/en/node-version-management-nvm)
- [How to Check Container Resource Usage with docker stats](/en/docker-stats-command)
