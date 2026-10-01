---
title: 'Fix "fatal: refusing to merge unrelated histories" on git pull (Git 2.43)'
date: '2026-10-01'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git pull or git merge stops with "fatal: refusing to merge unrelated histories" because local and remote share no common ancestor. Here is how to confirm it with git merge-base and fix it with --allow-unrelated-histories or git pull --rebase.'
ja_tags: ['Git', 'unrelated histories', 'git pull']
en_tags: ['Git', 'unrelated histories', 'git pull']
---

## What I Was Trying to Do

I had started a project locally with `git init` and made a commit. Afterwards I connected a remote with `git remote add` and tried to pull in what was already there: a single `Initial commit` that added a `README.md`, created somewhere else.

```bash
git pull origin main
```

It stopped with this:

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

`git merge origin/main` fails the same way. It is not a merge conflict. Git is refusing to start the merge at all.

## Environment

- OS: Linux (kernel 6.18)
- Git: 2.43.0
- Setup: a local working repo `work`, a bare repo `remote.git` acting as the remote, and a separate clone `other` used only to create the remote's first commit
- Branch name: `main` in all of them (`git init -b main`)
- `pull.rebase`: `false` (merge)

All output below comes from running this exact local setup. No external service such as GitHub was involved.

## What I Tried

### 1. Plain `git pull`

With no `pull.rebase` setting, `git pull origin main` first showed a different message:

```text
hint: You have divergent branches and need to specify how to reconcile them.
(...)
fatal: Need to specify how to reconcile divergent branches.
```

That is a separate check: Git wants to know whether to merge, rebase, or fast-forward only. After I ran `git config pull.rebase false`, the real error appeared. So "divergent branches" and "unrelated histories" are different problems, and the second can be hidden behind the first.

### 2. Checking for a common ancestor

To see whether the histories really were unrelated, I used `git merge-base`:

```bash
git fetch origin
git merge-base main origin/main
echo "rc=$?"
```

```text
rc=1
```

No hash printed and exit code 1. `git merge-base` prints the common ancestor when it finds one and exits with 1 when it does not. So local `main` and `origin/main` really have no shared commit.

### 3. Trying to push first

I wondered whether pushing first would sidestep the problem:

```bash
git push origin main
```

```text
To ../remote.git
 ! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to '../remote.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. If you want to integrate the remote changes,
hint: use 'git pull' before pushing again.
```

Rejected, as expected. `--force` would have wiped the remote's initial commit, so I did not go that way.

## Why This Happens

To merge, Git looks for the common ancestor of the two branches and does a three-way merge. Here the local `main` and the remote `main` each start from their own separate root commit, so there is no ancestor to use.

Since Git 2.9, merging in that situation is refused by default. It is a safety net against accidentally joining two repositories that were never meant to be related. The error therefore most likely means that the local history and the remote history were created independently, which matches the empty result from `git merge-base`.

Common ways to end up here:

- Running `git init` locally, then creating a non-empty repository (with a README) on the hosting side
- Re-pointing a copy of one project at a different, newly created repository
- Rewriting history with a tool like `git filter-repo` and then reconnecting to the old remote

## Solution

There are two options. I tried both and both worked.

### Option A: merge with `--allow-unrelated-histories`

Use this when you want to keep both histories as they are.

```bash
git pull origin main --allow-unrelated-histories --no-rebase --no-edit
```

`--allow-unrelated-histories` permits a merge with no common ancestor, and `--no-edit` skips the commit message editor.

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

No file names collided, so there was no conflict. If both sides have a file with the same name, you get an ordinary merge conflict to resolve by hand before committing.

### Option B: `git pull --rebase`

Use this when you want a single straight history with no merge commit.

```bash
git pull --rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Rebasing (1/1)
Successfully rebased and updated refs/heads/main.
```

Surprisingly, this needed no `--allow-unrelated-histories`. Rebase does not require a common ancestor, so my one local commit was replayed on top of the remote's `Initial commit`.

## Verify It Works

After Option B the history is linear:

```bash
git log --oneline --graph
```

```text
* 9e36887 local first commit
* afd93a6 Initial commit
```

`ls` showed both the remote's `README.md` and my local `local.txt`.

After Option A you get a merge commit instead:

```text
*   8d47f79 Merge branch 'main' of ../remote
|\  
| * 8a6cd5e Initial commit
* 07a76a6 local first commit
```

I also confirmed that `git push origin main` then succeeds:

```text
To ../remote.git
   8a6cd5e..8d47f79  main -> main
```

## Summary

- `refusing to merge unrelated histories` means the two branches share no common ancestor. An empty `git merge-base` confirms it
- Use `--allow-unrelated-histories` to keep both histories, or `git pull --rebase` for a straight line
- Do not `git push --force` over the remote without checking what you would delete

To avoid it in new projects, create the remote first and `git clone` it, so both sides share a root commit from the start. If you already worked locally, the two methods above cover it.

The behavior described here was verified on Git 2.43.0; defaults may differ in other versions.

## FAQ

**Q: Is `--allow-unrelated-histories` safe?**
If you accidentally connected the wrong repository, it will mix unrelated histories. Check `git log origin/main` first to make sure the content is what you expect.

**Q: Should I use `git pull --rebase` or `--allow-unrelated-histories`?**
With few local commits and a wish for a clean history, use `--rebase`. If you want to keep both histories intact or the commits are already shared, merge.

**Q: How do I avoid this error?**
Create the repository on the remote first and `git clone` it before you start working.

## Related Articles

- [Fixing a Rejected git push](/en/git-push-rejected-fix)
- [Resolving Merge Conflicts on git pull](/en/git-pull-merge-conflict)
- [Basic Usage of git rebase](/en/git-rebase-basics)
- [Basic git remote Operations](/en/git-remote-operations)
- [Pushing to GitHub for the First Time](/en/github-first-push)
