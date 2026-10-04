---
title: 'Fix: git status "fatal: detected dubious ownership in repository" (Git 2.43 / Ubuntu 24.04)'
date: '2026-10-04'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git status and git log stop with "fatal: detected dubious ownership in repository". Reproduced here: the cause is an owner mismatch, fixed with safe.directory or chown, plus why safe.directory "*" is risky.'
en_tags: ['Git', 'safe.directory', 'dubious ownership']
---

## What I Was Trying to Do

I wanted to check the state of a Git repository that lives in a directory created by a different user.

```bash
cd repo
git status
```

Instead of the usual status output, Git stopped with this:

```text
fatal: detected dubious ownership in repository at '/path/to/repo'
To add an exception for this directory, call:

	git config --global --add safe.directory /path/to/repo
```

`git log` failed the same way, with exit code 128. I briefly wondered whether the repository was corrupted, but `.git` was fine. The real cause was elsewhere. (`/path/to/repo` stands in for the real path; the message structure is exactly as printed.)

## Environment

Every output in this article comes from commands I actually ran in this environment.

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- Running as: root (uid=0)
- Repository owner: uid=1000, gid=1000 (changed on purpose with `chown`)

In real life this tends to show up after a Docker bind mount shifts ownership, when you open a repository on a Windows drive from WSL2, or when you touch a repository another user created on a shared server. To isolate the cause, I ran `git init` and then changed only the owner with `chown`.

## What I Tried

First I suspected `.git` itself. But the message says `dubious ownership`, not `corrupt` or `not a git repository`. That means Git is refusing on purpose, not that anything is broken.

Next I reproduced it by changing the owner:

```bash
git init -q repo
chown -R 1000:1000 repo
id
```

```text
uid=0(root) gid=0(root) groups=0(root)
```

I'm root, the repository belongs to uid 1000, and `git status` produces the error above. So the trigger is that the current user and the directory owner differ. Read access is perfectly fine, which is what makes this confusing: `ls` and `cat` work on every file, yet Git still refuses to run.

## Root Cause

Git refuses to run in a repository whose directory is owned by someone other than the current user. This protection was added in Git 2.35.2 (the fix for CVE-2022-24765). It prevents a repository planted by someone else from running unintended commands through its config, such as `core.fsmonitor`.

`safe.directory` is the setting that tells Git "I trust this directory." For paths listed there, Git works normally even if the owner differs.

One catch: `safe.directory` is only read from **global or system config**. Putting it in the repository's `.git/config` has no effect. Otherwise a repository could vouch for itself and the protection would be pointless.

## The Fix

### 1. Confirm the owner mismatch

```bash
id -u
stat -c '%u %U' .
```

If the two values differ, this is your error.

### 2. Option A: add the directory to safe.directory (keep the owner)

Run the command Git printed, with `$(pwd)` supplying the current path:

```bash
git config --global --add safe.directory "$(pwd)"
```

### 3. Option B: take ownership (if the repo is yours)

If you will use the repository yourself, matching the owner is the real fix:

```bash
sudo chown -R "$(id -u):$(id -g)" .
```

Avoid this on a directory other users keep working in; it will break their access.

### 4. Option C: allow everything with `*` (not recommended)

```bash
git config --global --add safe.directory '*'
```

This clears the error, but it trusts every directory, which effectively turns the Git 2.35.2 protection off. I'd limit it to throwaway environments such as a CI container nobody else can write to.

## Verification

I ran Option A with an isolated `HOME` so my normal global config stayed untouched:

```bash
git config --global --add safe.directory "$(pwd)"
git status
```

```text
On branch master

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

The error was gone and the exit code was 0. You can list what you registered:

```bash
git config --global --get-all safe.directory
```

```text
/path/to/repo
```

It is stored in `~/.gitconfig` like this:

```text
[safe]
	directory = /path/to/repo
```

I also removed the entry, registered `'*'` instead, and `git status` worked again. As noted, that setting disables the protection.

## Summary

- `dubious ownership` is not corruption. Git is refusing because the directory owner differs from the current user.
- For a repository you trust, use `git config --global --add safe.directory <path>`; for your own repository, align ownership with `chown`.
- `safe.directory '*'` is convenient but disables the protection wholesale. Keep it to disposable environments, and remember that writing it to `.git/config` does nothing.

Ownership drift is often caused by Docker volumes or by having run `sudo git ...`. When you hit this error, run `stat` on the directory first; it narrows things down quickly, and it saves you from poking at `.git` or reinstalling Git for no reason.

## FAQ

**Q: I ran `sudo git pull` and now my normal user gets the error.**
Files created or updated under `sudo` are likely owned by root now. Restore ownership with `sudo chown -R "$(id -u):$(id -g)" .` and avoid `sudo` for Git afterward.

**Q: Can I put `safe.directory` in `.git/config` to share it per repository?**
No. Git deliberately ignores `safe.directory` in repository-local config. It must be in global or system config.

**Q: How do I undo a `safe.directory` entry?**
`git config --global --unset-all safe.directory` removes all of them. To remove just one path, edit the matching line in `~/.gitconfig`.

## Related Articles

- [Fix: git clone Leaves Submodule Directories Empty and Breaks the Build](/en/git-submodule-not-initialized)
- [Fix "fatal: not a git repository"](/en/git-fatal-not-a-git-repository)
- [Fix "is already used by worktree" When Running git worktree add](/en/git-worktree-already-checked-out)
- [Linux File Permissions (chmod/chown) Basics](/en/linux-file-permissions)
- [Linux User Management (useradd/usermod) Basics](/en/linux-user-management)
