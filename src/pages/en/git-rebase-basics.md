---
title: 'Git Rebase: How to Keep a Clean Commit History'
date: '2026-05-21'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Fixes "error: failed to push some refs" after a git rebase, using git push --force-with-lease and resolving conflicts with git rebase --continue.'
ja_tags: ['Git', 'rebase', 'バージョン管理']
en_tags: ['Git', 'rebase', 'version control']
---

## What This Covers

How to use `git rebase` to keep a linear commit history and clean up commits before opening a pull request.

## Basic Rebase

```bash
# Rebase your feature branch onto main
git switch feature/my-feature
git rebase main
```

Unlike merge, rebase replays your commits on top of the target branch — no extra merge commit.

```
# Before rebase
main:    A - B - C
feature:     D - E

# After rebase
main:    A - B - C
feature:         D' - E'
```

## Handling Conflicts

```bash
# When a conflict occurs
git rebase main
# CONFLICT (content): Merge conflict in app.js

# Fix the file, then continue
git add app.js
git rebase --continue

# To cancel and go back
git rebase --abort
```

## Interactive Rebase: Squash Commits

```bash
# Edit the last 3 commits
git rebase -i HEAD~3
```

An editor opens with options for each commit:

```
pick abc1234 add feature
pick def5678 fix typo
pick ghi9012 another fix

# Common commands:
# pick   = keep as-is
# squash = merge into previous commit
# reword = edit the commit message
# drop   = remove the commit
```

Use `squash` to combine small commits before submitting a pull request.

## After Rebase: Force Push

```bash
# Regular push will fail after rebase
git push origin feature/my-feature
# error: failed to push some refs

# Use force-with-lease (safer than --force)
git push --force-with-lease origin feature/my-feature
```

`--force-with-lease` prevents overwriting if someone else pushed to the same branch. Never force-push to shared branches like `main`.

## Key Points

- Use `git rebase --abort` if things go wrong — it fully restores the previous state
- Commit hashes change after rebase, so force push is required
- Always rebase from the feature branch, not from main
- If conflicts are too complex, `git rebase --abort` and use merge instead

## Related Articles

- [Git Branch Commands: Create, Switch, and Merge](/en/git-branch-basics)
- [How to Undo a Git Commit](/en/git-commit-undo)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
