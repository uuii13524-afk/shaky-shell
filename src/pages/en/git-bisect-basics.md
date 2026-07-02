---
title: 'How to Find the Commit That Introduced a Bug with git bisect'
date: '2026-07-02'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['git', 'bisect', 'デバッグ', 'バージョン管理']
en_tags: ['git', 'bisect', 'debugging', 'version control']
description: 'Learn how to use git bisect to binary-search your commit history and pinpoint exactly which commit introduced a bug, including the automated bisect run workflow.'
---

## Quick Answer

```bash
git bisect start
git bisect bad              # current commit has the bug
git bisect good v1.0.0      # this commit was known to work
```

Git checks out a commit halfway between the two — test it, then mark it `good` or `bad` and repeat.

---

## What You're Trying to Do

A bug crept into the codebase somewhere along the way, but you have no idea which commit introduced it.
With hundreds of commits in the history, checking each one by hand isn't realistic.
`git bisect` performs a binary search over your commit history to find the exact commit efficiently.

---

## Environment

- Git 2.20 or later (if you want to use `bisect run` with an automated test script)
- Verified on Git 2.39

---

## Solution

### Step 1: Start bisecting

```bash
git bisect start
```

### Step 2: Mark the current commit as bad

```bash
git bisect bad
```

### Step 3: Mark a known-good commit

```bash
git bisect good v1.0.0
```

You can pass a tag, commit hash, or branch name. This defines the search range, and Git automatically checks out the commit in the middle.

### Step 4: Test and mark good or bad

Test whether the bug reproduces on the checked-out commit, then run one of:

```bash
git bisect bad   # the bug reproduced
git bisect good  # the bug did not reproduce
```

Repeat this process — Git narrows the range each time until it identifies the exact commit that introduced the bug.

### Step 5: Finish up

```bash
git bisect reset
```

This returns you to your original branch and commit.

### Automating it with git bisect run

Instead of testing manually, you can hand the whole process to a test script.

```bash
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
git bisect run npm test
```

If the test fails (non-zero exit code) the commit is marked `bad`; if it succeeds (exit code 0) it's marked `good` — fully automatic.

---

## Common Errors

### fatal: bad revision '...'

The tag or commit you specified doesn't exist. Check with `git log --oneline` or `git tag` that the reference actually exists.

### Bisect lands on a commit that doesn't even build

Exclude that specific commit from the search with:

```bash
git bisect skip
```

### git bisect run gives inconsistent results

Git treats exit code 125 as "untestable" (e.g. the build itself failed) and skips that commit automatically. Make sure your test script returns 125 when the build fails, rather than a generic failure code, to keep the bisect accurate.

---

## FAQ

**Q: Can I stop a bisect session partway through?**
Yes — `git bisect reset` cancels the session at any point and returns you to your original branch.

**Q: What if I mark a commit good or bad incorrectly?**
Run `git bisect log` to see the judgment history. You can edit that log and replay it with `git bisect replay`.

**Q: Does it scale to a huge number of commits?**
Yes — since it's a binary search, even 1000 commits need only about log2(1000) ≈ 10 tests to pinpoint the culprit.

**Q: Can I bisect commits that only exist on a remote?**
You need to fetch them locally first — bisect only works on commits already present in your local repository.

---

## Related Articles

- [How to View Commit History with git log](/en/git-log-history)
- [How to Recover Lost Commits with git reflog](/en/git-reflog)
- [git cherry-pick: Apply a Specific Commit to Another Branch](/en/git-cherry-pick)
- [How to Undo a Git Commit](/en/git-commit-undo)

## Recommended VPS / Hosting

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
