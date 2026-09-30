---
title: 'Fix: git status Fails With "fatal: detected dubious ownership in repository" (safe.directory)'
date: '2026-09-30'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git status or git log stops with "fatal: detected dubious ownership in repository". The repo owner differs from the user running git. Here is why, and how to fix it with git config --global --add safe.directory.'
en_tags: ['Git', 'safe.directory', 'dubious ownership']
---

## What I Was Trying to Do

I wanted to check the state of a Git repository created by a different user (UID 1001), while logged in as root. I `cd`'d into the directory and ran `git status`. Nothing useful came back, only this:

```bash
git status
```

```text
fatal: detected dubious ownership in repository at '/path/to/repo'
To add an exception for this directory, call:

	git config --global --add safe.directory /path/to/repo
```

`git log` fails the same way, and the exit code is `128`. It looks alarming, but the message is about ownership, not about a broken repository.

The output above comes from reproducing this situation in the environment listed below. Only the path was replaced with `/path/to/repo`.

## Environment

- OS: Linux (container)
- Git: 2.43.0
- User running git: root (UID 0)
- Repository owner: UID 1001

## What I Tried

My first suspicion was a corrupted `.git` directory. But the error is `dubious ownership`, not `fatal: not a git repository`. Git recognizes the repository and refuses to use it.

Next I checked whether an exception was already registered:

```bash
git config --global --get-all safe.directory
```

It printed nothing, so this directory wasn't trusted yet.

## Cause

If the directory owner differs from the user running the command, Git refuses to operate on the repository by default. This was added as a fix for CVE-2022-24765, to stop Git from reading a malicious `.git/config` planted in a directory someone else can write to.

Here the owner was UID 1001 and the user was root, so the owners didn't match. The error doesn't mean the repository is broken. It's a safety check that says: the owner is different, so I won't touch it until you allow it explicitly.

It commonly shows up with Docker bind mounts, shared servers, running git under `sudo`, and CI containers, anywhere the user who created the files isn't the user running git.

## Solution

### 1. Mark the directory as safe

Use the command printed in the error itself:

```bash
git config --global --add safe.directory /path/to/repo
```

`--global` writes the setting to the running user's `~/.gitconfig`. Use the exact path from the error message.

### 2. Confirm it was registered

```bash
git config --global --get-all safe.directory
```

```text
/path/to/repo
```

### 3. Run git again

```bash
git status
```

```text
On branch master
nothing to commit, working tree clean
```

The error is gone and the normal output is back.

### Alternative: fix the ownership instead

You can also make the owner match the user running git with `chown -R`, which removes the mismatch entirely. I didn't do that here because other users still needed to use the repository, and I did not run that `chown` step. If you do, double-check the target path first.

## How to Check Who Owns the Directory

Before adding an exception, it's worth confirming that the mismatch is real and that you actually trust the other owner. `ls -ld` shows the owner of the directory, and `id -un` shows the user you are currently running as:

```bash
ls -ld /path/to/repo
id -un
```

If the two names differ, you've found the cause. Only add the exception if you know who created the repository and why. The whole point of the check is that a directory writable by someone else could contain configuration that runs with your privileges, so registering a path means you vouch for everyone who can write to it. That's why I registered one specific path rather than looking for a way to disable the check globally.

## Verification

Running `git status` in the same directory before and after:

- Before: `fatal: detected dubious ownership in repository`, exit code 128
- After: `On branch master` / `nothing to commit, working tree clean`

To undo the setting, remove the entry. After removal, `git status` produced the same error again, as expected:

```bash
git config --global --unset-all safe.directory
```

## Summary

- `dubious ownership` is a safety check triggered when the repo owner differs from the user running git. It is not data corruption.
- For a repository you trust, register the path from the error with `git config --global --add safe.directory <path>`.
- This tends to happen with Docker, shared servers, `sudo`, and CI containers. Registering only the specific paths you trust is safer than trusting everything.

## FAQ

**Q: Can I put `safe.directory` in the repo's own `.git/config`?**
No. Git doesn't honor it from repository-level config, so a malicious repository can't declare itself trusted. Set it at the user (`--global`) or system level.

**Q: I registered it and it still fails.**
Check that the registered path exactly matches the path in the error. `git config --global --get-all safe.directory` lists what's registered. If you run git through `sudo`, the user is root, so the entry must be in root's `~/.gitconfig`.

**Q: It's my own repository and I still get this error.**
The ownership may have changed unintentionally. Check it with `ls -ld`.

## Related Articles

- [Fix "is already used by worktree" When Running git worktree add](/en/git-worktree-already-checked-out)
- [Fix: git clone Leaves Submodule Directories Empty and Breaks the Build](/en/git-submodule-not-initialized)
- [Fix "fatal: not a git repository"](/en/git-fatal-not-a-git-repository)
- [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github)
- [Git Remote Repository Operations (remote/fetch/pull/push)](/en/git-remote-operations)
