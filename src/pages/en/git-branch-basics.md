---
title: 'Git Branch Commands: Create, Switch, and Merge'
date: '2026-05-08'
category: 'Git'
---

## Basic Commands

```bash
git branch                    # List branches
git switch -c branch-name     # Create and switch
git switch branch-name        # Switch to existing branch
git merge branch-name         # Merge into current branch
git branch -d branch-name     # Delete branch
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

## Remote Branch Operations

```bash
git branch -r                              # List remote branches
git push -u origin branch-name             # Push branch to remote
git switch -c branch origin/branch-name    # Pull remote branch locally
```

## Key Points

- Use `git switch` (modern) instead of `git checkout` (older syntax)
- Always switch to `main` before merging
- Branch names cannot contain spaces — use `-` or `/` instead
- Use `-D` to force-delete an unmerged branch

## Related Articles

- [How to Create Your First GitHub Repository and Push](/en/github-actions-basic)
- [How to Undo a Git Commit](/en/git-commit-undo)
- [Cloudflare Pages Auto-Deploy Not Working](/en/cloudflare-pages-deploy-not-working)
