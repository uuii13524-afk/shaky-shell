---
title: 'How to Fix nginx 403 Forbidden Error'
date: '2026-07-20'
category: 'nginx'
layout: '../../layouts/PostLayoutEn.astro'
description: 'nginx returns 403 Forbidden though index.html is 644. Cause: a missing execute bit on /home/deploy, found via namei -l and fixed with chmod o+x.'
en_tags: ['nginx', '403', 'forbidden', 'permission', 'linux']
---

## What I Was Trying to Do

I reconfigured nginx on a VPS to serve a static site, and suddenly every request — from the browser and from curl — came back with 403 Forbidden. The config was a copy of one that had been working fine the day before, so I had no idea where to even start, and I ended up rereading the same server block for nearly an hour.

```text
$ curl -I https://example.com/
HTTP/1.1 403 Forbidden
Server: nginx/1.24.0
Date: Mon, 20 Jul 2026 09:12:03 GMT
Content-Type: text/html
Content-Length: 153
Connection: keep-alive
```

---

## Environment

- OS: Ubuntu 22.04 LTS (Sakura VPS)
- nginx: 1.24.0 (Ubuntu's stock package)
- Deploy method: `rsync` pushing a prebuilt static bundle to `/var/www/example.com/html`
- Running as: a non-root deploy user, `deploy`

---

## What I Tried

Since 403 usually means a permissions problem, I first suspected the `root` path itself and ran `ls -la` on the directory → the file was there and looked fine → so a wrong path wasn't the issue, which left me stuck on what actually was.

```bash
ls -la /var/www/example.com/html
```

```text
total 12
drwxr-xr-x 2 deploy deploy 4096 Jul 20 09:00 .
drwxr-xr-x 3 deploy deploy 4096 Jul 19 22:10 ..
-rw-r--r-- 1 deploy deploy  612 Jul 20 09:00 index.html
```

Next, after confirming `index.html` itself was `644` and readable, I just restarted nginx and tried again — still 403. That's when it clicked that the file's own permissions were fine and something else in the path was blocking access.

```bash
systemctl restart nginx
curl -I https://example.com/
```

```text
HTTP/1.1 403 Forbidden
```

---

## Root Cause

For nginx to serve a file, it's not enough for the file itself to be readable — every ancestor directory on the way to it needs the execute bit (`x`) set for whichever user nginx runs as, usually `www-data`. In this case the deploy script had rsynced into a path under the deploy user's home directory, `/home/deploy/www`, and `/home/deploy` itself still had its default `750` permissions. `www-data` couldn't traverse into that directory at all, so it never even reached the file. Checking only the file's own permissions completely missed this.

---

## The Fix

### Walk the whole path with namei

```bash
namei -l /var/www/example.com/html/index.html
```

```text
f: /var/www/example.com/html/index.html
drwxr-xr-x root     root     /
drwxr-xr-x root     root     var
drwxr-xr-x root     root     www
drwxr-xr-x deploy   deploy   example.com
drwxr-xr-x deploy   deploy   html
-rw-r--r-- deploy   deploy   index.html
```

`namei -l` prints the permissions and ownership of every directory from the root down to the target file in one go. In this deploy, `/var/www` itself was fine — the actual gap was in a separate `/home/deploy/www` setup used on a staging box.

### Add the execute bit on the blocking directory

```bash
chmod o+x /home/deploy
```

```text
(no output — confirmed with namei -l afterward: 750 became 755)
```

The directory execute bit (`x`) means "permission to enter this directory and look up entries inside it," which is independent of the write bit. Adding just `o+x` is enough to let nginx traverse the directory without also letting other users write to it.

### Confirm the cause in the error log

```bash
tail -n 5 /var/log/nginx/error.log
```

```text
2026/07/20 09:11:58 [error] 812#812: *3 open() "/home/deploy/www/index.html" failed (13: Permission denied), client: 203.0.113.5, server: example.com, request: "GET / HTTP/1.1"
```

Seeing `(13: Permission denied)` confirms it's a permissions issue rather than a bad path (which would show `is not found` instead). Checking this log first would have saved the detour of second-guessing the `root` path.

---

## Where I Got Tripped Up

- I checked `index.html`'s own permissions with `ls -la`, saw they looked fine, and stopped there — completely missing that the ancestor directories mattered just as much. That cost me over 30 minutes.
- The public directory lived under a home directory (`/home/deploy/www`), and Ubuntu's default `750` on home directories was still in place, blocking `www-data` from reading anything under it.
- I almost ran `chmod -R 755` on the target directory itself, which wouldn't have fixed anything — the blocking directory was further up the tree, so each ancestor needed `o+x` individually.
- I kept restarting nginx before ever looking at the error log, which just wasted time without giving me any new information.

---

## FAQ

**Q: What's the difference between nginx 403 Forbidden and a missing index.html?**
403 means nginx confirmed the file exists but was denied access to it; a missing file instead produces 404. The error log spells out which one you're dealing with — `Permission denied` points to a 403-style permissions issue, while `No such file or directory` points to a 404-style path problem.

**Q: What about the "directory index of ... is forbidden" error?**
That happens when `autoindex` is off and a directory has no `index.html` for nginx to fall back to, so it refuses to list the directory contents instead. That's a missing-index-file issue, not a permissions issue — check with `ls` whether `index.html` actually exists in that directory before touching permissions.

**Q: Does this happen if I keep everything under /var/www?**
It's less likely, since `/var/www` and its parents are usually `755` by default. The trouble mostly shows up when you serve files from inside a home directory like `/home/username/...`, because Ubuntu's default home directory permission of `750` blocks `www-data` from traversing it. Keeping public content under `/var/www` avoids this entirely, and it also matches the paths most tutorials and package defaults already assume, so there's less custom configuration to get wrong later.

---

## Related Articles

- [nginx 404 Not Found: Causes and How to Fix It](/en/nginx-404-not-found)
- [nginx 502 Bad Gateway: Causes and How to Fix It](/en/nginx-502-bad-gateway)
- [nginx Basic Configuration File Guide](/en/nginx-basic-config)
- [nginx location Directives Explained](/en/nginx-location-directives)
- [Linux File Permissions Guide (chmod/chown)](/en/linux-file-permissions)
