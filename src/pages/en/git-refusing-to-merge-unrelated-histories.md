---
title: 'Fix "fatal: refusing to merge unrelated histories" on git pull (Git 2.43)'
date: '2026-10-09'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git pull stops with "fatal: refusing to merge unrelated histories" because local and remote share no common ancestor commit. Here is how to confirm it with git merge-base, when --allow-unrelated-histories is safe, and how to resolve the add/add conflict.'
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## What I Was Trying to Do

I had started a project locally with `git init` and made a commit. Separately, a remote repository already existed with a single commit containing only a README. I added the remote and ran `git pull`, expecting the two to merge.

```bash
git pull --no-rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

The fetch itself worked, and `origin/main` was created. But the merge step aborted with `fatal: refusing to merge unrelated histories` and exit code 128, so I could not push my local work either.

All output in this article comes from commands I actually ran in a sandbox, using two separately initialized repositories to reproduce the situation. Hashes and paths belong to that test setup and will differ on your machine.

## Environment

- OS: Ubuntu 24.04.5 LTS
- Git: 2.43.0
- Local: created with `git init -b main`, one commit that adds `app.txt`
- Remote: a bare repository; a separate clone had pushed one commit that adds `README.md`
- Config: no global git config, so `pull.rebase` was unset

## What I Tried

### 1. The first pull failed with a different error

My first attempt was a plain `git pull origin main`. With Git 2.43.0 and no `pull.rebase` setting, it stops with this instead:

```text
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint: 
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
(...)
fatal: Need to specify how to reconcile divergent branches.
```

That message only asks you to choose merge or rebase. It is a separate issue. Once I passed `--no-rebase` to choose merge, I got the `refusing to merge unrelated histories` error shown above.

### 2. Looking at both histories

```bash
git log --oneline
git log --oneline origin/main
```

```text
50b54e2 Initial local commit
48b9326 Initial commit (README)
```

The first line is the local history and the second is the remote one. Each is a single root commit with no parent, which means they are two separate trees.

### 3. Checking for a common ancestor with `git merge-base`

```bash
git merge-base HEAD origin/main
echo $?
```

```text
1
```

It printed nothing and exited with 1, meaning no common ancestor exists. That confirmed the diagnosis.

## Root Cause

Git merges two branches by finding their merge base (a shared ancestor) and doing a three-way merge from there. When `git merge-base` finds nothing, the two histories are "unrelated", and since Git 2.9 `git merge` and `git pull` refuse to combine them by default. This is a safety check that stops you from accidentally mixing two unrelated projects.

In my case the local repository started from `git init`, while the remote's first commit was created somewhere else. The two root commits are different objects, so there is no shared ancestor. Nothing is corrupted. Git is simply correct that these histories never branched from one another.

## The Fix

### Option A: merge with `--allow-unrelated-histories` (what I used)

If you want to keep both histories and join them, add the flag:

```bash
git pull --no-rebase --allow-unrelated-histories --no-edit origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`--no-edit` just skips the commit-message editor. When no file exists on both sides, the merge commit is created without conflicts.

### Option B: `git pull --rebase` did not refuse in my test

In the same situation, rebasing did not raise the error on my machine:

```bash
git pull --rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Rebasing (1/1)Successfully rebased and updated refs/heads/main.
```

My local commit was replayed on top of the remote one, giving a linear history with no merge commit. I only verified this on Git 2.43.0, so check it on your own version before relying on it.

### Option C: do not join them at all

If you do not need the remote's contents (for example, the remote is an empty placeholder you created by mistake), do not force a merge. Push to an empty repository, or recreate the remote. Avoid `--force` unless you have checked what you would overwrite, since it can discard other people's commits.

## Verification

After option A:

```bash
git log --oneline --graph
ls
```

```text
*   c55bc9d Merge branch 'main' of ../remote
|\  
| * 48b9326 Initial commit (README)
* 50b54e2 Initial local commit
README.md
app.txt
```

The two histories are now connected by merge commit `c55bc9d`, and both `README.md` and `app.txt` are in the working tree. A normal `git push origin main` works from here.

## Gotchas

### The same filename on both sides causes an add/add conflict

If I had also created `README.md` locally, the flag would let the merge start, but with no common ancestor both sides count as newly added files. I reproduced this by creating `README.md` on both sides:

```text
Auto-merging README.md
CONFLICT (add/add): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

`git status -sb` shows `AA README.md`. Resolve it like any merge conflict: edit the file, run `git add README.md`, then `git commit`. See [Resolving Merge Conflicts After git pull](/en/git-pull-merge-conflict) for the general procedure.

### The flag does not make a merge safe by itself

`--allow-unrelated-histories` is for when you really mean to combine separate histories. If you registered the wrong remote URL, the flag will happily merge a completely different project into yours. Run `git remote -v` first to confirm the URL.

## Summary

- `fatal: refusing to merge unrelated histories` means `git merge-base` found no common ancestor between the two histories
- To join them on purpose, use `git pull --no-rebase --allow-unrelated-histories`. To keep a linear history, `--rebase` is another option (verified on Git 2.43.0 only)
- Same-named files on both sides produce an `add/add` conflict, and you should double-check `git remote -v` before adding the flag

For other pull and push rejections, see [Fixing git push Rejected Errors](/en/git-push-rejected-fix) and [Basic git remote Operations](/en/git-remote-operations).

## Related Articles

- [Resolving Merge Conflicts After git pull](/en/git-pull-merge-conflict)
- [Fixing git push Rejected Errors](/en/git-push-rejected-fix)
- [Basic git remote Operations](/en/git-remote-operations)
- [Basic Usage of git rebase](/en/git-rebase-basics)
- [Your First Push to GitHub](/en/github-first-push)
