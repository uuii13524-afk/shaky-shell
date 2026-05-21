---
title: 'How to Undo a Git Commit (Before and After Push)'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
---

## Solutions by Situation

### 1. Undo the last commit but keep file changes

```
git reset --soft HEAD~1
```

### 2. Undo the last commit and discard all changes

```
git reset --hard HEAD~1
```

**This cannot be undone.**

### 3. Fix the commit message only

```
git commit --amend -m "New message"
```

### 4. Undo after push (safe method)

```
git revert HEAD
```

Creates a new commit that reverses the previous one. Safe for shared repos.

## Key Points

- Use `--soft` to keep changes, `--hard` to discard everything
- After pushing, use `git revert` instead of `git reset`

## Related Articles

- [How to Create Git Branches](/en/git-branch-basics)
- [How to Set Up .gitignore](/en/git-gitignore-setup)
