---
title: 'Fix: git push Fails with "Permission denied (publickey)" in WSL2 (Ubuntu 24.04)'
date: '2026-08-11'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git push and git clone fail with "Permission denied (publickey)" inside WSL2 Ubuntu even though the SSH key is already registered on GitHub. Here is how loose private key file permissions silently disable the key, and how to fix it with chmod.'
en_tags: ['Git', 'SSH', 'WSL2', 'permission denied']
---

## What I Was Trying to Do

I set up a new Windows 11 machine and wanted to keep working on an existing GitHub repo from WSL2 Ubuntu. I zipped up the `.ssh` folder from the old machine's `C:\Users\me\.ssh` in Windows Explorer, unzipped it into `~/.ssh` inside WSL2, and then ran a normal push.

```bash
cd ~/projects/errsolved
git push origin main
```

It was rejected with an error I hadn't seen before.

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

Testing the SSH connection on its own failed the same way.

```bash
ssh -T git@github.com
```

```text
git@github.com: Permission denied (publickey).
```

The key was already registered on GitHub, and the exact same key worked fine from Git Bash on Windows. I didn't expect a plain file copy to break anything, so it took a while to narrow down.

## Environment

- OS: Windows 11 23H2 / WSL2 Ubuntu 24.04.1 LTS
- Git: 2.43.0
- OpenSSH client: 9.6p1
- Key type: `ed25519` (`id_ed25519` / `id_ed25519.pub`)
- How the key got there: zipped the Windows `.ssh` folder, extracted it inside WSL2

## What I Tried

My first guess was that the key wasn't actually registered on GitHub, so I compared the public key contents character by character against what was listed under `Settings > SSH and GPG keys`. They matched exactly, so the key content itself wasn't the problem.

Next I checked whether the SSH agent even had the key loaded.

```bash
ssh-add -l
```

```text
The agent has no identities.
```

Nothing was loaded, so I added it explicitly.

```bash
ssh-add ~/.ssh/id_ed25519
```

```text
Identity added: /home/me/.ssh/id_ed25519 (me@example.com)
```

That looked successful, but running `ssh -T git@github.com` again still returned the same `Permission denied (publickey)`. The fact that `ssh-add` reported success while authentication kept failing was odd enough that I switched to verbose logging.

```bash
ssh -vT git@github.com
```

Buried in the output was a warning I'd missed at a glance.

```text
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0644 for '/home/me/.ssh/id_ed25519' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "/home/me/.ssh/id_ed25519": bad permissions
git@github.com: Permission denied (publickey).
```

OpenSSH was explicitly stating that the file was readable by others and was being ignored for safety. The key content and its GitHub registration were both fine — file permissions alone were silently knocking it out of the authentication process.

## Root Cause

Checking the actual permissions with `ls -la` made the cause obvious.

```bash
ls -la ~/.ssh
```

```text
drwxr-xr-x  2 me me 4096 Aug 11 09:02 .
-rw-r--r--  1 me me  411 Aug 11 09:02 id_ed25519
-rw-r--r--  1 me me  103 Aug 11 09:02 id_ed25519.pub
```

The private key `id_ed25519` was `644` (readable by group and other), and the `.ssh` directory itself was `755`. Extracting a zip created on Windows doesn't map Windows ACLs onto proper Unix permission bits, so everything came out at the default `644` instead.

OpenSSH refuses to use a private key file if it's readable by anyone other than its owner — that's a deliberate safeguard against key theft. It doesn't raise an error for this; it just silently drops the key from the list of candidates. That's why `ssh-add` reported success (it can still read and load the file) while the actual SSH handshake never offered the key at all.

## How I Fixed It

### 1. Fix permissions on the `.ssh` directory and key files

The private key should be owner-read/write only (`600`), the public key `644`, and the directory `700`.

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

### 2. Confirm the permissions changed

```bash
ls -la ~/.ssh
```

```text
drwx------  2 me me 4096 Aug 11 09:14 .
-rw-------  1 me me  411 Aug 11 09:14 id_ed25519
-rw-r--r--  1 me me  103 Aug 11 09:14 id_ed25519.pub
```

### 3. Reload the key into the SSH agent

To avoid confusion from the earlier failed load, I re-added the key.

```bash
ssh-add ~/.ssh/id_ed25519
ssh-add -l
```

```text
256 SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx me@example.com (ED25519)
```

### 4. Re-test the GitHub connection

```bash
ssh -T git@github.com
```

```text
Hi myuser! You've successfully authenticated, but GitHub does not provide shell access.
```

Instead of `Permission denied`, I got the standard authentication-success message.

## Verify It Works

I re-ran `git push` and confirmed it reached the remote normally.

```bash
git push origin main
```

```text
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Writing objects: 100% (3/3), 312 bytes | 312.00 KiB/s, done.
To github.com:myuser/errsolved.git
   a1b2c3d..e4f5g6h  main -> main
```

I also re-checked `ssh -vT git@github.com` and confirmed the `bad permissions` warning no longer appeared.

## Takeaways

- `Permission denied (publickey)` doesn't always mean the key itself is wrong. If the private key file is readable by anyone other than the owner (e.g. `644`), OpenSSH silently ignores it entirely.
- A successful `ssh-add` doesn't guarantee the key is actually used — a key with bad permissions loads into the agent fine but still gets excluded when the real handshake happens. Running `ssh -vT git@github.com` and looking for a `bad permissions` warning is the reliable way to confirm this specific cause.
- The fix is `chmod 700 ~/.ssh` plus `chmod 600` on the private key and `chmod 644` on the public key. This shows up most often when `.ssh` is moved between Windows and WSL2 via zip extraction or manual copying through Explorer, since Windows ACLs don't translate cleanly into Unix permission bits. Get in the habit of running `ls -la ~/.ssh` right after any such migration.

## FAQ

**Q: `ssh-add -l` shows my key, so why does authentication still fail?**
`ssh-add` only needs to be able to read the key file to report success — that's a separate check from what the SSH client does at connection time. During the actual handshake, OpenSSH re-checks file permissions and drops any key that's readable by anyone other than the owner. So the key can appear "loaded" while never actually being offered to the server.

**Q: Does this only happen in WSL2, or on regular Linux servers too?**
It happens anywhere OpenSSH is used — this isn't a WSL2-specific quirk, it's standard OpenSSH client behavior. Restoring `.ssh` from a backup with `scp` or `rsync`, or copying a key out of another user's home directory, can trigger the exact same warning.

**Q: `chmod` didn't fix it for me — what else should I check?**
It's easy to fix the key file but forget the directory itself. If `~/.ssh` is still `755`, the warning can persist, so make sure `chmod 700 ~/.ssh` runs alongside the key file changes. If it's still failing after that, verify the public key registered on GitHub actually pairs with the private key you're using — regenerate it locally with `ssh-keygen -y -f ~/.ssh/id_ed25519` and compare the output directly.

## Related Articles

- [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github)
- [How to Fix a Rejected Git Push (Non-Fast-Forward)](/en/git-push-rejected-fix)
- [Fix "fatal: not a git repository (or any of the parent directories): .git"](/en/git-fatal-not-a-git-repository)
- [Linux File Permissions Guide (chmod/chown)](/en/linux-file-permissions)
- [How to Install Git on Windows and Configure It](/en/windows-git-install)
