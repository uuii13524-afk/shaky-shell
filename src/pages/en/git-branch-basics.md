---
title: 'Git Branch Commands: Create, Switch, and Merge'
date: '2026-05-08'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
---

## Basic Commands

```bash
git branch                    # List branches
git switch -c branch-name     # Create and switch
git switch branch-name        # Switch
git merge branch-name         # Merge
git branch -d branch-name     # Delete
```

## Common Workflow

```bash
git switch -c feature/new-function
git add .
git commit -m "add new function"
git switch main
git merge feature/new-function
git branch -d feature/new-function
```

## Key Points

- Use `git switch` (modern) instead of `git checkout`
- Always switch to `main` before merging

## Related Articles

- [How to Undo a Git Commit](/en/git-commit-undo)
- [How to Set Up .gitignore](/en/git-gitignore-setup)
