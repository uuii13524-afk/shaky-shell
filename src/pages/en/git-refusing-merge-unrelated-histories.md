---
title: 'Fix "fatal: refusing to merge unrelated histories" on git pull'
date: '2026-10-05'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git pull stops with "refusing to merge unrelated histories" when a local repo and a remote branch have no common ancestor. Here is how to confirm the cause with git merge-base and fix it with --allow-unrelated-histories or rebase.'
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## What I Was Trying to Do

I had started a project locally with `git init` and a first commit. Separately, a remote repository already existed with a single commit that only added a `LICENSE` file, which is what you get when you create a GitHub repo with "Add a license". I wanted to pull the remote `main` into my local `main`.

```bash
git pull origin main
```

With no `pull.rebase` setting, Git first stopped with this hint:

```text
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint: 
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
fatal: Need to specify how to reconcile divergent branches.
```

Choosing a plain merge with `--no-rebase` produced the real error:

```bash
git pull --no-rebase origin main
```

```text
From /path/to/remote
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

## Environment

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- Setup: a local repo (one commit, "local first") and a bare remote repo (one commit, "license"), both on `main`
- How I tested: I reproduced this in a scratch directory with two separately created repositories. I did not run it against a real hosted repository.

## What I Tried

My first suspicion was a wrong remote URL or branch name. `git remote -v` and `git branch -a` both looked correct, so I moved on.

Next I ran `git fetch` on its own. It succeeded and created `origin/main`, so the connection and credentials were fine. The failure happened only at the merge step.

```bash
git fetch origin
git log --oneline origin/main
```

```text
2bf58e3 license
```

The local log showed:

```text
2424710 local first
```

Each side had one commit and neither contained the other. That pointed to a missing common ancestor, so I checked with `git merge-base`:

```bash
git merge-base HEAD origin/main
echo "rc=$?"
```

```text
rc=1
```

No output and exit code 1: there is no merge base. To see why, I listed the root commits (commits with no parent) of both histories:

```bash
git rev-list --max-parents=0 HEAD origin/main
```

```text
2424710fe4cde8737592c4f44c4c8bc08096480e
2bf58e398abe768a44485b7af3d2fa203abf998d
```

Two different root commits. Histories that come from the same repository share one root, so these were two histories created independently.

## Cause

The local repo and the remote repo each created their own root commit. Git merges by finding the common ancestor of the two branches and doing a three-way merge from there. With no common ancestor, there is no base to diff against.

Since Git 2.9, `git merge` and `git pull` refuse this case by default and print `refusing to merge unrelated histories`. It is a guard against accidentally combining two unrelated projects, for example by pointing `origin` at the wrong URL. If you really do want to combine them, you have to say so explicitly.

## Fix

There are two ways to join the histories. I ran both on the scratch repos.

### Option 1: Merge with --allow-unrelated-histories

```bash
git pull --no-rebase --allow-unrelated-histories --no-edit origin main
```

`--allow-unrelated-histories` lifts the refusal, and `--no-edit` skips the commit message editor.

```text
From /path/to/remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 LICENSE | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 LICENSE
```

If both sides have a file with the same path, you get a normal merge conflict. Here `README.md` and `LICENSE` did not overlap, so it merged cleanly.

### Option 2: Rebase onto the remote

If you prefer a linear history, fetch and rebase. For this test I reset the local repo back to the single "local first" commit first.

```bash
git fetch origin
git rebase origin/main
```

```text
Successfully rebased and updated refs/heads/main.
```

Rebase does not need `--allow-unrelated-histories`. It replays your local commits on top of `origin/main`.

## Verification

After option 1:

```bash
git log --oneline --graph
```

```text
*   059c014 Merge branch 'main' of /path/to/remote
|\  
| * 2bf58e3 license
* 2424710 local first
```

After option 2 the history is a straight line:

```text
* 2116477 local first
* 2bf58e3 license
```

In both cases `ls` showed `README.md` and `LICENSE`.

## Gotchas

- Without `pull.rebase` configured, the first `git pull` stops at the "divergent branches" hint. The unrelated-histories error only shows up after you pick merge or rebase.
- Rebase works on unrelated histories without any extra flag, while merge needs `--allow-unrelated-histories`. That difference is easy to miss.
- Rebasing rewrites the hashes of your local commits. On a branch other people have already pulled, a merge is safer.

## Summary

- `refusing to merge unrelated histories` means the two branches share no ancestor. `git merge-base HEAD origin/main` returning nothing with exit code 1 confirms it.
- Two results from `git rev-list --max-parents=0 HEAD origin/main` mean two independently created histories.
- If you want to combine them, use `git pull --allow-unrelated-histories` or `git rebase origin/main`. If you did not expect it, check that `origin` points to the right repository.

## FAQ

**Q: Is `--allow-unrelated-histories` dangerous?**
It is if you are about to mix two unrelated projects by mistake. Check the remote URL first. If you intend to combine the histories, it is fine.

**Q: How do I avoid this next time?**
When you create the remote first, create it empty (no README or LICENSE) and push your local history to it. When the remote already has content, `git clone` it and start working from there.

**Q: Merge or rebase?**
For a new personal repo, rebase gives a cleaner linear history. For a branch others have already pulled, merge is safer because existing hashes do not change.

## Related Articles

- [Fix git push "rejected" Errors](/en/git-push-rejected-fix)
- [Resolving Merge Conflicts on git pull](/en/git-pull-merge-conflict)
- [Git Remote Operations: remote, fetch, pull, push](/en/git-remote-operations)
- [Your First Push to GitHub](/en/github-first-push)
- [git rebase Basics](/en/git-rebase-basics)
