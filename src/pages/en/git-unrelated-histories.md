---
title: 'Fix "fatal: refusing to merge unrelated histories" in Git'
date: '2026-08-27'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Merging two independently git-initialized repositories can fail with refusing to merge unrelated histories. Here is why it happens and how to fix it with --allow-unrelated-histories.'
ja_tags: ['Git', 'unrelated histories', 'git merge', 'コンフリクト解決', 'リポジトリ統合']
en_tags: ['Git', 'unrelated histories', 'git merge', 'merge conflict', 'repository merge']
---

## What I Was Trying to Do

I had a side project I'd been building in its own local repo (created with a plain `git init`, never cloned from anything), and I wanted to fold it into an existing main repository as part of its history. Instead of recreating the repo on GitHub from scratch, I figured I could just `git merge` the two local histories together directly.

As soon as I fetched the other repo and tried to merge it in, Git stopped me with:

```
fatal: refusing to merge unrelated histories
```

If you try `git pull` instead of fetch+merge, you may hit this divergent-branches warning first:

```
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint:
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
fatal: Need to specify how to reconcile divergent branches.
```

## Environment

- OS: Ubuntu 24.04 (verified in a container)
- Git: 2.43.0
- Setup: two independent local repositories, each created with its own `git init`, sharing no common ancestor commit

## What I Tried

First I just tried pulling the other repo in directly:

```bash
git pull /path/to/repo-b master
```

This stopped on the "divergent branches" warning above. Switching between `--rebase` and `--no-rebase` didn't help, because the real problem wasn't the reconciliation strategy — it was that the two repositories' commit histories had zero common ancestor to begin with.

Next I fetched explicitly and tried a plain merge:

```bash
git fetch /path/to/repo-b master
git merge FETCH_HEAD
```

Same result:

```
fatal: refusing to merge unrelated histories
```

## Root Cause

Both repositories were created with separate `git init` calls, so their very first commits have no parent-child relationship at all. Since Git 2.9, `git merge` refuses by default to merge two histories that don't share a common ancestor. This is a safety check to prevent accidentally merging two genuinely unrelated repositories together — and in my case the warning was doing exactly its job, because I really was about to merge two histories that had never been connected.

Before reaching for a flag, it's worth confirming that the histories really are unrelated on purpose, rather than something like a shallow clone or a repo that lost its `.git` folder and got re-initialized by accident. A quick way to check is comparing the very first commit of each repo:

```bash
git log --reverse --oneline | head -1
```

If the first commits of both repositories are different and neither history contains the other's commits at all, you're dealing with genuinely unrelated histories, and the merge below is the right move.

## The Fix

If merging unrelated histories is actually what you want, pass `--allow-unrelated-histories` to say so explicitly:

```bash
# Fetch the history you want to bring in
git fetch /path/to/repo-b master

# Explicitly allow merging histories with no common ancestor
git merge --allow-unrelated-histories FETCH_HEAD -m "Merge project B into project A"
```

In my case both repos happened to have a `README.md`, so the merge didn't finish cleanly — it hit a normal add/add conflict:

```
Auto-merging README.md
CONFLICT (add/add): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

That conflict has nothing to do with `--allow-unrelated-histories` specifically — it's the same kind of conflict you'd get from any ordinary merge, so it's resolved the same way:

```bash
# Look at the conflict markers
cat README.md

# Edit out the <<<<<<< / ======= / >>>>>>> markers and decide the final content

# Mark it resolved
git add README.md

# Complete the merge commit
git commit -m "Merge project B into project A"
```

## Verifying the Fix

After committing, `git log --oneline --graph --all` showed the two histories joined by a single merge commit:

```bash
git log --oneline --graph --all
```

```
*   fc79c3d Merge project B into project A
|\
| * f08ba49 Initial commit for project B
* 40e3102 Initial commit for project A
```

`git status` also came back clean with `nothing to commit, working tree clean`, confirming no conflicts were left behind.

## FAQ

**Q: Does `--allow-unrelated-histories` also resolve conflicts automatically?**
No. It only tells Git to allow the merge operation itself between histories with no common ancestor. If the actual file contents conflict, you still get a normal merge conflict that needs manual resolution before you commit.

**Q: Should I use `git pull` or `git fetch` + `git merge` here?**
When you're not sure the two histories are even related, fetching first and inspecting the result (for example with `git log FETCH_HEAD`) before merging is safer than letting `git pull` fetch and merge in one step, since a `pull` can hide the fact that something unexpected is being merged in.

**Q: Can I make Git allow this by default so I don't have to pass the flag every time?**
There's no global setting to disable this check permanently, and that's intentional — it exists specifically to stop you from accidentally merging two unrelated repositories. If you find yourself merging the same two repos repeatedly, it's worth reconsidering whether `git subtree` or `git submodule` fits your workflow better than repeated unrelated-history merges.

## Summary

- `fatal: refusing to merge unrelated histories` means Git found no common ancestor between the two histories you're trying to merge, and refused as a safety measure.
- If the merge is intentional, add `--allow-unrelated-histories`. Any conflicts from identically named files still need to be resolved manually like any other merge.
- If you see this error unexpectedly, treat it as a warning sign first — double-check that you're not about to merge two genuinely unrelated repositories before reaching for the flag.

## Related Articles

- [Fixing Merge Conflicts After git pull](/en/git-pull-merge-conflict)
- [Git Remote Operations Cheat Sheet (remote/fetch/pull/push)](/en/git-remote-operations)
- [Recovering Lost Commits with git reflog](/en/git-reflog)
- [Fixing a Rejected git push](/en/git-push-rejected-fix)
- [Creating Your First GitHub Repository and Pushing to It](/en/github-first-push)
