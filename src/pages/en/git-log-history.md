---
title: 'How to View Commit History with git log'
date: '2026-05-17'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Learn how to use git log to view commit history. Covers --oneline, --graph, --since, and other options for readable log output.'
---

## Basic Usage

```bash
git log --oneline              # One line per commit (most useful)
git log --oneline -10          # Latest 10 commits
git log --oneline --graph --all  # Graph view of all branches
git log -p                     # Show diffs as well
git show <commit-id>           # Details of a specific commit
```

## Search and Filter

```bash
git log --author="name"
git log --since="2026-01-01"
git log --grep="keyword"
```

## Check Diffs

```bash
git diff
git diff HEAD~1
```

## Key Points

- Press `q` to exit `git log`
- `--oneline` is the most readable option

If you want to bring a specific commit to another branch, see [How to Use git cherry-pick to Apply a Specific Commit](/en/git-cherry-pick).

## Related Articles

- [How to Undo a Git Commit](/en/git-commit-undo)
- [How to Resolve Merge Conflicts from git pull](/en/git-pull-merge-conflict)
- [How to Temporarily Save Work with git stash](/en/git-stash-usage)
- [Git Branch Basics: Create and Switch Branches via CLI](/en/git-branch-basics)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
