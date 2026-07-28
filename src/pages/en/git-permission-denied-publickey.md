---
title: 'Fix "git@github.com: Permission denied (publickey)" on git clone/push'
date: '2026-07-28'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'How to fix "git@github.com: Permission denied (publickey)" when running git clone, git pull, or git push over SSH, including missing ssh-agent keys and wrong key selection.'
en_tags: ['Git', 'GitHub', 'SSH', 'Permission denied', 'publickey']
---

## What I Was Trying to Do

I'd set up a new laptop, cloned a couple of HTTPS repos without issue, then switched one of them to the SSH remote so I could push without typing a token every time. The very next `git push` refused to authenticate.

```text
$ git push origin main
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

## Environment

- OS: Ubuntu 24.04
- Git: 2.43.0
- SSH client: OpenSSH_9.6p1
- Remote: `git@github.com:example/myrepo.git`

## What I Tried

My first assumption was that GitHub simply didn't have a key for this machine yet, so I checked what SSH actually had loaded.

```bash
ssh-add -l
```

```text
The agent has no identities.
```

That confirmed the agent was empty. I did have an SSH key on disk from a previous project, so I checked for it directly.

```bash
ls -la ~/.ssh
```

```text
-rw-------  1 acia acia  411 Jul 28 09:02 id_ed25519
-rw-r--r--  1 acia acia   99 Jul 28 09:02 id_ed25519.pub
```

The key file existed, but `ssh-add -l` still showed nothing — the agent wasn't holding it, and Git had no way to present it during authentication.

## Why This Happens

`git@github.com: Permission denied (publickey)` means the SSH handshake completed, but none of the keys offered were accepted by GitHub for that account. There are three common causes:

1. **No key loaded in the agent.** Having a key file in `~/.ssh` doesn't mean SSH will use it automatically — the running `ssh-agent` has to hold it, or `ssh` has to be told about it explicitly.
2. **The key was never added to the GitHub account.** The public key (`.pub` file) has to be registered under GitHub → Settings → SSH and GPG keys, matching the account that owns (or has access to) the repository.
3. **The wrong key gets offered when multiple keys exist.** If several key pairs exist on the machine, SSH may try them in the wrong order or default to one that isn't registered anywhere, and GitHub rejects every offer.

## Solution

### 1. Confirm it's actually an SSH/key problem, not a permissions problem on GitHub

```bash
ssh -T git@github.com
```

```text
git@github.com: Permission denied (publickey).
```

A successful setup replies with `Hi <username>! You've successfully authenticated...`, so seeing `Permission denied` here isolates the issue to SSH authentication itself, before Git is even involved.

### 2. Start the agent and add the key

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

```text
Agent pid 4821
Identity added: /home/acia/.ssh/id_ed25519 (acia@laptop)
```

```bash
ssh-add -l
```

```text
256 SHA256:9fKq...redacted... acia@laptop (ED25519)
```

### 3. Make sure the matching public key is registered on GitHub

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the full output (starts with `ssh-ed25519` and ends with the comment) and add it under GitHub → Settings → SSH and GPG keys → New SSH key. If the key was already added under a different GitHub account than the one with access to the repository, that's the same symptom — check which account the key is registered under.

### 4. Re-test and retry

```bash
ssh -T git@github.com
```

```text
Hi acia! You've successfully authenticated, but GitHub does not provide shell access.
```

```bash
git push origin main
```

```text
Enumerating objects: 5, done.
...
To github.com:example/myrepo.git
   a1b2c3d..e4f5g6h  main -> main
```

Once `ssh -T` returns the "successfully authenticated" message, `git push`/`git pull`/`git clone` over SSH work the same way.

### 5. If multiple keys are involved, pin the right one per host

When more than one key exists (for example a personal key and a work key), add an explicit mapping in `~/.ssh/config` instead of relying on SSH to guess correctly.

```text
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

`IdentitiesOnly yes` stops SSH from offering every key in the agent and forces it to use only the one listed, which avoids GitHub rejecting the connection after too many failed offers.

## Gotchas

- `ssh-add` only holds keys for the current agent session — after a reboot, `ssh-add -l` goes back to "no identities" unless the agent is started automatically (most desktop Linux/macOS setups do this already; a fresh server shell often doesn't).
- If `~/.ssh/id_ed25519` has looser permissions than `600`, SSH silently refuses to use it without a clear error pointing at permissions — `chmod 600 ~/.ssh/id_ed25519` fixes that class of failure.
- Registering the key under the wrong GitHub account (a work account instead of a personal one, or vice versa) produces the exact same `Permission denied (publickey)` message — there's no separate error for "wrong account."

## FAQ

**Q: Does switching the remote back to HTTPS avoid this entirely?**
Yes — `git remote set-url origin https://github.com/example/myrepo.git` sidesteps SSH key setup, at the cost of authenticating with a token/credential helper on each push instead of a key.

**Q: `ssh -T git@github.com` works, but `git push` still fails — why?**
That usually means the key that authenticates fine doesn't have push access to that specific repository (registered to a different account, or added as a read-only deploy key). Check which account the key belongs to and whether that account has write access.

**Q: How do I tell which key SSH is actually offering?**
Run `ssh -vT git@github.com` and look for the `Offering public key` lines in the verbose output — it shows exactly which key file was tried and whether GitHub accepted or rejected it.

## Related Articles

- [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github/)
- [How to Fix a Rejected Git Push (Non-Fast-Forward)](/en/git-push-rejected-fix/)
- [How to Push to GitHub for the First Time](/en/github-first-push/)
- [Git Remote Repository Operations (remote/fetch/pull/push)](/en/git-remote-operations/)
- [Fix "fatal: not a git repository (or any of the parent directories): .git"](/en/git-fatal-not-a-git-repository/)
