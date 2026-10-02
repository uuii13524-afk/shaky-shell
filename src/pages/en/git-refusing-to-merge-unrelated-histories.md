---
title: 'Fix "fatal: refusing to merge unrelated histories" on git pull (Git 2.43)'
date: '2026-10-02'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git pull stops with "fatal: refusing to merge unrelated histories". Reproduced on Git 2.43: why local and remote share no common ancestor, how --allow-unrelated-histories fixes it, and when you should not use it.'
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## What I Was Trying to Do

I had a project started locally with `git init`, and a remote repository that had been created separately with a README in it. I wanted to bring the remote content into my local branch, so I ran `git pull`. Both sides had their own commits, and neither had ever been derived from the other.

```bash
git pull --no-rebase origin main
```

```text
From ../origin
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

There is no list of conflicting files here, just the phrase "unrelated histories" and a stop.

One note up front: every output in this article comes from a sandbox where I created a bare "remote" repository and a local repository myself, to reproduce the error. It is not a log from a production incident.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- Local: created with `git init -b main`, one commit containing `app.py`
- Remote: a separate repository with one commit containing `README.md`, pushed to a bare repository
- Branch name: `main` on both sides

## What I Tried

### 1. Plain `git pull`

My first attempt was a bare `git pull origin main`. With `pull.rebase` unset on Git 2.33 or later, it stops earlier, with a different message:

```bash
git pull origin main
```

```text
From ../origin
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint:
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
hint:
hint: You can replace "git config" with "git config --global" to set a default
hint: preference for all repositories. You can also pass --rebase, --no-rebase,
hint: or --ff-only on the command line to override the configured default per
hint: invocation.
fatal: Need to specify how to reconcile divergent branches.
```

That is a separate question (how to reconcile), so I re-ran with `--no-rebase` to choose merge explicitly. That produced the `refusing to merge unrelated histories` error shown above.

### 2. Confirm that `git fetch` works

`git fetch origin` finished without errors and `origin/main` was available locally. So this is not a network or authentication problem. Only the integration step is refused.

### 3. Look at the history graph

```bash
git log --oneline --all --graph
```

```text
* dbdc507 Add app.py
* 10b54b6 Initial commit on remote
```

The two commits are just stacked, with no point where the lines join. Then I asked Git for a common ancestor:

```bash
git merge-base main origin/main
echo "rc=$?"
```

```text
rc=1
```

No output and exit code 1. `git merge-base` prints a common ancestor commit, so this confirms that there is none.

### 4. `git pull --rebase` also works here

I also tried a rebase, which succeeded in this setup:

```bash
git pull --rebase origin main
```

```text
From ../origin
 * branch            main       -> FETCH_HEAD
Rebasing (1/1)
Successfully rebased and updated refs/heads/main.
```

My `Add app.py` commit ended up on top of the remote's initial commit in a single line. A rebase moves your commits onto the other tip, so it does not need a common ancestor. If you only want a linear history, this is a valid option. Just keep in mind that it rewrites the hashes of every local commit, which matters if your local history is long.

## Cause

A merge-type `git pull` performs a three-way merge starting from the common ancestor of the two branches. When the local and remote repositories each began from their own `git init`, no commit chain connects them, which is why `git merge-base` printed nothing.

Since Git 2.9, merging in that state is refused by default. The idea is to prevent you from accidentally combining two unrelated projects. This is Git's safety check working as intended, not a bug.

## Fix

Only when you have confirmed you really want to join the two histories, add the opt-in flag.

### 1. Inspect what you are about to pull in

```bash
git fetch origin
git log --oneline origin/main
```

Check what the remote contains and decide whether it really belongs with your project. Skipping this step is how files from an unrelated project end up in your repository.

### 2. Merge with `--allow-unrelated-histories`

```bash
git pull --no-rebase --allow-unrelated-histories --no-edit origin main
```

```text
From ../origin
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`--no-edit` skips the commit message editor and keeps the automatic merge message.

If both sides have a file with the same name and different content (for example `README.md` on both), you get an ordinary merge conflict. Resolve it the same way as in [How to Resolve Merge Conflicts After git pull](/en/git-pull-merge-conflict).

### 3. Check the result, then push

```bash
git log --oneline --graph
git push origin main
```

## Verification

After the merge, the history looked like this:

```text
*   95596db Merge branch 'main' of ../origin
|\
| * 10b54b6 Initial commit on remote
* dbdc507 Add app.py
```

The two lines now join at a merge commit, and both files are present:

```bash
ls
```

```text
README.md
app.py
```

Git can also find a common ancestor now:

```bash
git merge-base main origin/main
```

```text
10b54b6c530467ce81f2441e60f0c2e1d2467358
```

From here on, ordinary `git pull` and `git push` behave normally.

## Gotchas

- The first message you see may not be `unrelated histories` at all. On Git 2.43 in my test, the `divergent branches` message came first, and I had to choose merge or rebase before reaching the target error.
- `--allow-unrelated-histories` is not a flag that merely silences the error. It states that you are deliberately joining two separate histories. If the remote is actually a different project, you will push a history with mixed-up files.
- The real prevention is to start the same way on both sides: either `git clone` the remote first, or create the remote as an **empty repository without a README** when the local one comes first. The first-push steps are covered in [How to Create a GitHub Repository and Push for the First Time](/en/github-first-push).

## Summary

- `refusing to merge unrelated histories` appears when local and remote share no ancestor commit. If `git merge-base` prints nothing, this is your case.
- Add `--allow-unrelated-histories` only after checking what you are merging. If you prefer a linear history, `git pull --rebase` is an alternative.
- The same error shows up after re-pointing a remote or re-running `git init` on a repository you later reconnect. Make `git log --oneline --all --graph` your first check.

## FAQ

**Q: Does `--allow-unrelated-histories` delete any data?**
No. It keeps both histories and joins them with a merge commit. If files with the same name exist, you still have to resolve the conflicts as usual.

**Q: What if I want to discard my local history and match the remote?**
Only when you have confirmed that the local commits do not matter, `git reset --hard origin/main` aligns your branch. Local changes are lost, so check `git log` first.

**Q: Is a rejected `git push` the same problem?**
Not quite. That is usually a `non-fast-forward` rejection. See [How to Fix a Rejected Git Push (Non-Fast-Forward)](/en/git-push-rejected-fix).

## Related Articles

- [How to Resolve Merge Conflicts After git pull](/en/git-pull-merge-conflict)
- [How to Fix a Rejected Git Push (Non-Fast-Forward)](/en/git-push-rejected-fix)
- [How to Create a GitHub Repository and Push for the First Time](/en/github-first-push)
- [Git Remote Operations Cheat Sheet](/en/git-remote-operations)
- [Fixing "fatal: not a git repository"](/en/git-fatal-not-a-git-repository)
