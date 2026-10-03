---
title: 'Fix: git pull Fails with "fatal: refusing to merge unrelated histories"'
date: '2026-10-03'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'After running git init locally and committing first, git pull from a non-empty remote stops with fatal: refusing to merge unrelated histories. Here is how to confirm the cause and merge safely with --allow-unrelated-histories.'
en_tags: ['Git', 'unrelated histories', 'git pull']
---

## What I Was Trying to Do

I had a local project that I created with `git init` and committed to first. Later I added a remote that was not empty — it already had a single commit containing a README. My `git push` was rejected, so I followed the hint and ran `git pull`. Instead of merging, Git stopped with this:

```text
fatal: refusing to merge unrelated histories
```

This isn't a file conflict. Git refuses to start the merge at all.

## Environment

- OS: Linux
- Git: 2.43.0
- Local repo: created with `git init -b main`, one commit (`app.py` only)
- Remote: a separate history on `main` with one commit containing only `README.md` (I used a local bare repository as the remote for testing)
- Git config: defaults, with `pull.rebase` unset

Every command and output below was run in a throwaway test repository with this setup, and pasted as-is.

## What I Tried

First, a plain push:

```bash
git push origin main
```

```text
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '../remote.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
```

Following the hint, I ran `git pull origin main`. On Git 2.43.0 with no config, that stops at a different error first:

```text
hint: You have divergent branches and need to specify how to reconcile them.
fatal: Need to specify how to reconcile divergent branches.
```

That one only asks you to choose merge or rebase, so I picked merge with `--no-rebase`:

```bash
git pull origin main --no-rebase
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

That is the real error. The fetch succeeded, so the refusal comes from the merge half of `git pull`.

## Root Cause

`git merge` looks for a common ancestor commit (the merge base) and does a three-way merge from there. When the local and remote repositories were each initialized separately, their root commits differ and there is no common ancestor. Git treats the two histories as unrelated and refuses by default, because merging them is usually a mistake. Since Git 2.9, you have to opt in with `--allow-unrelated-histories`.

You can confirm there is no common ancestor directly:

```bash
git fetch origin
git merge-base main origin/main
echo "rc=$?"
```

```text
rc=1
```

`merge-base` prints nothing and exits with 1. For related histories, it would print one commit hash.

## The Fix

### 1. Inspect both histories first

```bash
git log --oneline --all --graph
```

```text
* fd5d0d8 first local commit
* fd4f79a first local commit
* 275e74c Initial commit
```

There are two separate lines that never join. The two "first local commit" entries have different hashes, so they are different commits.

### 2. Merge on purpose

If you want to keep both histories:

```bash
git pull origin main --allow-unrelated-histories --no-rebase --no-edit
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`--no-edit` skips opening an editor for the merge commit message. If both sides had a file with the same name, you would get normal conflicts here and resolve them the usual way. In this test the filenames didn't overlap (`README.md` vs `app.py`), so the merge completed automatically.

### 3. Verify and push

```bash
git log --oneline --graph
ls
git push origin main
```

## Verifying the Result

After the merge, the log looked like this:

```text
*   8591421 Merge branch 'main' of ../remote
|\  
| * fd4f79a first local commit
| * 275e74c Initial commit
* fd5d0d8 first local commit
```

`ls` showed both `README.md` and `app.py`, and the push succeeded with `fd4f79a..8591421  main -> main`. The merge commit joins the two lines, so a normal `git pull` works from here on.

## Alternative: Keep a Linear History

If you don't want a merge commit, you can replay your local commits on top of the remote branch:

```bash
git pull origin main --rebase
```

In my test this printed `Successfully rebased and updated refs/heads/main.` and left a single line of history. The catch is that your local commit hashes change, so avoid rebasing commits other people already have.

If the remote content is disposable and you only want your local history, forcing a push (`git push --force-with-lease`) is another option. It discards the remote history, so only do it when you are sure that repository doesn't matter.

## Takeaways

- `fatal: refusing to merge unrelated histories` means the local and remote branches share no common ancestor. `git merge-base` exiting with code 1 and no output confirms it.
- Use `git pull origin main --allow-unrelated-histories --no-rebase` to keep both histories, or `--rebase` for a single line.
- The usual trigger is pushing an existing local project to a GitHub repository that was created with a README. Create the remote empty, or clone it first and add your files, to avoid the error next time.

## FAQ

**Q: Will `--allow-unrelated-histories` delete anything?**
No. It keeps both sets of commits and joins them with a new merge commit. If both sides have a file with the same name, you get ordinary conflicts instead of a silent overwrite.

**Q: I added `--allow-unrelated-histories` but still got "Need to specify how to reconcile divergent branches".**
That is a separate error. `pull.rebase` isn't set, so Git wants you to choose. Add `--no-rebase` or `--rebase`, or set a default with `git config pull.rebase false`.

**Q: I really do want to combine two unrelated projects. Is it the same procedure?**
Mostly, yes. Directory layouts tend to collide, so moving one project into a subdirectory and committing that first makes the merged result easier to tidy up.

## Related Articles

- [Fix "Updates were rejected" When git push Fails](/en/git-push-rejected-fix)
- [Resolving git pull Merge Conflicts](/en/git-pull-merge-conflict)
- [Git Remote Repository Operations (remote/fetch/pull/push)](/en/git-remote-operations)
- [How to Create a GitHub Repository and Push for the First Time](/en/github-first-push)
- [Fix "fatal: not a git repository"](/en/git-fatal-not-a-git-repository)
