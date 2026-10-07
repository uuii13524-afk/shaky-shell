---
title: 'Fix "fatal: refusing to merge unrelated histories" on git pull (Git 2.43)'
date: '2026-10-07'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git pull stops with "fatal: refusing to merge unrelated histories". Why local and remote have no common ancestor, and how --allow-unrelated-histories or a rebase safely combines them.'
ja_tags: ['Git', 'unrelated histories', 'git pull', 'git merge']
en_tags: ['Git', 'unrelated histories', 'git pull', 'git merge']
---

## What I Was Trying to Do

I had started a project locally and connected it to a remote repository I created afterwards. I wanted to pull a file that existed only on the remote (`LICENSE`) and then push. Instead, `git pull` stopped with this:

```text
From ../bare
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

The fetch itself succeeded and `origin/main` was created, but the merge was refused. The exit code was `128`.

## Environment

- OS: Ubuntu 24.04.5 LTS
- Git: 2.43.0
- Setup: a local repository plus a local bare repository (`../bare`) used as the remote

The same error happens against GitHub. For this reproduction I used a bare repository as a stand-in for GitHub and pushed an independent "Initial commit" to it from a separate clone.

## What I Tried

The key to reproducing this is that the local repository and the remote each got their own first commit independently.

```bash
# Local side: create the repo and commit first
git init -b main
echo "# my-app" > README.md
git add README.md
git commit -m "first commit"
git remote add origin ../bare
```

The remote already had an "Initial commit" containing only `LICENSE`. Pushing straight away was rejected:

```text
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '../bare'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
```

Following the hint, I ran `git pull origin main`. With `pull.rebase` unset, Git 2.43.0 refuses to continue until you choose how to reconcile the branches:

```text
hint: You have divergent branches and need to specify how to reconcile them.
fatal: Need to specify how to reconcile divergent branches.
```

I explicitly chose merge with `--no-rebase`, and that produced the error above:

```bash
git pull --no-rebase origin main
```

```text
fatal: refusing to merge unrelated histories
```

## Why This Happens

The two branches have no common ancestor commit. Looking at both histories, the local `first commit` and the remote `Initial commit` are separate root commits, and neither has a parent.

```bash
git log --oneline --all --graph
```

```text
* c397f9e first commit
* ec06513 Initial commit
```

The two lines never meet. Running `git merge-base HEAD FETCH_HEAD` printed nothing and returned exit code `1`, which confirms there is no shared ancestor.

Since Git 2.9, merging histories that share no ancestor is refused by default. It's a safety net against accidentally mixing two unrelated repositories. In my case the likely cause was running `git init` locally and then creating the remote separately with its own initial commit, instead of cloning.

## Solution

These steps apply once you've confirmed that the remote and the local repository really are parts of the same project. There are two options.

### Option 1: Merge with --allow-unrelated-histories

```bash
git pull --no-rebase origin main --allow-unrelated-histories --no-edit
```

`--allow-unrelated-histories` removes the safety check, and `--no-edit` skips editing the merge commit message. The output was:

```text
From ../bare
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 LICENSE | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 LICENSE
```

If both sides contain a file with the same name, you'll get a conflict. Resolve it like any other merge and run `git commit`.

### Option 2: Rebase your local commits on top

If you prefer a linear history with no merge commit, a rebase works. In my test it didn't need `--allow-unrelated-histories` at all:

```bash
git pull --rebase origin main
```

```text
Rebasing (1/1)Successfully rebased and updated refs/heads/main.
```

My local `first commit` was replayed on top of the remote's `Initial commit`, giving a straight line. Note that the commit hash changes. That's fine for local commits you haven't pushed yet.

## Verify It Worked

The history after Option 1:

```bash
git log --oneline --graph
```

```text
*   2643bed Merge branch 'main' of ../bare
|\  
| * ec06513 Initial commit
* c397f9e first commit
```

The two lines now join in a single merge commit, and `ls` shows both `LICENSE` and `README.md`. After that, a normal `git push -u origin main` works. For Option 2, a single straight line in `git log --oneline --graph` means it worked.

## Gotchas

- Always run `git remote -v` first. If `origin` points to a different project, adding `--allow-unrelated-histories` will happily pull in a pile of unrelated files.
- The rebase option rewrites the hashes of your local commits. Only use it for commits that haven't been pushed.
- With `pull.rebase` unset, you'll hit the "divergent branches" error before you ever see the unrelated-histories one. Passing `--no-rebase` or `--rebase` explicitly gets you past it.
- To avoid all of this next time, create the remote first and `git clone` it, or create the remote empty (no README or LICENSE) and then run `git remote add`.

## FAQ

**Q: Is `--allow-unrelated-histories` dangerous?**
It does nothing destructive by itself, since it just creates a merge commit joining the two histories. The risk is mixing the wrong repositories, which is why checking `git remote -v` first matters.

**Q: Can I undo the merge if it was a mistake?**
If you haven't pushed yet, `git reset --hard ORIG_HEAD` right after the merge puts the branch back where it was. Check `git status` first, because `--hard` discards uncommitted changes.

**Q: Why did Option 2 work without the flag?**
In my test the rebase simply replayed my one local commit onto the fetched `origin/main`, which doesn't require creating a merge between two roots. Behavior with more complex histories may differ, so check the result with `git log --graph`.

## Related Articles

- [How to Fix git push Rejected Errors](/en/git-push-rejected-fix)
- [How to Resolve Merge Conflicts on git pull](/en/git-pull-merge-conflict)
- [Git Remote Repository Operations (remote/fetch/pull/push)](/en/git-remote-operations)
- [How to Create a GitHub Repository and Push for the First Time](/en/github-first-push)
- [Git Rebase Basics](/en/git-rebase-basics)
