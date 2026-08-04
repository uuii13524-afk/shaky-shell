---
title: 'Fix: SSH "Permission denied (publickey)" on a Fresh VPS'
date: '2026-08-04'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
description: 'SSH key-based login to a new VPS gets rejected with Permission denied (publickey) even though the key is correct. Here is how sshd StrictModes checks .ssh and authorized_keys permissions, and how to fix it.'
en_tags: ['SSH', 'Linux', 'VPS', 'permissions']
---

## What I Was Trying to Do

I set up a new VPS (Ubuntu 22.04) and tried to SSH in using an ed25519 key I'd generated locally. I hadn't used `ssh-copy-id` — instead I created `authorized_keys` by hand from the provider's browser-based console right after provisioning the server.

```bash
ssh -i ~/.ssh/id_ed25519_vps deploy@203.0.113.10
```

There was no password prompt at all — the connection was rejected outright.

```text
deploy@203.0.113.10: Permission denied (publickey).
```

I was confident the public key was pasted correctly into `authorized_keys`, and the private key path was right. Password authentication was already disabled on the server, so there was no fallback either.

## Environment

- Client: macOS 14.5 (local machine)
- Server: Ubuntu 22.04.4 LTS (freshly provisioned VPS)
- OpenSSH: client 9.6p1 / server 8.9p1
- Key type: ed25519 (generated with `ssh-keygen -t ed25519`)
- Login user: `deploy` (created via `adduser` from the console; `authorized_keys` placed manually)

## What I Tried

My first suspicion was the private key path or its local permissions, so I re-ran the connection with `-v` for verbose output.

```bash
ssh -v -i ~/.ssh/id_ed25519_vps deploy@203.0.113.10
```

```text
debug1: Offering public key: /Users/me/.ssh/id_ed25519_vps ED25519 SHA256:xxxxxxxx
debug1: Authentications that can continue: publickey
debug1: Trying private key: /Users/me/.ssh/id_ed25519_vps
debug1: Authentications that can continue: publickey
debug1: No more authentication methods to try.
deploy@203.0.113.10: Permission denied (publickey).
```

The client was clearly offering the key correctly (it got to `Offering public key`), so the problem wasn't on my end — the server was refusing it. I logged into the VPS console directly and checked `sshd`'s auth log.

```bash
sudo tail -n 20 /var/log/auth.log
```

```text
Aug  4 10:12:03 vps sshd[1842]: Authentication refused: bad ownership or modes for directory /home/deploy
Aug  4 10:12:03 vps sshd[1842]: Connection closed by authenticating user deploy 203.0.113.1 port 51422 [preauth]
```

That gave a concrete reason: `bad ownership or modes for directory /home/deploy`. I checked the actual permissions.

```bash
ls -ld /home/deploy /home/deploy/.ssh /home/deploy/.ssh/authorized_keys
```

```text
drwxrwxrwx 3 deploy deploy 4096 Aug  4 10:05 /home/deploy
drwxrwxrwx 2 deploy deploy 4096 Aug  4 10:06 /home/deploy/.ssh
-rw-rw-rw- 1 deploy deploy  103 Aug  4 10:07 /home/deploy/.ssh/authorized_keys
```

Creating `~/.ssh` and editing `authorized_keys` by hand from the console had left them with a loose umask, so they'd ended up world-writable (`777`/`666`).

## Root Cause

With `StrictModes yes` (the OpenSSH default), sshd verifies the ownership and permissions of the home directory, `.ssh` directory, and `authorized_keys` file before it will accept key-based authentication. If the group or other users have write access, sshd treats that as "someone other than the owner could rewrite `authorized_keys`" and refuses the login outright — regardless of whether the key itself is valid. In this case `/home/deploy` was `777`, `.ssh` was `777`, and `authorized_keys` was `666`, which tripped that check. Since the client-side key offer and log both looked correct, the issue was isolated to server-side permissions rather than the key itself.

This is easy to misdiagnose because the client-side debug output gives no hint that anything is wrong — `Offering public key` and `Trying private key` both look completely normal, and the failure only shows up as a generic `No more authentication methods to try`. The actual reason only surfaces in the server's own auth log, which most people don't think to check until they've already re-generated the key pair, double-checked the key's contents byte-for-byte, and confirmed the username is spelled correctly. All of that time is wasted if the real problem is a permission bit on the server side.

## How I Fixed It

### 1. Fix the home directory and .ssh permissions

I couldn't get in over SSH, so this had to be done from the console.

```bash
chmod 755 /home/deploy
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh
```

- `700`: only the owner can read, write, or enter the `.ssh` directory.
- `600`: only the owner can read or write `authorized_keys`.

### 2. Confirm the new permissions

```bash
ls -ld /home/deploy /home/deploy/.ssh /home/deploy/.ssh/authorized_keys
```

```text
drwxr-xr-x 3 deploy deploy 4096 Aug  4 10:20 /home/deploy
drwx------ 2 deploy deploy 4096 Aug  4 10:20 /home/deploy/.ssh
-rw------- 1 deploy deploy  103 Aug  4 10:20 /home/deploy/.ssh/authorized_keys
```

### 3. Watch the auth log while reconnecting

I opened a second console session to tail the log, then reconnected from my local machine.

```bash
# on the VPS console
sudo tail -f /var/log/auth.log
```

```bash
# on the local machine
ssh -i ~/.ssh/id_ed25519_vps deploy@203.0.113.10
```

## Verify It Works

The connection from my local machine succeeded with no password prompt.

```text
Welcome to Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-107-generic x86_64)
deploy@vps:~$
```

The server log also switched from `Authentication refused` to a successful login entry.

```text
Aug  4 10:24:11 vps sshd[1901]: Accepted publickey for deploy from 203.0.113.1 port 51501 ssh2: ED25519 SHA256:xxxxxxxx
```

## Takeaways

- `Permission denied (publickey)` doesn't always mean the key is wrong — sshd's `StrictModes` check can reject a perfectly valid key if the server-side permissions are too loose. Checking `sudo tail /var/log/auth.log` (or `/var/log/secure` on some distros) for the actual rejection reason is the fastest way to tell the two apart.
- A log line like `bad ownership or modes for directory` points at the home directory, `.ssh`, or `authorized_keys` permissions. The safe baseline is `700` for `.ssh` and `600` for `authorized_keys`.
- Creating `.ssh`/`authorized_keys` by hand from a provider's console is exactly the situation where a loose umask can silently leave them group- or world-writable. Using `ssh-copy-id` where possible avoids this, since it sets the correct permissions automatically.

## FAQ

**Q: Can I loosen `700`/`600` at all?**
`.ssh` at `750` and `authorized_keys` at `640` will sometimes still work, but any write access for group or other triggers `StrictModes` rejection. Stick to `700`/`600` unless you have a specific reason not to.

**Q: Can I just set `StrictModes no` to work around this?**
You can, but it's not recommended — it lets sshd accept keys even when `authorized_keys` is writable by someone other than the owner, which is a real security risk. Fixing the permissions is the safer option.

**Q: Does the home directory's own permissions matter too?**
Yes. If the home directory itself is group- or other-writable (e.g. `775`/`777`), sshd rejects the login with `bad ownership or modes for directory` even if `.ssh` and `authorized_keys` are correct. That was the actual root cause in this case.

## Related Articles

- [Adding an SSH Key to GitHub](/en/ssh-key-github)
- [Organizing SSH Connections with an SSH Config File](/en/ssh-config-file)
- [Linux File Permissions Basics](/en/linux-file-permissions)
- [Linux User Management Commands](/en/linux-user-management)
- [Setting Up Docker on a VPS](/en/vps-docker-setup)
