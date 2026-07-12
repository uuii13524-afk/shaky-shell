---
title: 'git diff Command Guide: How to Review Changes in Git'
date: '2026-07-12'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Git', 'git diff', 'diff', 'staging area', 'commit comparison']
description: 'Complete guide to the git diff command. Compare working tree vs staging, review staged changes, diff between commits and branches, and filter by file.'
---

## Quick Answer

```bash
# Diff between working tree and staging area
git diff

# Diff of staged changes (before committing)
git diff --staged

# Compare two specific commits
git diff <commit1> <commit2>
```

---

## What You're Trying to Do

Before committing, you want to see exactly what changed. `git status` only lists filenames — to see line-by-line changes you need `git diff`.

It's also common to get confused about the difference between staged and unstaged changes when using `git diff`.

---

## Environment

- Git 2.30 or later
- OS: Linux / macOS / Windows (including WSL2)

---

## Solution

### Basic: View Changes in the Working Tree

```bash
git diff
```

This shows the difference between the last staged state (`git add`) and your current working tree. Use it to review changes before staging them.

### View Staged Changes (--staged / --cached)

```bash
git diff --staged
# or
git diff --cached
```

After running `git add`, use this to confirm exactly what will be included in your next commit.

### Diff a Specific File

```bash
git diff src/app.js

# multiple files
git diff src/app.js src/index.js
```

### Compare Commits

```bash
# Diff against the previous commit
git diff HEAD~1 HEAD

# Diff between two specific commits
git diff a1b2c3d e4f5g6h
```

### Compare Branches

```bash
# Diff current branch against main
git diff main

# Diff feature branch against main
git diff main..feature/login
```

### Show a Summary of Changes (--stat)

```bash
git diff --stat
```

Example output:
```
 src/app.js   | 12 +++++++-----
 src/index.js |  4 ++--
 2 files changed, 10 insertions(+), 6 deletions(-)
```

Handy for getting a quick overview of which files changed before diving into details.

### Word-Level Diff (--word-diff)

```bash
git diff --word-diff
```

Highlights only the changed words instead of whole lines — useful for reviewing prose files like Markdown.

### Diff Against a Remote Branch

```bash
git fetch origin
git diff origin/main
```

You need to `git fetch` first, otherwise you'll be comparing against a stale copy of the remote branch.

---

## Common Errors

### `git diff` Shows Nothing

```bash
git diff
# (no output)
```

If you've already run `git add`, `git diff` returns nothing because there's no difference between the staged snapshot and the working tree. Check the staged changes instead:

```bash
git diff --staged
```

### Binary Files Only Show `Binary files differ`

```bash
Binary files a/image.png and b/image.png differ
```

Git can't produce a meaningful text diff for binary files like images or compiled artifacts. The `--text` flag forces a text diff, but the output is usually unreadable.

### Diff Is Full of Line-Ending (CRLF/LF) Changes

Common in mixed Windows / Linux-macOS environments.

```bash
git config core.autocrlf input   # Linux/macOS
git config core.autocrlf true    # Windows
```

Setting this normalizes line endings going forward.

### The Pager Opens and Is Hard to Navigate

By default, `git diff` output is piped through a pager like `less`.

```bash
# Print straight to stdout without a pager
git --no-pager diff

# Disable the pager permanently
git config --global core.pager cat
```

---

## FAQ

**Q: What's the difference between `git diff` and `git status`?**
`git status` only lists which files changed. `git diff` shows the actual line-by-line content changes.

**Q: How do I see both staged and unstaged changes together?**
Compare `HEAD` directly against the working tree to see everything at once.

```bash
git diff HEAD
```

**Q: Can I view only added lines or only removed lines?**
In the diff output, `-` marks removed lines and `+` marks added lines. You can filter with `grep`:

```bash
git diff | grep "^-"
```

**Q: Can I limit the diff to a specific directory?**
Yes, pass a path to scope the diff to that directory.

```bash
git diff src/components/
```

**Q: Can I view diffs in a nicer external tool?**
Configure `difftool` to open diffs in an editor like VSCode.

```bash
git config --global diff.tool vscode
git config --global difftool.vscode.cmd 'code --wait --diff $LOCAL $REMOTE'
git difftool
```

---

## Related Articles

- [How to Use git stash](/en/git-stash-usage)
- [git rebase Basics](/en/git-rebase-basics)
- [Resolving Merge Conflicts with git pull](/en/git-pull-merge-conflict)
- [Viewing Commit History with git log](/en/git-log-history)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
