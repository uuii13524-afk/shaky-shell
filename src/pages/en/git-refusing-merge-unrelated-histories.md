---
title: 'Fix "fatal: refusing to merge unrelated histories" on git pull [Git 2.43]'
date: '2026-09-29'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git pull stops with "fatal: refusing to merge unrelated histories". Here is why a local repo and a remote with separate root commits cannot be merged by default, and how to integrate them with rebase or --allow-unrelated-histories and push.'
ja_tags: ['Git', 'git pull', 'unrelated histories']
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## What I Was Trying to Do

I had started a project locally and wanted to push it to a remote repository that I had created earlier. That remote was not empty: it already contained a single README commit, because I had ticked "Add a README" when creating it.

`git push` was rejected first.

```bash
git push -u origin main
```

```text
To ../remote.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '../remote.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

Following the hint, I ran `git pull` with merge, and hit a different error.

```bash
git pull --no-rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

I could neither push nor pull. Below is what I checked, reproduced in a scratch setup.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- Branch name: `main` on both sides
- Remote: a local bare repository (`../remote.git`) used for the test. GitHub behaves the same way.
- Local: a freshly `git init`-ed repo with one commit containing `index.js`
- Remote: one commit containing `README.md`

## What I Tried

### 1. Force-pushing

The rejection says "fetch first", so my first thought was `--force`. I did not run it. It would discard the remote commit, and on a shared repository that is not recoverable.

### 2. Plain `git pull`

Running `git pull origin main` with no options did not show the unrelated-histories error. Git only asked me to choose how to reconcile the branches.

```text
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

On Git 2.43 this appears when `pull.rebase` is not configured. Only after I explicitly chose merge with `--no-rebase` did I reach `refusing to merge unrelated histories`.

### 3. Looking at the history

```bash
git log --oneline --all --graph
```

Both `first local commit` and the remote's `Initial commit` are root commits with no parent. They share no ancestor.

## Why This Happens

A repository created with `git init` locally and one created separately on the remote each start their own history from their own root commit. Since there is no common ancestor, a merge has no base to work from.

Git has refused to merge such histories by default since 2.9. It is a guard against accidentally merging an unrelated repository and mixing the two histories. If you really do want to combine them, you have to say so explicitly.

## Solution

There are two ways to integrate. Rebase gives a straight line; merge records the join. Neither rewrites the remote history.

### Option A: Rebase

```bash
git pull --rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
Rebasing (1/1)
Successfully rebased and updated refs/heads/main.
```

Rebase replays my local commit on top of the remote's `Initial commit`, so no merge base is needed and no error appeared. The result is linear:

```text
* a023d71 first local commit
* c083ee9 Initial commit
```

The local commit's hash changed, which is fine because it had never been pushed.

### Option B: Merge with `--allow-unrelated-histories`

```bash
git pull --no-rebase --allow-unrelated-histories --no-edit origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`--allow-unrelated-histories` lifts the restriction, and `--no-edit` skips the merge-message editor. The two histories join in a merge commit:

```text
*   f4c77b3 Merge branch 'main' of ../remote
|\  
| * 28dafe8 Initial commit
* 1ddf576 first local commit
```

If both sides contain a file with the same name, for example a different `.gitignore` on each, you will get a normal merge conflict here. Fix the file, then `git add` and `git commit`. In my test, `README.md` and `index.js` did not overlap, so there was no conflict.

### Then push

```bash
git push -u origin main
```

```text
To ../remote.git
   c083ee9..a023d71  main -> main
branch 'main' set up to track 'origin/main'.
```

The `c083ee9..a023d71` range shows the push appended to the remote history rather than overwriting it.

## Verify It Works

```bash
git status -sb
```

```text
## main...origin/main
```

Local `main` and `origin/main` point to the same place, and `git log --oneline --graph` shows both my commit and the remote's commit.

## Gotchas

- The cause is the missing common ancestor, not your pull settings. Changing `pull.rebase` will not help if you still merge; `git pull --no-rebase` gives the same error.
- Only add `--allow-unrelated-histories` when you truly mean to combine the two. If you pulled from the wrong URL, the flag lets the merge succeed and pulls in a pile of unrelated files. Check `git remote -v` first.
- `git push --force` also gets you past the rejection, but it deletes the remote history. Avoid it unless the remote is yours alone and empty of anything you need.
- All output above came from a local test repository. Against GitHub, only the URL lines differ.

## FAQ

**Q: When does this error usually show up?**
Typically when you connect a locally `git init`-ed repository to a remote that was created separately, especially one created with an auto-generated README or LICENSE.

**Q: Rebase or merge?**
Rebase for a clean straight line; merge if you want the join recorded. The resulting file contents are the same.

**Q: How do I avoid it in the first place?**
Create the remote repository empty, with no README or other initial files, then push your local history directly. Alternatively, `git clone` the remote first and add your files inside the clone.

## Summary

- `refusing to merge unrelated histories` means the local and remote branches share no common ancestor.
- Integrate with `git pull --rebase` or `git pull --allow-unrelated-histories`, then push normally.
- Check `git remote -v` before using the override flag so you do not merge the wrong repository.

## Related Articles

- [Fixing git push Rejected Errors](/en/git-push-rejected-fix)
- [Resolving Merge Conflicts on git pull](/en/git-pull-merge-conflict)
- [Basic Usage of git rebase](/en/git-rebase-basics)
- [Basic git remote Operations](/en/git-remote-operations)
- [Your First Push to GitHub](/en/github-first-push)
