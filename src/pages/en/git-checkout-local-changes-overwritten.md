---
title: 'Fix: git checkout Fails With "Your local changes...would be overwritten"'
date: '2026-09-26'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git checkout fails with "Your local changes to the following files would be overwritten by checkout". Here is why it happens and how to fix it with git stash.'
en_tags: ['Git', 'git checkout', 'git stash']
---

## What I Was Trying to Do

I was mid-edit on `config.json` on `main` and wanted to quickly peek at what another teammate had changed on `feature/add-retry-option`, planning to come right back. Without thinking much about it, I just ran a checkout.

```bash
git checkout feature/add-retry-option
```

It stopped with this error instead:

```text
error: Your local changes to the following files would be overwritten by checkout:
	config.json
Please commit your changes or stash them before you switch branches.
Aborting
```

It exited with status 1 and the branch never switched. I hadn't committed anything, so being told my "local changes" would be overwritten was confusing at first.

## Environment

- OS: Ubuntu 24.04.4 LTS (Noble Numbat)
- Git: 2.43.0
- File involved: `config.json` (tracked on both `main` and `feature/add-retry-option`)
- State: `config.json` edited on `main`, but not committed or stashed

## What I Tried

First I checked exactly what was uncommitted, per the error's own hint.

```bash
git status
```

```text
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   config.json

no changes added to commit (use "git add" and/or "git commit -a")
```

`config.json` was indeed modified. I had flipped `"debug": false` to `"debug": true` for local debugging and forgotten to deal with it.

```bash
git diff
```

```text
diff --git a/config.json b/config.json
index 9bb899a..6000699 100644
--- a/config.json
+++ b/config.json
@@ -1,4 +1,4 @@
 {
   "env": "production",
-  "debug": false
+  "debug": true
 }
```

My first thought was "it's not committed, so a checkout should just work" — but from Git's point of view, the target branch matters too. `config.json` on `feature/add-retry-option` is a different, committed version of the same file with an added `retry` key. If Git silently swapped the working tree over to that version, my uncommitted `debug: true` edit would be gone with no way to get it back. So Git detects that risk and refuses instead.

## Root Cause

`git checkout <branch>` replaces working tree files with the content recorded on the target branch. When a file is tracked on both the current and target branch, and the working tree has uncommitted changes to that same file, Git treats those changes as a diff that could be silently destroyed by the switch — so it aborts instead of merging or guessing.

In my case:

- `main` side of `config.json`: `debug: true` (uncommitted)
- `feature/add-retry-option` side of `config.json`: a committed version with `retry: 3` added

Since both branches track the same file path, Git can't reconcile the two, so it errs on the side of caution and stops. This is a safety feature, not a bug — if it had overwritten silently, the `debug: true` edit would have been unrecoverable.

What made this confusing is that the error message only says the change "would be overwritten" without explaining why — that the other branch also has a different version of the same file. Running `git diff` for my own change and `git log --oneline feature/add-retry-option -- config.json` for the other branch's history makes it clear both sides touched the same file.

## How I Fixed It

### 1. Check what's uncommitted

```bash
git diff
```

Just the `debug` field, as expected. If it were disposable, `git restore config.json` would be enough. I wanted to keep it, though.

### 2. Stash the change

```bash
git stash
```

```text
Saved working directory and index state WIP on main: d9f2ad0 initial commit
```

### 3. Confirm the working tree is clean

```bash
git status
```

```text
On branch main
nothing to commit, working tree clean
```

### 4. Switch to the target branch

```bash
git checkout feature/add-retry-option
```

```text
Switched to branch 'feature/add-retry-option'
```

No error this time.

```bash
cat config.json
```

```text
{
  "env": "production",
  "debug": false,
  "retry": 3
}
```

That's the `feature/add-retry-option` version, `retry: 3` included, as expected.

### 5. Switch back and restore the stash

```bash
git checkout main
git stash pop
```

```text
Switched to branch 'main'
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   config.json

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (95b4ca24866e1dbd45da2592e314864d1b4426b5)
```

## Verify It Works

```bash
cat config.json
```

```text
{
  "env": "production",
  "debug": true
}
```

`debug: true` is back exactly as it was before the stash. `git stash list` was also empty, confirming nothing was left behind. I'd achieved what I actually wanted: check the other branch's content without losing my uncommitted edit on `main`.

## Takeaways

- `git checkout` refuses to switch branches when the working tree has uncommitted changes to a file that's also tracked and different on the target branch. The "would be overwritten by checkout" message is Git protecting you, not a bug.
- Decide first whether the change is disposable or worth keeping. Discard it with `git restore <file>`, or keep it with `git stash` before switching.
- Restore with `git stash pop` when you're back. If you have multiple stashes, check `git stash list` first so you don't pop the wrong one.

## FAQ

**Q: Is there a way to switch branches without stashing?**
Since Git 2.23, `git switch --discard-changes <branch>` will force the switch, but as the name says, it throws away the uncommitted changes for good. If you want to keep them, `git stash` is the safer option.

**Q: What if `git stash pop` reports a CONFLICT?**
That happens when the branch you switched to also touched the same lines your stash changed. Resolve the conflict markers (`<<<<<<<` etc.) by hand, `git add` the file, then run `git stash drop` to remove that stash entry — `pop` won't auto-delete it on a failed apply, so `drop` is a separate step after resolving.

**Q: Checking `git status` every time feels tedious. Any shortcut?**
Getting into the habit of running `git diff --stat` before a checkout shows at a glance which files are uncommitted. If you do hit this error anyway, `git status` plus `git diff` is still the fastest way to figure out what's worth keeping.

## Related Articles

- [Use git stash to Temporarily Shelve Your Work](/en/git-stash-usage)
- [How to Resolve Merge Conflicts After git pull](/en/git-pull-merge-conflict)
- [How to Undo a Commit in Git](/en/git-commit-undo)
- [Fix "is already used by worktree" When Running git worktree add](/en/git-worktree-already-checked-out)
- [Fix: git clone Leaves Submodule Directories Empty and Breaks the Build](/en/git-submodule-not-initialized)
