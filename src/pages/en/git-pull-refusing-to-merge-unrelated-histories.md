---
title: 'Fix "fatal: refusing to merge unrelated histories" on git pull (Git 2.43 / Ubuntu 24.04)'
date: '2026-10-10'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git pull origin main stops with "fatal: refusing to merge unrelated histories". I reproduced it in a scratch repo: the two histories share no common ancestor. Here is how to merge them with --allow-unrelated-histories or --rebase.'
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## What I Was Trying to Do

I had a local repository created with `git init` and a few commits. Later I added a remote that already contained one commit: the README that GitHub generates when you create a repository with "Add a README" ticked. I wanted to pull that commit in, so I ran `git pull`, and it stopped here:

```bash
git pull origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

This is not a merge conflict and not a network problem. The fetch itself succeeded; Git simply refuses to perform the merge.

A note on the logs: they come from a scratch setup I built locally (a bare repository plus a separate working repository), not from a production repo. You can follow the same steps to confirm the diagnosis on your own repository.

## Environment

- OS: Ubuntu 24.04.5 LTS
- Git: 2.43.0
- Setup: a local repository (`main`, one commit) and a separate bare repository (`main`, one commit that only adds `README.md`)
- `pull.rebase` set to `false` (merge strategy)

## What I Tried

Running `git pull` again obviously gave the same error, so I looked at the history next:

```bash
git log --oneline --all
```

```text
76ddee3 local first commit
94d4adb Initial commit
```

Two commits, and neither is the parent of the other. Then I asked Git for the common ancestor of the two branches:

```bash
git merge-base main origin/main
echo "rc=$?"
```

```text
rc=1
```

No output and exit code 1: there is no common ancestor at all.

## Cause

The empty `git merge-base` result is the key piece of evidence. The local `main` and the remote `main` are **two histories that were born independently**. The first commit made by `git init` locally and the first commit created on the remote do not know about each other.

Since Git 2.9, merging histories with no shared ancestor is refused by default. It is a safety net that stops you from accidentally pulling in a completely different project. The repository is not broken, and Git is behaving as designed.

Your Git configuration can change which error you see first. With no `pull.rebase` setting and diverged branches, `git pull` can stop earlier with `fatal: Need to specify how to reconcile divergent branches.` In my reproduction I set `pull.rebase false` first, so that only the unrelated-histories error remained.

## Solution

### 1. Check that this is the remote you meant to pull from

```bash
git remote -v
git log --oneline origin/main
```

Confirm that the URL is correct and that the remote commits look as expected (for example, just an initial README commit). If you registered the wrong URL, fix it with `git remote set-url` instead of merging anything.

### 2. If you do want to join the histories, add `--allow-unrelated-histories`

```bash
git pull --allow-unrelated-histories --no-edit origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`--no-edit` just skips the commit message editor for the merge commit.

### 3. Or use `--rebase` if you prefer a linear history

In a second scratch repository, `git pull --rebase` worked without any extra flag:

```bash
git pull --rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Successfully rebased and updated refs/heads/main.
```

Rebase just replays your local commits on top of the remote tip, so it does not need a common ancestor. The commit hashes change, though, so avoid it if the local commits have already been pushed and shared.

## Verification

After the `--allow-unrelated-histories` merge:

```bash
git log --oneline --graph
git status -sb
```

```text
*   2f2ca02 Merge branch 'main' of ../remote
|\  
| * 94d4adb Initial commit
* 76ddee3 local first commit
## main
```

The remote `Initial commit` and my `local first commit` are now joined by merge commit `2f2ca02`. From here on there is a shared ancestor, so plain `git pull` and `git push` work normally.

## Pitfalls I Noticed

- `--allow-unrelated-histories` is not a general "make the error go away" flag. If I had registered the wrong remote URL, the flag would have happily merged a completely different project into mine. Checking `git remote -v` first costs a few seconds and avoids that.
- The option only changes the merge check. It does not resolve conflicts for you, so if both histories contain a file at the same path, you still have to edit it by hand and commit.
- Whether you see this error or the "divergent branches" message first depends on `pull.rebase` and `pull.ff`. Setting one of them explicitly makes `git pull` behave the same way on every machine, which makes the error much easier to read.
- The merge commit created here is permanent history. If you would rather not have it, abort before pushing with `git reset --hard ORIG_HEAD` and use the rebase approach instead.

## Summary

- `refusing to merge unrelated histories` means the local and remote branches share no ancestor commit. An empty `git merge-base` confirms it.
- Join them deliberately with `git pull --allow-unrelated-histories`, or keep history linear with `git pull --rebase`.
- Always verify the remote URL and its contents first; the main risk is pulling in the wrong project.
- To avoid it in future, create the GitHub repository without an auto-generated README, or start from `git clone`.

## FAQ

**Q: Will `--allow-unrelated-histories` overwrite my files?**
If the same path exists on both sides, it is treated as an ordinary merge conflict. If the files do not overlap, as in my test, both sets of files simply end up in the result.

**Q: Does "refusing" mean my repository is corrupted?**
No. Git is stopping on purpose. Check the facts, then allow the merge explicitly with the option.

## Related Articles

- [Fixing git push "rejected" Errors](/en/git-push-rejected-fix)
- [Resolving Merge Conflicts After git pull](/en/git-pull-merge-conflict)
- [Basic git remote Operations](/en/git-remote-operations)
- [Your First Push to GitHub](/en/github-first-push)
- [Basic Usage of git rebase](/en/git-rebase-basics)
