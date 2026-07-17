---
title: 'How to Fix Git Detached HEAD State'
date: '2026-07-16'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Git', 'detached-head', 'branch', 'checkout']
---

## What Happened

I wanted to peek at an old commit, so I ran `git checkout <hash>` and jumped straight to it. I poked around, made a couple of quick commits without thinking much about it, then ran `git switch main` to get back to my main branch. When I checked `git log` afterward, the commits I'd just made were nowhere to be found. Scrolling back up in my terminal, I found this message from when I'd first jumped to that commit:

```text
Note: switching to '3f2a1b9'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

HEAD is now at 3f2a1b9 fix: update config parser
```

I hadn't actually read that warning carefully the first time, which is exactly what got me into trouble.

---

## Environment

- OS: Ubuntu 22.04 / macOS 14 (Sonoma)
- Git: 2.42.0
- Editor: VS Code 1.89
- Shell: bash 5.1

---

## What I Tried

My first move was just to switch back to main and hope for the best, since I'd already made the commits and figured Git would keep them around somewhere. Running `git switch main` printed this:

```text
Warning: you are leaving 1 commit behind, not connected to
any of your branches:

  3f2a1b9 fix: update config parser

If you want to keep it by creating a new branch, this may be a good time
to do so with:

 git branch <new-branch-name> 3f2a1b9

Switched to branch 'main'
```

I skimmed past that warning too, figuring "I'm back on main, so it's fine" → then I ran `git log` and the commit I'd just made was gone from the history → it turned out the commit hadn't actually been deleted, it just wasn't reachable from any branch anymore, so `git log`'s normal output didn't show it at all.

---

## Root Cause

A Git branch is really just a named pointer to a specific commit. In detached HEAD state, HEAD points directly at a commit instead of going through a branch name. Any commit you make in that state isn't attached to any branch, so it becomes unreachable the moment you check out something else. Git doesn't delete unreachable commits right away — they still show up in the reflog and stay recoverable for a while — but they'll eventually get swept up by `git gc` if nothing ever points to them.

---

## The Fix

### If You're Still in Detached HEAD, Create a Branch Now

```bash
git switch -c recovered-work
```

```text
Switched to a new branch 'recovered-work'
```

Giving the commit a real branch name attaches a proper ref to it. Once it has a ref, it survives branch switches just like any other commit.

### If You've Already Switched Away, Dig It Up with Reflog

```bash
git reflog
```

```text
3f2a1b9 HEAD@{0}: commit: fix: update config parser
a1b2c3d HEAD@{1}: checkout: moving from main to 3f2a1b9
7e6d5c4 HEAD@{2}: checkout: moving from feature/parser to main
```

`git reflog` tracks every place HEAD has pointed, so the commit you made in detached HEAD state is still listed even if `git log` can't find it. Once you spot the hash you want (here, `3f2a1b9`), point a new branch at it:

```bash
git branch recovered-work 3f2a1b9
git branch
```

```text
  main
* recovered-work
```

That gives you a branch pointing at the commit that looked like it had vanished.

---

## Where I Got Tripped Up

- I'd made two commits in detached HEAD state and `git log` showed them just fine at the time, so nothing looked wrong until I ran `git status` and noticed it said `HEAD detached at 3f2a1b9`.
- The warning that scrolled by after `git switch main` was easy to miss — it only stays on screen for a second before more output pushes it up. I now make a habit of reading it immediately instead of scrolling back later.
- `git reflog` output can get long fast, and it wasn't obvious at a glance which entry was the one I wanted. Filtering with `git reflog | grep "fix: update config parser"` made it much easier to spot.
- I tried `git branch recovered-work 3f2a1b9` and hit `fatal: A branch named 'recovered-work' already exists`, because a teammate already had a local branch with that name. Had to pick something more specific.
- Reflog entries don't stick around forever — by default, unreachable commits get cleaned up by `git gc` after about 30 days. If you don't recover the commit fairly soon, it can genuinely disappear for good.

---

## FAQ

**Q: How do I get out of Git's detached HEAD state?**
Run `git switch main` (or whatever branch you want) to move back onto a real branch. If you've made commits you care about while detached, create a branch for them first with `git switch -c new-branch-name` — otherwise you'll get the same "leaving commits behind" warning I did.

**Q: How do I avoid ending up in detached HEAD when checking out a commit?**
Checking out a raw hash or tag with `git checkout <hash>` always puts you in detached HEAD — that's expected Git behavior. If you want a branch instead, use `git checkout -b new-branch-name <hash>` or `git switch -c new-branch-name <hash>`, which creates a proper branch pointing at that commit right away.

**Q: How long do git reflog entries actually last?**
By default, reflog entries for commits still reachable from a branch expire after 90 days, and entries for unreachable commits expire after 30 days, at which point `git gc` can clean them up. You can check or change these windows with `git config gc.reflogExpire` and `git config gc.reflogExpireUnreachable`.

---

## Related Articles

- [Git Branch Commands: Create, Switch, and Merge](/en/git-branch-basics)
- [How to Recover Lost Commits with git reflog](/en/git-reflog)
- [How to Undo a Git Commit](/en/git-commit-undo)
- [Stashing Work in Progress with git stash](/en/git-stash-usage)
