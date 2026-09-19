---
title: 'Fix: Astro Dev Server Crashes Right After Start with "ENOSPC: System limit for number of file watchers reached"'
date: '2026-09-19'
category: 'Astro'
layout: '../../layouts/PostLayoutEn.astro'
description: 'On a VPS, astro dev crashes seconds after starting with ENOSPC: System limit for number of file watchers reached. Here is why fs.inotify.max_user_watches is the real cause, with the actual error log and how to raise it permanently via sysctl.'
en_tags: ['Astro', 'ENOSPC', 'inotify', 'Vite', 'VPS']
---

## What I Was Trying to Do

I wanted to run this Astro blog's dev server on a test VPS instead of only locally, so after SSHing in I set it up the usual way.

```bash
cd shaky-shell
npm install
npm run dev -- --host 127.0.0.1 --port 4321
```

`npm install` finished cleanly with 271 packages, and `npm run dev` looked like it started fine too — it printed `[vite] connected.`. But before I could even open it in a browser, the whole process crashed a few seconds later with an unhandled exception.

```text
> shaky-shell@0.0.1 dev
> astro dev --host 127.0.0.1 --port 4321

▶ Astro collects anonymous usage data.
  This information helps us improve Astro.
  Run "astro telemetry disable" to opt-out.
  https://astro.build/telemetry

[vite] connected.
node:internal/fs/watchers:254
    const error = new UVException({
                  ^

Error: ENOSPC: System limit for number of file watchers reached, watch '/home/user/shaky-shell/src/pages/en/docker-stats-command.md'
    at FSWatcher.<computed> (node:internal/fs/watchers:254:19)
    at Object.watch (node:fs:2554:36)
    at createFsWatchInstance (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:12958:16)
    at setFsWatchListener (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:13000:14)
    at NodeFsHandler$1._watchWithNodeFs (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:13114:20)
    at NodeFsHandler$1._handleFile (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:13158:24)
    at NodeFsHandler$1._addToNodeFs (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:13332:26)
Emitted 'error' event on FSWatcher instance at:
    at FSWatcher._handleError (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:14133:148)
    at NodeFsHandler$1._addToNodeFs (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:13337:18) {
  errno: -28,
  syscall: 'watch',
  code: 'ENOSPC',
  path: '/home/user/shaky-shell/src/pages/en/docker-stats-command.md',
  filename: '/home/user/shaky-shell/src/pages/en/docker-stats-command.md'
}

Node.js v22.22.2
```

The file it choked on wasn't always the same — a different run would crash on a different file, `docker-stats-command.md` one time, something else the next. My first guess was that this specific Markdown file was corrupted, so I checked it, but it was perfectly fine.

## Environment

- OS: Ubuntu (VPS container environment, working as root)
- Node.js: v22.22.2
- npm: 10.9.7
- Astro: v6.3.5 (`astro dev` uses Vite's file watcher internally)
- Project: a blog with 127+ Markdown files each under `src/pages/posts/` and `src/pages/en/`

## What I Tried

My first suspicion was a broken `npm install` or corrupted packages. I wiped `node_modules` and reinstalled from scratch.

```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

Same result — it crashed with `ENOSPC` again a few seconds in. Since the file it failed on seemed random, I stopped suspecting a single bad file and started suspecting a limit on the total number of files that could be watched at once. The error said `ENOSPC` (No space left on device), but `df -h` showed plenty of free disk space.

```bash
df -h /
```

```text
Filesystem      Size  Used Avail Use% Mounted on
overlay          40G   12G   28G  30% /
```

Disk space wasn't the problem, which pointed toward a different meaning of `ENOSPC`: it's also the error Linux returns when a process hits the limit on how many files it's allowed to watch via inotify. I checked the actual limit.

```bash
cat /proc/sys/fs/inotify/max_user_watches
```

```text
100
```

On this VPS, the value was set to just `100`.

## Root Cause

Astro's dev server (`astro dev`) uses Vite internally, and Vite registers an inotify watch on essentially every source file it needs to detect changes on. This blog alone has 127+ Markdown files under `src/pages/posts/` and another 127+ under `src/pages/en/`, plus components, layouts, and some files inside `node_modules` — easily several hundred to a few thousand watch targets in total.

The Linux kernel caps how many inotify watches a single user can hold open at once, controlled by the kernel parameter `fs.inotify.max_user_watches`. Most distributions default this to around 8192, but the container image this VPS was built from had it set to an unusually low `100`. The moment Vite's watcher tried to register more file watches than that ceiling allowed, the underlying `fs.watch()` call failed with `ENOSPC: System limit for number of file watchers reached`, and the uncaught exception took down the entire Node.js process.

What made this confusing is that `ENOSPC` (Error No Space) strongly suggests a disk-space problem, and it took a `df -h` check to rule that out before I widened my search. `ENOSPC` isn't disk-specific — the same kernel error code is returned when a syscall hits any kind of resource ceiling, including the inotify watch limit. That's the piece of first-hand information that mattered here: the error name is misleading, and disk capacity is only one of the things it can mean.

## How I Fixed It

### 1. Check the current inotify watch limit

```bash
cat /proc/sys/fs/inotify/max_user_watches
```

```text
100
```

Confirmed it was far lower than expected.

### 2. Raise the limit temporarily with sysctl

To verify the fix quickly, I raised it with `sysctl` first (this resets on reboot).

```bash
sudo sysctl fs.inotify.max_user_watches=524288
```

```text
fs.inotify.max_user_watches = 524288
```

### 3. Restart the dev server and check

```bash
npm run dev -- --host 127.0.0.1 --port 4321
```

```text
> shaky-shell@0.0.1 dev
> astro dev --host 127.0.0.1 --port 4321

[vite] connected.
00:09:38 [types] Generated 0ms
 astro  v6.3.5 ready in 1451 ms
┃ Local    http://127.0.0.1:4321/
00:09:38 watching for file changes...
```

This time it stayed up — no `ENOSPC`, and it reached `watching for file changes...` and kept running.

### 4. Make the change persist across reboots

A value set with `sysctl` alone resets on reboot, so I added a config file under `/etc/sysctl.d/` to make it permanent.

```bash
echo "fs.inotify.max_user_watches=524288" | sudo tee /etc/sysctl.d/99-inotify-watches.conf
sudo sysctl -p /etc/sysctl.d/99-inotify-watches.conf
```

```text
fs.inotify.max_user_watches=524288
fs.inotify.max_user_watches = 524288
```

With this file in place, the limit gets reapplied automatically on boot — no more typing the `sysctl` command by hand after every restart.

## Verify It Works

After adding the config file, I actually rebooted the VPS and checked whether the value survived without running `sysctl` manually.

```bash
cat /proc/sys/fs/inotify/max_user_watches
```

```text
524288
```

The value held across the reboot. I then started the dev server again and left it running while editing files for several minutes to confirm `ENOSPC` didn't come back.

```bash
sysctl fs.inotify.max_user_watches
```

```text
fs.inotify.max_user_watches = 524288
```

## Takeaways

- `astro dev` (via Vite under the hood) consumes one Linux inotify watch per file it monitors. The more files in the project, the more watches it needs.
- The name `ENOSPC` makes disk space the obvious first suspect, but if `df -h` shows plenty of free space and you still hit this error, check `fs.inotify.max_user_watches` — you're very likely hitting the inotify watch ceiling instead. `cat /proc/sys/fs/inotify/max_user_watches` is the fastest way to confirm it.
- `sudo sysctl fs.inotify.max_user_watches=524288` fixes it immediately, but that alone resets on reboot — the full fix also needs a config file under `/etc/sysctl.d/` to make the change permanent.

## FAQ

**Q: Is there a reason to pick `524288` specifically?**
It's the value commonly recommended in the official docs of tools like Vue CLI, VS Code, and JetBrains IDEs for exactly this kind of issue, and it's widely considered safe to set on most Linux distributions. Smaller projects may get by with something like `65536`.

**Q: Do I need to do this inside Docker containers or WSL2 too?**
Containers and WSL2 usually share the host kernel's parameters, so the fix needs to happen on the host side (the VPS itself, or the WSL2 configuration on Windows). Running `sysctl` only inside the container may not take effect at all, depending on permissions and namespace configuration.

**Q: Does raising `max_user_watches` use a lot of memory?**
Each inotify watch uses only a small amount of memory (on the order of a few hundred bytes), so raising the limit to something like `524288` is not a meaningful concern on a typical VPS. That said, there's no need to set it higher than your project actually requires.

## Related Articles

- [How to Add a New Page in Astro](/en/astro-add-page)
- [Deploying an Astro Project to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [Managing Node.js Versions with nvm](/en/node-version-management-nvm)
- [Setting Up Docker on a VPS for Production](/en/vps-docker-setup)
- [Setting Up Swap Space on Linux](/en/linux-swap-setup)
