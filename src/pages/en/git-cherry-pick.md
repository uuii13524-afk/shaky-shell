---
title: 'git cherry-pick: Apply a Specific Commit to Another Branch'
date: '2026-05-21'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Git', 'cherry-pick', 'バージョン管理']
en_tags: ['Git', 'cherry-pick', 'version control']
---

## What This Covers

How to use `git cherry-pick` to apply a specific commit from one branch to another — without merging the whole branch.

## Basic Usage

```bash
# Find the commit hash
git log --oneline

# Apply a specific commit to the current branch
git cherry-pick abc1234
```

Use `git log --oneline` to find the hash of the commit you want to bring over.

## Cherry-pick Multiple Commits

```bash
# Pick multiple commits individually
git cherry-pick abc1234 def5678

# Pick a range of consecutive commits (excludes abc1234, includes ghi9012)
git cherry-pick abc1234..ghi9012
```

The range `A..B` excludes A and includes B.

## Handling Conflicts

```bash
# When a conflict occurs
git cherry-pick abc1234
# CONFLICT (content): Merge conflict in app.js

# Fix the file, then continue
git add app.js
git cherry-pick --continue

# To cancel and go back
git cherry-pick --abort
```

Same flow as rebase: fix the conflict → `git add` → `--continue`.

## Undoing a Cherry-pick

```bash
# Create a revert commit to undo the cherry-picked changes (if already pushed)
git revert abc1234

# Remove the cherry-pick commit entirely (only if not pushed yet)
git reset --hard HEAD~1
```

If you've already pushed, use `git revert` to create a safe undo commit instead of `reset`.

## Key Points

- `git log --oneline` is the quickest way to find commit hashes
- The cherry-picked commit gets a new hash — it's recorded as a new commit
- The range `A..B` excludes A and includes B (same behavior as rebase)
- Cherry-picking the same change twice often causes conflicts
- For pushed commits, always use `revert` instead of `reset`

## Related Articles

- [Git Branch Commands: Create, Switch, and Merge](/en/git-branch-basics)
- [How to Undo a Git Commit](/en/git-commit-undo)
- [Git Rebase: How to Keep a Clean Commit History](/en/git-rebase-basics)
