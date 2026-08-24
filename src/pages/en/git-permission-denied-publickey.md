---
title: 'Fix: git clone Fails with "Permission denied (publickey)" on a Fresh VPS (Ubuntu 24.04)'
date: '2026-08-24'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'On a freshly provisioned VPS, git clone fails immediately with "Permission denied (publickey)". Here is how to trace it to an overly permissive private key file and fix it with chmod and ssh-agent.'
en_tags: ['Git', 'SSH', 'Permission denied']
---

## What I Was Trying to Do

I had just provisioned a new Ubuntu 24.04 VPS and wanted to clone a private repository onto it for deployment. I copied over the same SSH key I already used on my local machine.

```bash
git clone git@github.com:example-org/deploy-target.git
```

It failed immediately with this error:

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

Since the exact same repository cloned and pushed fine from my local machine, my first guess was that my GitHub access to the repo had somehow been revoked, so I went to check the repository settings first.

## Environment

- OS: Ubuntu 24.04 LTS (freshly provisioned VPS)
- Git: 2.43.0 (Ubuntu 24.04's default package)
- OpenSSH: 9.6p1
- SSH key: ed25519, generated locally and copied over to the VPS
- GitHub account: personal account with access to the organization's private repo

## What I Tried

I checked "Settings > Collaborators" on GitHub first, and my account clearly had access. Next I compared the HTTPS and SSH clone URLs for typos, but the SSH URL I was using was correct too.

At that point I stopped suspecting the repository itself and tested the raw SSH connection using GitHub's own connectivity check command.

```bash
ssh -T git@github.com
```

```text
git@github.com: Permission denied (publickey).
```

The exact same error showed up even without Git in the picture at all. That confirmed the problem was in SSH authentication, not in anything on GitHub's side.

To narrow it down further, I re-ran the same command with verbose logging.

```bash
ssh -vT git@github.com
```

```text
debug1: Offering public key: /root/.ssh/id_ed25519 ED25519 SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
debug1: Authentications that can continue: publickey
debug1: No more authentication methods to try.
git@github.com: Permission denied (publickey).
```

The key was found and offered, but authentication never succeeded. Since the key content itself looked intact, I checked the file permissions next.

```bash
ls -la ~/.ssh/
```

```text
-rw-r--r-- 1 root root  411 Aug 24 09:12 id_ed25519
-rw-r--r-- 1 root root  100 Aug 24 09:12 id_ed25519.pub
```

The private key `id_ed25519` had permissions `644` (`-rw-r--r--`). Copying it from my local machine over `scp` didn't preserve the original mode — the VPS's default umask overwrote it on write.

## Root Cause

OpenSSH's client silently refuses to use a private key file if its permissions are too permissive (readable by group or other users) — this is a deliberate security behavior. Critically, it doesn't say "permission is the problem" anywhere in the error output. GitHub itself only ever replies with the generic "Permission denied (publickey)", which makes it very easy to go chasing the key's contents or the GitHub-side configuration instead.

Even the `ssh -v` debug log still shows "Offering public key" — the client attempted to present the key — but the local permission check happens separately and doesn't produce an obvious message at that verbosity level. I had to go up to circumstantial evidence (checking `ls -la` directly) to pin down the actual cause.

A private key needs mode `600` (read/write for the owner only), and the `.ssh` directory itself needs `700`. In this case, the VPS's umask (`022`) was applied during the `scp` transfer, which downgraded the key's permissions to `644` in the process.

## How I Fixed It

### 1. Fix the permissions on `.ssh` and the private key

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

The private key should be readable and writable only by its owner (`600`). The public key can stay world-readable (`644`) — that's fine.

### 2. Confirm the permissions took effect

```bash
ls -la ~/.ssh/
```

```text
drwx------ 2 root root 4096 Aug 24 09:12 .
-rw------- 1 root root  411 Aug 24 09:12 id_ed25519
-rw-r--r-- 1 root root  100 Aug 24 09:12 id_ed25519.pub
```

`id_ed25519` now shows `-rw-------` (600), as expected.

### 3. Register the key with ssh-agent

A fresh VPS usually doesn't have `ssh-agent` running by default, so I started it explicitly and added the key.

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

```text
Agent pid 3241
Identity added: /root/.ssh/id_ed25519 (deploy@vps)
```

### 4. Re-test the SSH connection

```bash
ssh -T git@github.com
```

```text
Hi example-user! You've successfully authenticated, but GitHub does not provide shell access.
```

"successfully authenticated" confirmed that auth was now working.

### 5. Clone again

```bash
git clone git@github.com:example-org/deploy-target.git
```

```text
Cloning into 'deploy-target'...
remote: Enumerating objects: 142, done.
remote: Counting objects: 100% (142/142), done.
remote: Compressing objects: 100% (98/98), done.
remote: Total 142 (delta 31), reused 120 (delta 18), pack-reused 0
Receiving objects: 100% (142/142), 1.02 MiB | 3.14 MiB/s, done.
Resolving deltas: 100% (31/31), done.
```

The clone completed without any errors.

## Verify It Works

Manually running `ssh-add` on every deploy isn't realistic, so I checked whether the fix would survive a VPS reboot.

```bash
ssh-add -l
```

```text
The agent has no identities.
```

As expected, the agent's registration was gone after a reboot. As a permanent fix, I added auto-registration to `~/.bashrc` and re-checked after logging back in.

```bash
grep -A2 "ssh-agent" ~/.bashrc
```

```text
eval "$(ssh-agent -s)" > /dev/null
ssh-add ~/.ssh/id_ed25519 2>/dev/null
```

```bash
ssh-add -l
```

```text
256 SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx deploy@vps (ED25519)
```

After logging back in, the key was registered automatically, and `git clone` / `git pull` both worked without any manual key entry.

## Takeaways

- "Permission denied (publickey)" doesn't only mean a corrupted or wrong key — an **overly permissive private key file fails with the exact same message**. The error text alone can't tell you which.
- When copying an SSH key to another machine with `scp` or `rsync`, the destination's umask can silently change its permissions. Always check with `ls -la ~/.ssh/` afterward — the private key needs `600`, and the `.ssh` directory needs `700`.
- Diagnose with `ssh -T git@github.com` (add `-v` if needed) instead of `git clone` directly — it quickly tells you whether the problem is on GitHub's side (repo access) or in local SSH authentication.

## FAQ

**Q: The `ssh -v` log shows "Offering public key" — why does it still fail?**
Offering a key as a candidate and that key actually being accepted as valid are two separate things. A key with overly permissive file permissions can get rejected locally before authentication even reaches GitHub, and standard `-v` verbosity often doesn't spell that out directly. Checking permissions with `ls -la` is the reliable way to confirm it.

**Q: How do I avoid forgetting to `chmod` every time?**
`ssh-keygen` itself always creates a private key with mode `600` from the start. Permissions usually get broken later, when the key is moved between machines via `scp`, `rsync`, or an archive tool like `tar`/`zip`. Get in the habit of running `ssh -T git@github.com` right after any such transfer, and you'll catch it early.

**Q: Re-running `ssh-add` after every VPS reboot is annoying.**
Adding the `ssh-agent` startup and `ssh-add` call to `~/.bashrc` or `~/.profile` registers the key automatically on every login. For a dedicated deploy user, explicitly pointing to the key path in `~/.ssh/config` also works well.

## Related Articles

- [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github)
- [Managing SSH Connection Settings with the SSH Config File](/en/ssh-config-file)
- [Fixing a Rejected git push](/en/git-push-rejected-fix)
- [Linux File Permissions Basics (chmod/chown)](/en/linux-file-permissions)
- [How to Create a GitHub Repository and Push for the First Time](/en/github-first-push)
