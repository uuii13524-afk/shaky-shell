---
title: 'Fix: git pull "fatal: refusing to merge unrelated histories" (Git 2.43)'
date: '2026-10-08'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git pull origin main stops with "fatal: refusing to merge unrelated histories". Here is a reproduced case, why the two histories share no ancestor, and how to merge them with --allow-unrelated-histories.'
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## What I Wanted to Do (Symptom)

I had started a project locally with `git init` and wanted to sync it with a remote repository I created afterwards. The remote already contained an initial commit with only a README, the kind that gets added automatically when you create a repository from a web UI.

```bash
git remote add origin ../remote.git
git pull origin main
```

The first `git pull` stopped with a hint about divergent branches.

```text
From ../remote
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
fatal: Need to specify how to reconcile divergent branches.
```

That only means `pull` did not know how to integrate the changes, so I picked merge explicitly and ran it again. This time I got a different error:

```bash
git pull --no-rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

## Environment

- OS: Ubuntu 24.04.5 LTS
- Git: 2.43.0
- Local: created with `git init -b main`, one commit containing a README
- Remote: a bare repository holding a separate initial commit (README only)
- Everything here was reproduced with a local bare repository (`../remote.git`)

## What I Tried

My first suspicion was a branch name mismatch. Both sides use `main`, so that was not it.

Next I fetched and looked at both sets of commits side by side.

```bash
git fetch origin
git log --oneline --all --graph
```

```text
* 2aec163 first local commit
* 42aee34 initial commit on remote
```

The two commits sit in a straight column with no branching lines joining them. They are two independent histories with no parent-child relationship.

To confirm there was no shared ancestor, I ran `merge-base`.

```bash
git merge-base HEAD origin/main
echo "exit=$?"
```

```text
exit=1
```

It printed nothing and returned exit code 1, meaning there is no common ancestor commit at all.

## Cause

`git merge` and `git pull` do a three-way merge starting from the common ancestor (the merge base) of the two branches. Here, the local and remote histories each begin from a different root commit, so no common ancestor exists. Merging them could mix in an entirely unrelated project by accident, so Git refuses by default. That is what `refusing to merge unrelated histories` means.

As far as I know, this refusal became the default behavior in Git 2.9. Older versions merged such histories silently, which is why some older tutorials give steps that no longer work as written.

It tends to show up in situations like these:

- You ran `git init` locally, then created a remote that already has an initial commit (README or LICENSE) and tried to sync
- You rewrote history with a tool such as `git filter-repo`, or recreated the repository, so the root commit changed
- You want to combine two repositories that were created independently

## Solution

### 1. Confirm the histories really should be joined

```bash
git log --oneline origin/main
```

Check that you are not about to pull in an unrelated project. In my case the remote was only a README initial commit, so merging was fine.

### 2. Merge with `--allow-unrelated-histories`

```bash
git pull --no-rebase origin main --allow-unrelated-histories
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Auto-merging README.md
CONFLICT (add/add): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

The "unrelated histories" error is gone and the merge ran. But both sides had a `README.md` that counted as newly added, so it ended in an add/add conflict.

### 3. Resolve the conflict

```bash
git status --short
cat README.md
```

```text
AA README.md
<<<<<<< HEAD
# local
=======
# remote
>>>>>>> 42aee348ee440d6e8b918e39cd3e62e00de6a5a5
```

`AA` means "added by both". I edited the file to the content I wanted, a single line in this case:

```bash
echo "# project" > README.md
git add README.md
git commit
```

An editor opens for the commit message; I saved the default merge message as it was.

## Verification

I checked the history after the merge and whether a common ancestor now exists.

```bash
git log --oneline --graph
git merge-base HEAD origin/main
```

```text
*   2888d83 Merge branch 'main' of ../remote
|\  
| * 42aee34 initial commit on remote
* 2aec163 first local commit
42aee348ee440d6e8b918e39cd3e62e00de6a5a5
```

The two histories are now joined by a merge commit, and `merge-base` returns the remote's initial commit. Later `git pull` runs work normally.

## Summary

- `refusing to merge unrelated histories` means the two branches share no common ancestor, so Git refuses to merge. It is about different root commits, not a branch name mismatch.
- If `git merge-base HEAD origin/main` prints nothing and exits with 1, you are in this case.
- Once you have confirmed the merge is intended, add `--allow-unrelated-histories`. If both sides have a README or LICENSE you will get an add/add conflict, so expect to resolve it by hand.
- To avoid it next time, clone the existing remote before you start working, or create the remote empty (without a README).

## FAQ

**Q: Does `--allow-unrelated-histories` delete any data?**
In my test, both sides' contents stayed in the working tree until I resolved the conflict myself. If you discard one side while resolving, that content disappears from the latest file, although it remains in history as commits. Check `git log origin/main` before running it.

**Q: Typing `--no-rebase` on every pull is tedious.**
`git config pull.rebase false` makes merge the default. It is a separate issue from this error, but when the very first `pull` stops, setting it first makes it easier to see which problem you are actually hitting.

**Q: I don't need the remote history and want to overwrite it with mine. What then?**
`git push --force` overwrites it, but the remote history is lost. On a shared repository that can break other people's work, so agree with your team first.

## Related Articles

- [Fix: git push Rejected (Non-Fast-Forward)](/en/git-push-rejected-fix)
- [How to Resolve Merge Conflicts on git pull](/en/git-pull-merge-conflict)
- [Git Remote Repository Operations (remote/fetch/pull/push)](/en/git-remote-operations)
- [How to Create a GitHub Repository and Push for the First Time](/en/github-first-push)
