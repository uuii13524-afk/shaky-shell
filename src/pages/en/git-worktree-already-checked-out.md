---
title: 'Fix "is already used by worktree" When Running git worktree add'
date: '2026-07-30'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git worktree add fails with "is already used by worktree" even after the directory is gone. Here is why deleting a worktree folder with rm leaves stale metadata, and how git worktree prune fixes it.'
en_tags: ['Git', 'git worktree', 'branch']
---

## What I Was Trying to Do

I use `git worktree` to work on several feature branches in parallel. At some point I decided I no longer needed the worktree for `feature-login`, and instead of running `git worktree remove`, I just deleted the whole directory with `rm -rf`.

A few days later, I tried to set up a fresh worktree for the same branch in a new location, and `git worktree add` failed.

```bash
git worktree add ../feature-login feature-login
```

```text
fatal: 'feature-login' is already used by worktree at '/home/dev/project-feature-login'
```

The directory was already gone, but Git still believed the worktree existed. I tried a different target path, and got the exact same error.

```bash
git worktree add ../feature-login-v2 feature-login
```

```text
fatal: 'feature-login' is already used by worktree at '/home/dev/project-feature-login'
```

There was no way to add a new worktree for this branch anywhere, under any path.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Git: 2.51.0
- Repo layout: one main working directory, plus a separate worktree per feature branch under `../`
- Deleted worktree directory: `/home/dev/project-feature-login` (removed with `rm -rf` instead of `git worktree remove`)

## What I Tried

First I checked what worktrees Git currently thought existed.

```bash
git worktree list
```

```text
/home/dev/project                  a1b2c3d [main]
/home/dev/project-feature-login    e4f5g6h [feature-login]
```

`/home/dev/project-feature-login` was still listed as an active worktree, even though the directory itself was long gone. I confirmed that by trying to `cd` into it.

```bash
cd /home/dev/project-feature-login
```

```text
bash: cd: /home/dev/project-feature-login: No such file or directory
```

Next I checked whether the branch itself was intact.

```bash
git branch -v
```

```text
* main            a1b2c3d Latest commit on main
  feature-login   e4f5g6h Add login form validation
```

The branch was fine — nothing wrong with the commit history. The problem was that Git's internal worktree metadata still recorded `feature-login` as checked out at a path that no longer existed.

## Why This Happens

Git keeps per-worktree bookkeeping under `.git/worktrees/` in the main repository — which directory each worktree lives in, and which branch it has checked out. Running `git worktree remove` cleans up both the directory and this metadata together, keeping everything consistent.

But deleting the directory directly with `rm -rf`, like I did, only removes the folder. The entry under `.git/worktrees/` is left behind, so as far as Git is concerned, `feature-login` is still checked out at `/home/dev/project-feature-login`. When I tried to add the same branch to a new worktree, Git's safeguard against checking out the same branch in two places at once kicked in, and I got `is already used by worktree`. Nothing was actually broken — Git simply didn't know the directory was gone yet.

## Solution

### 1. Check the current worktree list

```bash
git worktree list
```

Look for any path that no longer exists on disk.

### 2. Clean up the stale worktree metadata

`git worktree prune` safely removes bookkeeping entries whose directory no longer exists.

```bash
git worktree prune -v
```

```text
Removing worktrees/project-feature-login: gitdir file points to non-existent location
```

### 3. Re-check the worktree list

```bash
git worktree list
```

```text
/home/dev/project    a1b2c3d [main]
```

The `feature-login` entry is gone, and the branch is no longer considered checked out anywhere.

### 4. Add the worktree again

```bash
git worktree add ../feature-login feature-login
```

```text
Preparing worktree (checking out 'feature-login')
HEAD is now at e4f5g6h Add login form validation
```

This time it succeeded without error.

## Verify It Works

```bash
git worktree list
```

```text
/home/dev/project                a1b2c3d [main]
/home/dev/project-feature-login  e4f5g6h [feature-login]
```

The `feature-login` branch is now correctly checked out in the new directory.

## Gotchas

- Deleting a worktree directory with `rm -rf` does not automatically clean up Git's bookkeeping under `.git/worktrees/`. Either use `git worktree remove`, or run `git worktree prune` afterward if you already deleted it by hand.
- The `is already used by worktree` message reads like the branch is genuinely in use somewhere, but in a lot of cases it's just a "ghost" worktree whose directory no longer exists. Check `git worktree list` before reaching for `--force`.
- `git worktree add --force` will let you check out the same branch into a second worktree, but having one branch checked out in two places at once is risky — it's easy to lose commits or accidentally clobber changes. Fixing the stale metadata is the safer route.
- `git worktree remove` itself refuses to run if the directory still has uncommitted changes, unless you also pass `--force` to it. That's a separate safeguard from the one described above — it protects against losing local edits, not against double-checkout. If a worktree is genuinely abandoned and you don't care about its uncommitted state, `git worktree remove --force <path>` is the cleaner alternative to `rm -rf` in the first place, since it updates the metadata for you in the same step.

## FAQ

**Q: Does deleting a worktree without `git worktree remove` damage anything else?**
No — it only leaves a mismatch between the directory and Git's metadata. Commit history and the branch itself stay intact. `git worktree prune` resolves the mismatch.

**Q: Does `git worktree prune` affect my other worktrees?**
No. It only removes entries whose corresponding directory can't be found; worktrees that still exist on disk are untouched.

**Q: How do I avoid this in the future?**
Always run `git worktree remove <path>` when you're done with a worktree. If you do delete the folder manually, make `git worktree prune` a standard follow-up step.

## Related Articles

- [Basic Git Branch Commands Cheat Sheet](/en/git-branch-basics)
- [Fixing a Detached HEAD in Git](/en/git-detached-head-fix)
- [Basic Usage of git rebase](/en/git-rebase-basics)
- [How to Use git stash](/en/git-stash-usage)
- [Fixing "fatal: not a git repository"](/en/git-fatal-not-a-git-repository)
