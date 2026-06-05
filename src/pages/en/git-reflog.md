---
title: 'How to Recover Lost Commits with git reflog'
date: '2026-06-04'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['git', 'reflog', 'コミット復元', 'バージョン管理']
en_tags: ['git', 'reflog', 'recover commits', 'version control']
description: 'Learn how to recover lost commits using git reflog after a git reset --hard or rebase gone wrong. Step-by-step guide with examples.'
---

## What I Wanted to Do

I accidentally wiped commits with `git reset --hard` and panicked thinking they were gone for good.
Turns out `git reflog` records every HEAD movement — even "deleted" commits are still recoverable.

## What is git reflog?

`git reflog` shows the full history of where HEAD has pointed, including commits that no longer appear in `git log`.

```bash
git reflog
```

Sample output:

```
a1b2c3d HEAD@{0}: reset: moving to HEAD~2
e4f5g6h HEAD@{1}: commit: add form validation
i7j8k9l HEAD@{2}: commit: implement login feature
```

## How to Recover a Lost Commit

### Step 1: Find the target commit in reflog

```bash
git reflog
```

Note the hash of the commit you want to restore (e.g. `e4f5g6h`).

### Step 2: cherry-pick the commit back

If you only need that one specific commit:

```bash
git cherry-pick e4f5g6h
```

### Step 3: reset to that point

If you want to restore everything up to that commit:

```bash
git reset --hard e4f5g6h
```

## Recovering a Lost stash Entry

If you've lost track of a stash, reflog can help there too:

```bash
git reflog show stash
```

Or find all dangling commits with `fsck`:

```bash
git fsck --lost-found
```

## Things That Tripped Me Up

- Reflog entries expire after 90 days by default — act fast if you need to recover something old
- Reflog is local only; a fresh clone won't have the history
- If you already force-pushed the reset, the remote is gone — only local reflog can help
- Work on `--orphan` branches sometimes doesn't show up in reflog

## Related Articles

- [How to Undo a Git Commit (Before and After Push)](/en/git-commit-undo)
- [git cherry-pick: Apply a Specific Commit to Another Branch](/en/git-cherry-pick)
- [How to Use git stash to Save Work in Progress](/en/git-stash-usage)
- [How to View Commit History with git log](/en/git-log-history)
- [Git Rebase: How to Keep a Clean Commit History](/en/git-rebase-basics)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
