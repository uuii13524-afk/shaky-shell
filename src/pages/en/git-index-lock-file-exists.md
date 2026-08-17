---
title: 'Fix "Unable to create .git/index.lock: File exists" in git commit'
date: '2026-08-17'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git commit or git add fails with "Unable to create .git/index.lock: File exists" even though no other git process is running. Here is why the lock file gets stuck and how to remove it safely.'
en_tags: ['Git', 'index.lock', 'commit']
---

## What I Was Trying to Do

I tried to commit some changes in a repository I was working in, the same way I always do.

```bash
git commit -m "first commit"
```

```text
fatal: Unable to create '/path/to/repo/.git/index.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
```

The command stopped with `fatal` and no commit was created. I hadn't opened an editor or any other git command right before this, and I only had a single terminal open.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- Repository: a normal local git repository (`.git` lives inside the working directory, not on external or networked storage)

## What I Tried

First I ran `git status` to check whether the repository itself was corrupted.

```bash
git status
```

```text
On branch master

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   file.txt
```

Surprisingly, `git status` worked fine and correctly showed the staged file. That told me the repository wasn't broken — only some operations were failing. I confirmed this by running `git add` on another file, which reproduced the exact same error.

```bash
git add file2.txt
```

```text
fatal: Unable to create '/path/to/repo/.git/index.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
```

So `git status` (a mostly read-only command) succeeded, while `git add` and `git commit` (commands that write to the index) both failed. The error message itself pointed at a specific file — `.git/index.lock` — so I checked whether it actually existed.

```bash
ls -la .git/index.lock
```

```text
-rw-r--r-- 1 root root 0 Aug 17 00:10 .git/index.lock
```

A zero-byte `index.lock` file was indeed sitting there. Being empty is consistent with it being a lock file that's supposed to be created and deleted automatically during normal operation, not a file meant to hold any content.

## Why This Happens

Before Git writes to `.git/index` (the file that holds the staging area), it creates a temporary `.git/index.lock` file, does its work, and deletes it when finished. This is a simple mutual-exclusion mechanism that prevents two git processes from writing to the index at the same time and corrupting it. While `index.lock` exists, Git assumes another process is currently editing the index, and any new write command — `add`, `commit`, `merge`, and similar — refuses to run and fails with this error.

In the normal case, `index.lock` is removed automatically the instant the command finishes. It was left behind here because a previous git command was interrupted before it could finish — the terminal being force-closed, the process being killed, or an editor invoked by `commit` hanging or crashing. The process that was holding the lock no longer existed, but the lock file itself — its leftover trace — never got cleaned up, so every subsequent write command kept assuming the repository was still in use.

`git status` succeeding makes sense in this light: it only reads the index to display its contents and never writes to it, so it's unaffected by whether `index.lock` exists. That matches exactly what I observed — only the write-oriented commands were blocked.

## Solution

### 1. Confirm no other git process is actually running

Before deleting the lock file, make sure no other git command or IDE Git integration is genuinely still working on the same repository. Deleting the lock file while a real process is still writing to the index can corrupt it, so this check comes first, not after.

```bash
ps aux | grep -i git
```

Once you've confirmed nothing relevant shows up and no editor or IDE has the repository open, move on to the next step.

### 2. Remove `.git/index.lock` manually

With no active process confirmed, delete the lock file as the error message itself suggests.

```bash
rm .git/index.lock
```

### 3. Retry the write command that failed

```bash
git add file2.txt
git commit -m "second commit"
```

```text
[master 2e8c229] second commit
 1 file changed, 1 insertion(+)
```

The commit completed with no error.

## Verify It Works

```bash
git log --oneline
git status
```

```text
2e8c229 second commit
35f7321 first commit
On branch master
nothing to commit, working tree clean
```

Both `add` and `commit` worked normally after removing `index.lock`, and `git status` reported a clean working tree afterward.

## Gotchas

- Because `git status` still worked, I almost concluded the repository was fine and looked elsewhere first. In reality, read-only and write commands simply behave differently here — `status` succeeding tells you nothing about whether the root cause is fixed.
- `index.lock` is zero bytes, so there's nothing to learn from its contents. Its mere existence is the signal — it means a previous operation was interrupted, not that anything specific went wrong during that operation.
- Deleting the lock file while another git process is genuinely still running would create a real conflict and could corrupt the index. I made a point of checking `ps aux` first rather than skipping straight to `rm`.

## FAQ

**Q: Is it safe to just delete `index.lock`?**
Yes, as long as you've confirmed no other git process is currently running against the same repository. If one is, deleting the lock file mid-operation can cause its write to collide with your next command and corrupt the index — always check for running processes first.

**Q: Why didn't `git status` fail too?**
`status` only reads and displays the index; it never writes to it. `.git/index.lock` exists specifically to serialize write operations, so read-only commands are unaffected by its presence.

**Q: How do I avoid this happening again?**
Avoiding force-killing terminals or processes while a git command is mid-write helps, but it can't be fully prevented. If it happens again, the fix is the same: confirm nothing is still running, then remove `.git/index.lock`.

## Related Articles

- [Fixing a Rejected git push](/en/git-push-rejected-fix)
- [How to Use git stash](/en/git-stash-usage)
- [Fixing "fatal: not a git repository"](/en/git-fatal-not-a-git-repository)
- [Recovering Commits with git reflog](/en/git-reflog)
