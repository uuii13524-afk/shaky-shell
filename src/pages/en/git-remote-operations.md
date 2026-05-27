---
title: 'Git Remote Repository Operations (remote/fetch/pull/push)'
date: '2026-05-14'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Git', 'リモートリポジトリ', 'push', 'pull', 'fetch']
en_tags: ['Git', 'remote repository', 'push', 'pull', 'fetch']
description: 'A reference for git remote, fetch, pull, and push commands. Covers checking, adding, and changing remote URLs and understanding the difference between fetch and pull.'
---
## Check Remote Repositories

```bash
git remote -v
```

## Add, Change, or Remove a Remote

```bash
git remote add origin URL
git remote set-url origin URL
git remote remove origin
```

## fetch vs pull vs push

```bash
git fetch origin        # Download remote changes (no merge)
git pull origin main    # fetch + merge
git push                # Push local commits to remote
git push -u origin main # Push and set upstream branch
```

## Common Pitfalls

- Never use `git push --force` on a shared repository
- The `-u` flag sets the upstream so future `git push` works without arguments

If you're using SSH for GitHub authentication, set the remote URL to the SSH format. See [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github).

## Related Posts

- [How to Push Your First Repository to GitHub](/en/github-first-push)
- [How to Resolve Merge Conflicts After git pull](/en/git-pull-merge-conflict)
- [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github)
- [Git Branch Basics: Create and Switch Branches](/en/git-branch-basics)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
