---
title: 'How to Resolve Merge Conflicts After git pull'
date: '2026-05-13'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Git', 'コンフリクト', 'マージ', 'pull']
en_tags: ['Git', 'merge conflict', 'pull', 'resolve']
description: 'How to identify and resolve merge conflicts that occur after git pull. Step-by-step guide from spotting conflict markers to committing the fix.'
---
## Symptom

```
CONFLICT (content): Merge conflict in filename
Automatic merge failed; fix conflicts and then commit the result.
```

## Resolution Steps

### 1. Check Which Files Have Conflicts

```bash
git status
```

### 2. Open the File and Edit

```
<<<<<<< HEAD
Your local changes
=======
Incoming changes
>>>>>>> branch-name
```

Remove the `<<<<<<<`, `=======`, and `>>>>>>>` markers and keep the correct content.

### 3. Commit

```bash
git add .
git commit -m "resolve conflict"
```

## Abort the Merge

```bash
git merge --abort
```

## Common Pitfalls

- Don't commit with conflict markers still in the file — it will break the code
- Pull frequently to keep conflicts small and manageable

To avoid conflicts altogether, [git rebase Basics](/en/git-rebase-basics) lets you replay your commits on top of the latest remote branch.

## Related Posts

- [Git Branch Basics: Create and Switch Branches](/en/git-branch-basics)
- [How to Undo a Git Commit](/en/git-commit-undo)
- [How to Use git stash to Save Work in Progress](/en/git-stash-usage)
- [How to View Commit History with git log](/en/git-log-history)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
