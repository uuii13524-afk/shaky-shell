---
title: 'How to Fix a Rejected Git Push (Non-Fast-Forward)'
date: '2026-07-19'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Git', 'github', 'push', 'rejected', 'rebase']
---

## What Happened

I'd just finished a chunk of work on a feature branch a teammate and I were both touching, and went to push like always. Instead of the usual clean push, I got an error I hadn't run into in a while. Turned out my teammate had pushed a commit of their own to the same branch a few minutes earlier, and I had no idea — I'd been happily committing on top of a branch that was already out of date.

```text
$ git push origin feature/user-settings
To github.com:example/myapp.git
 ! [rejected]        feature/user-settings -> feature/user-settings (fetch first)
error: failed to push some refs to 'github.com:example/myapp.git'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally. This is usually caused by another repository pushing
hint: to the same ref. You may want to first integrate the remote changes
hint: (e.g., 'git pull ...') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

I fixated on the word "rejected" and assumed something was wrong with my permissions, which sent me down the wrong path first.

---

## Environment

- OS: Windows 11 23H2
- Git: 2.45.2 (Git for Windows)
- Terminal: Git Bash
- Remote: GitHub (origin, over SSH)

---

## What I Tried

Because the message said "rejected," my first instinct was to suspect an access problem, so I ran `ssh -T git@github.com` to double-check my SSH key was still working → it came back with `Hi username! You've successfully authenticated`, which ruled out permissions entirely → the actual clue had been sitting right there in `(fetch first)`, but I hadn't read that part carefully, so I wasted time checking something unrelated.

Next I did what the hint actually suggested and ran `git pull`, which stopped with a different warning:

```text
$ git pull origin feature/user-settings
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint:
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.rebase interactive # rebase (interactive)
fatal: Need to specify how to reconcile divergent branches.
```

I'd never set `pull.rebase`, so Git had no default strategy to fall back on and refused to guess whether I wanted a merge or a rebase.

---

## Root Cause

The push was rejected because the remote branch had moved ahead of my local branch. Git refuses to silently overwrite history when the local and remote branches have diverged — if your local HEAD isn't an ancestor of the remote's latest commit (in other words, the push wouldn't be a fast-forward), Git blocks it rather than guessing what you meant. In my case, my teammate's push had added a commit on the remote that I didn't have locally, so our histories had diverged and the push hit this guard.

---

## The Fix

### Pull in the Remote Changes (Rebase)

```bash
git pull --rebase origin feature/user-settings
```

```text
Successfully rebased and updated refs/heads/feature/user-settings.
```

`--rebase` replays your local commits on top of the remote's latest commit instead of creating a merge commit. That keeps the history linear, which is usually what you want on a feature branch a couple of people are sharing.

### Push Again Once You're Rebased

```bash
git push origin feature/user-settings
```

```text
Enumerating objects: 7, done.
To github.com:example/myapp.git
   a1b2c3d..9f8e7d6  feature/user-settings -> feature/user-settings
```

Now that your local HEAD includes the remote's latest commit, the push is a fast-forward again and goes through cleanly.

### If You Hit a Conflict

If you and your teammate touched the same lines, the rebase can stop partway through with something like this:

```text
CONFLICT (content): Merge conflict in src/settings.js
error: could not apply 9f8e7d6... update user settings form
```

Resolve the conflicting lines by hand, `git add` the file, and run `git rebase --continue` to pick the rebase back up.

---

## Where I Got Tripped Up

- I read "rejected" and jumped straight to a permissions problem, when the real clue — `(fetch first)` — was right there in the same line. Reading the whole hint block would have saved me the detour.
- I'd never configured `pull.rebase`, so a plain `git pull` stopped and demanded I choose merge or rebase before it would do anything. Setting `git config --global pull.rebase true` once means I never get asked again.
- Mid-rebase, when the conflict showed up, I almost mashed `git rebase --abort` out of panic — that would have rolled back my own commits along with the conflict, not just fixed the conflict. Better to slow down and resolve just the conflicting file.
- I came dangerously close to running `git push --force` to just muscle past the rejection. That would have wiped my teammate's commit off the remote entirely. Force-pushing to a branch someone else is also working on is exactly the mistake that message is there to prevent.

---

## FAQ

**Q: What's the difference between "rejected (fetch first)" and "rejected (non-fast-forward)"?**
They both mean the same underlying thing: your local branch and the remote branch have diverged, so the push can't be applied as a fast-forward. The exact wording depends on your Git version and what you were doing, but the fix is identical either way — run `git pull` (or `git pull --rebase`) to bring in the remote's commits, then push again.

**Q: Is it ever okay to use `git push --force`?**
On a branch only you touch, sure — rewriting history and force-pushing is normal. On a shared branch, though, a plain `--force` can silently delete someone else's commits. Use `git push --force-with-lease` instead on shared branches; it only overwrites the remote if it's still in the state you last saw, so it fails loudly instead of eating a teammate's work.

**Q: Where do I check or change my `pull.rebase` setting?**
Run `git config pull.rebase` to see the current value. Setting `git config --global pull.rebase true` makes every future `git pull` rebase by default, so you won't get stopped and asked to choose every time your branches diverge.

---

## Related Articles

- [How to Resolve a Git Merge Conflict After git pull](/en/git-pull-merge-conflict)
- [Git Rebase Basics: How to Use It](/en/git-rebase-basics)
- [Git Branch Commands: Create, Switch, and Merge](/en/git-branch-basics)
- [How to Push to GitHub for the First Time](/en/github-first-push)
- [How to Recover Lost Commits with git reflog](/en/git-reflog)
