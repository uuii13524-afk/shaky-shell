---
title: 'How to Fix "EADDRINUSE: Address Already in Use" in Node.js'
date: '2026-07-21'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'A restarted nodemon server failed with EADDRINUSE: address already in use :::3000, caused by a zombie node process. lsof -i :3000 plus kill -9 freed the port.'
ja_tags: ['Node.js', 'EADDRINUSE', 'ポート使用中', 'express']
en_tags: ['Node.js', 'EADDRINUSE', 'port in use', 'express']
---

## What I Was Trying to Do

I was running an Express API through nodemon inside WSL2. The server crashed once while I was mid-edit, so I hit `Ctrl + C` to stop the terminal, then reran `npm run dev` to bring it back up. Instead it died immediately with this:

```text
node:events:495
      throw er; // Unhandled 'error' event
      ^

Error: listen EADDRINUSE: address already in use :::3000
    at Server.setupListenHandle [as _listen2] (node:net:1740:16)
    at listenInCluster (node:net:1788:12)
    at Server.listen (node:net:1876:7)
    at Function.listen (/home/user/api/node_modules/express/lib/application.js:635:24)
    at Object.<anonymous> (/home/user/api/src/index.js:42:10)
Emitted 'error' event on Server instance at:
    at emitErrorNT (node:net:1923:8)
    at process.processTicksAndRejections (node:internal/process/task_queues.js:83:21) {
  code: 'EADDRINUSE',
  errno: -98,
  syscall: 'listen',
  address: '::',
  port: 3000
}
```

The code hadn't changed except for one controller file, and the port number in the source was still 3000, same as always. I couldn't figure out why the OS was suddenly saying it was already in use.

## Environment

- OS: Windows 11 23H2 + WSL2 (Ubuntu 22.04.3 LTS)
- Node.js: v20.11.1
- npm: 10.2.4
- Framework: Express 4.19.2 + nodemon 3.1.0
- Editor: VSCode (terminal via the WSL Remote extension)

## What I Tried

My first assumption was that closing the VSCode terminal tab (clicking the trash-can icon) would kill whatever process was running in it. I closed the tab, opened a fresh one, and ran the dev command again.

```bash
npm run dev
```

```text
Error: listen EADDRINUSE: address already in use :::3000
```

Same error, unchanged. Closing a terminal tab doesn't guarantee that every child process spawned from that shell — in this case the actual node process forked by nodemon — gets terminated with it. The previous crash had come from an unhandled exception inside an async controller, and it happened before nodemon's watch-restart cycle could kick in, leaving the old node process holding port 3000 as a zombie.

Next I checked for lingering node processes with `ps aux`.

```bash
ps aux | grep node
```

```text
user      1823  0.3  1.2 923456 48120 ?        Sl   21:02   0:02 node src/index.js
user      2941  0.0  0.0  17456  1092 pts/3    S+   21:14   0:00 grep node
```

The second line was just the `grep` command matching itself. PID 1823 was the real culprit — a node process that had survived after I'd already closed its terminal tab.

## Why This Happens

Only one process can bind a given TCP port at a time. When Node.js calls `Server.listen()`, it asks the OS to reserve that port; if another process already has it bound, the OS refuses the request and Node.js throws `EADDRINUSE` (address already in use) and exits. In this case, the earlier crash meant nodemon's child process never received a clean SIGTERM, so closing the parent shell or terminal tab only detached it — the orphaned process kept running in the background, still holding port 3000. Every new process I tried to start failed to bind for the same reason, over and over.

## Solution

### 1. Find the process holding the port

```bash
sudo lsof -i :3000
```

```text
COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
node    1823 user   20u  IPv6  34521      0t0  TCP *:3000 (LISTEN)
```

`lsof -i :<port>` lists whichever process actually holds that port in a LISTEN state. Here it pointed straight at PID 1823.

### 2. Kill that process

```bash
kill -9 1823
```

```bash
sudo lsof -i :3000
```

After this, `lsof` returned nothing, confirming the port was free again. `kill -9` sends SIGKILL, which gives the process no chance to clean up — useful exactly when a process is detached from its parent shell and no longer responds to a normal termination signal.

### 3. Start the dev server again

```bash
npm run dev
```

```text
[nodemon] starting `node src/index.js`
Server listening on port 3000
```

With the port free, Node's `Server` could bind successfully and the app came up.

## Gotchas

- Closing a terminal tab doesn't reliably kill everything that was running in it — I only found the orphaned process by explicitly checking with `ps aux`.
- I first tried plain `kill 1823` (SIGTERM, no signal number), but the process was stuck mid-async and ignored it entirely — it was still showing up in `lsof` several seconds later. It only went away once I sent SIGKILL with `kill -9`.
- Windows Task Manager, running on the host side, never showed the process at all — since it was a WSL2 process, it was only visible from inside WSL via `ps`.
- Part of the problem was self-inflicted: my nodemon config had the edited file listed under `ignore`, so the auto-restart never fired after my change, and the old process just kept running untouched.

## FAQ

**Q: How do I find the process holding a port on native Windows (no WSL2)?**
Run `netstat -ano | findstr :3000` in PowerShell to get the port and its PID, then `taskkill /PID <PID> /F` to force-kill it. The command set is different from `lsof`/`kill` inside WSL2, so don't mix them up.

**Q: Manually killing the process every time is tedious. Is there a way to automate it?**
Running `npx kill-port 3000` finds and kills whatever is bound to that port automatically. Wiring it into a `predev` npm script means the port gets freed every time before `npm run dev` runs, without any manual step.

**Q: I get the same error running a container with Docker Compose. Is the cause the same?**
The underlying mechanism is identical, but with Docker it's usually a conflicting host port mapping (`ports: - "3000:3000"`) rather than a stray process. Check `docker ps` for another container already publishing the same port, and stop it with `docker compose down` if it's not needed.

## Related Articles

- [How to Kill a Process on Linux with the kill Command](/en/linux-kill-command)
- [How to Check Port and File Usage on Linux with lsof](/en/linux-lsof-command)
- [How to Fix "Port Is Already Allocated" in Docker](/en/docker-port-already-in-use)
- [How to Manage a Node.js Process with pm2](/en/node-pm2-setup)
- [Basic Windows Terminal Setup](/en/windows-terminal-setup)
