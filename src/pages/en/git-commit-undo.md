---
title: 'How to Undo a Git Commit (Before and After Push)'
date: '2026-05-06'
category: 'Git'
---

## Symptoms

You committed the wrong files. You made a typo in the commit message. You want to undo a commit before pushing.

## Solutions by Situation

### 1. Undo the last commit but keep file changes

```
git reset --soft HEAD~1
```

Only the commit is removed. Your file changes stay staged.

### 2. Undo the last commit and discard all changes

```
git reset --hard HEAD~1
```

Both the commit and file changes are removed. **This cannot be undone.**

### 3. Fix the commit message only

```
git commit --amend -m "New message"
```

### 4. Undo after push (safe method)

```
git revert HEAD
```

Creates a new commit that reverses the previous one. History is preserved — safe for shared repos.

## Verify Your History

```
git log --oneline
```

## Key Points

- Use `--soft` to keep changes, `--hard` to discard everything
- After pushing, use `git revert` instead of `git reset`
- `HEAD~1` means one commit back. `HEAD~2` means two commits back.

## Related Articles

- [How to Create and Switch Git Branches](/posts/git-branch-basics)
- [How to Set Up .gitignore](/posts/git-gitignore-setup)
- [How to Read Git Log History](/posts/git-log-history)
