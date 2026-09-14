---
title: 'Fix "git@github.com: Permission denied (publickey)" on a New Ubuntu Machine'
date: '2026-09-14'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'On a freshly installed Ubuntu 24.04 machine, git push fails with "Permission denied (publickey)" even for an existing GitHub account. Here is how ssh -vT pinpoints the cause and how registering the new key on GitHub fixes it.'
en_tags: ['Git', 'SSH', 'GitHub', 'publickey']
---

## What I Was Trying to Do

I was migrating my dev setup from my desktop to a new mini PC with a fresh install of Ubuntu 24.04. After setting things up, I tried to clone an existing repo and it failed with an authentication error.

```bash
git clone git@github.com:example-org/internal-tools.git
```

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

I'd been connecting to the same GitHub account from my old desktop for years without issue, so my first guess was a temporary GitHub outage. I waited a bit and tried again. Same result.

```bash
git clone git@github.com:example-org/internal-tools.git
```

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

## Environment

- OS: Ubuntu 24.04.1 LTS (fresh install on a mini PC)
- Git: 2.43.0
- OpenSSH: 9.6p1
- Key type: ed25519 (newly generated with `ssh-keygen -t ed25519`)
- GitHub account: an existing account I've used for years from my old desktop

## What I Tried

First I checked the contents of `~/.ssh`.

```bash
ls -la ~/.ssh
```

```text
total 20
drwx------ 2 dev dev 4096 Sep 14 09:12 .
drwxr-x--- 15 dev dev 4096 Sep 14 09:10 ..
-rw------- 1 dev dev  411 Sep 14 09:12 id_ed25519
-rw-r--r-- 1 dev dev  102 Sep 14 09:12 id_ed25519.pub
```

I remembered running `ssh-keygen -t ed25519 -C "dev@example.com"` while setting up this machine, and the key pair was right there. Permissions were `600`/`644`, nothing obviously wrong. I suspected a permissions issue at first and re-ran `chmod 600 ~/.ssh/id_ed25519`, but nothing changed.

Next I checked whether the key was actually loaded into the agent with `ssh-add -l`.

```bash
ssh-add -l
```

```text
2048 SHA256:9fK3l... /home/dev/.ssh/id_rsa (RSA)
```

The only identity listed was an old RSA key I'd copied over from the old desktop with `rsync`. The new `id_ed25519` hadn't been added to the agent at all. I added it and tried again.

```bash
ssh-add ~/.ssh/id_ed25519
git clone git@github.com:example-org/internal-tools.git
```

```text
Identity added: /home/dev/.ssh/id_ed25519 (dev@example.com)
```

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

Adding the key to the agent didn't change anything either. At this point I'd ruled out the key file itself and the agent registration, so I moved on to checking the SSH connection with verbose logging.

```bash
ssh -vT git@github.com
```

The tail of the output looked like this.

```text
debug1: Offering public key: /home/dev/.ssh/id_ed25519 ED25519 SHA256:8pQmZ...
debug1: Authentications that can continue: publickey
debug1: Offering public key: /home/dev/.ssh/id_rsa RSA SHA256:9fK3l...
debug1: Authentications that can continue: publickey
debug1: No more authentication methods to try.
git@github.com: Permission denied (publickey).
```

This showed that the client was correctly offering both `id_ed25519` and `id_rsa` (`Offering public key`). GitHub was rejecting both anyway — meaning the keys were being transmitted correctly, but GitHub simply didn't recognize either public key.

## Root Cause

Running `ssh-keygen` on the new mini PC only generated a key pair locally. I had never actually added the resulting public key (`id_ed25519.pub`) to this GitHub account's "SSH and GPG keys" settings.

GitHub authenticates SSH connections purely against the list of public keys explicitly registered on the account — not against the machine's identity or how long the account has been used. So the fact that I'd connected from the same account for years on the old desktop was completely irrelevant to authenticating a new machine with a newly generated key pair. Every time you set up a new machine or regenerate a key (say, after a clean OS install), you need to register that machine's public key with GitHub again.

The pattern in the `ssh -vT` log — keys being offered but every one rejected — is the classic signature of "the client is behaving correctly, the server just doesn't have this key on its allow list."

## How I Fixed It

### 1. Get the new machine's public key

```bash
cat ~/.ssh/id_ed25519.pub
```

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN2q... dev@example.com
```

I copied this single line as-is.

### 2. Register the public key on GitHub

I logged into GitHub in the browser, went to `Settings > SSH and GPG keys > New SSH key`, gave it a title that identified the machine (`mini-pc-2026`), pasted the public key from step 1 into the Key field, and saved it.

### 3. Re-test the SSH connection

```bash
ssh -T git@github.com
```

```text
Hi devuser! You've successfully authenticated, but GitHub does not provide shell access.
```

That message confirmed authentication succeeded.

### 4. Retry the clone

```bash
git clone git@github.com:example-org/internal-tools.git
```

```text
Cloning into 'internal-tools'...
remote: Enumerating objects: 842, done.
remote: Counting objects: 100% (842/842), done.
remote: Compressing objects: 100% (401/401), done.
remote: Total 842 (delta 398), reused 812 (delta 380), pack-reused 0
Receiving objects: 100% (842/842), 1.2 MiB | 4.8 MiB/s, done.
Resolving deltas: 100% (398/398), done.
```

It cloned cleanly.

### 5. Clean up the leftover old RSA key

The `id_rsa` key I'd copied from the old desktop wasn't needed for this repo, so to avoid future confusion I pinned which key gets used per host in `~/.ssh/config`.

```bash
# ~/.ssh/config
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

`IdentitiesOnly yes` makes SSH offer only the specified key, even if the agent has multiple identities loaded.

## Verify It Works

After editing `~/.ssh/config`, I cleared the agent entirely and re-tested the connection just to be safe.

```bash
ssh-add -D
ssh -T git@github.com
```

```text
Identity removed: /home/dev/.ssh/id_ed25519 (dev@example.com)
Identity removed: /home/dev/.ssh/id_rsa (RSA)
All identities removed.
Hi devuser! You've successfully authenticated, but GitHub does not provide shell access.
```

Even with an empty agent, the `IdentityFile` directive alone was enough to offer `id_ed25519` and authenticate successfully. I then tried `git push` on an existing working repo, and that went through cleanly too.

```bash
cd internal-tools
git push origin main
```

```text
Everything up-to-date
```

## Takeaways

- A GitHub account you've used for years elsewhere doesn't help a new machine authenticate. Every new machine or newly generated key pair needs its public key registered on the account separately — having the key file, correct permissions, or an agent entry is not enough on its own.
- If `ssh -vT git@github.com` shows `Offering public key` entries followed by `Permission denied (publickey)`, the client is behaving correctly and the problem is almost always an unregistered public key on the server side.
- When juggling multiple keys, set `IdentityFile` and `IdentitiesOnly yes` per host in `~/.ssh/config` to avoid the wrong key being offered first and rejected. The same verbose-logging approach generalizes to other "the key is right there but it won't connect" situations.

## FAQ

**Q: Could I have used HTTPS with a Personal Access Token instead?**
Yes. You can switch the remote to an HTTPS URL with `git remote set-url origin https://github.com/example-org/internal-tools.git` and authenticate with a Personal Access Token. That said, it means entering or managing a stored token on every push, so registering an SSH key is usually less friction on a machine you use regularly.

**Q: Is it safe to register multiple public keys on one GitHub account?**
Yes, that's expected and officially supported — registering a separate key per machine is the recommended practice. When you retire or replace a machine, remove its key from the Settings page.

**Q: Wouldn't plain `ssh -T` have told me the same thing?**
`ssh -T git@github.com` only reports `Permission denied (publickey)` — it doesn't tell you whether the key is unregistered, never loaded into the agent, or simply being shadowed by a different key. Adding `-v` (or `-vvv` for more detail) and reading the `Offering public key` lines is what lets you tell client-side and server-side causes apart.

## Related Articles

- [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github)
- [How to Create a GitHub Repository and Push for the First Time](/en/github-first-push)
- [Fix "rejected" When Running git push](/en/git-push-rejected-fix)
- [How to Write an SSH Config File (~/.ssh/config)](/en/ssh-config-file)
- [Installing Ubuntu on WSL2](/en/wsl2-install-windows)

## Recommended VPS / Cloud Hosting
Looking for developer-friendly infrastructure to deploy what you just fixed? These providers are solid choices for production workloads.
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - managed cloud hosting with one-click stacks.
- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - bare-metal and VPS optimized for demanding workloads.
