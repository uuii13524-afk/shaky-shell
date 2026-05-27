---
title: 'How to Use git stash to Save Work in Progress'
date: '2026-05-20'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Git', 'stash', '一時退避', 'ブランチ切り替え']
en_tags: ['Git', 'stash', 'save work', 'branch switch']
description: 'How to stash and restore uncommitted changes with git stash. Covers list, pop, apply, drop, and clear commands with practical examples.'
---
## Basic Commands

```bash
git stash              # Stash changes
git stash list         # View stash list
git stash pop          # Restore latest stash and delete it
git stash apply        # Restore latest stash (keep it in list)
git stash drop         # Delete latest stash
git stash clear        # Delete all stashes
```

## Common Workflow

```bash
# Urgent fix needed while working on a feature
git stash
git switch hotfix
# Make and commit the fix
git switch main
git stash pop
```

## Common Pitfalls

- `git stash pop` can cause conflicts if the stashed changes overlap
- New untracked files need the `-u` flag: `git stash -u`
- `git stash clear` cannot be undone — use with caution

After stashing, use [Git Branch Basics](/en/git-branch-basics) to switch branches and come back when ready.

## Related Posts

- [Git Branch Basics: Create and Switch Branches](/en/git-branch-basics)
- [How to Undo a Git Commit](/en/git-commit-undo)
- [How to Resolve Merge Conflicts After git pull](/en/git-pull-merge-conflict)
- [How to View Commit History with git log](/en/git-log-history)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
