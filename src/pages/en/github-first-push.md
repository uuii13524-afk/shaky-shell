---
title: 'How to Create a GitHub Repository and Push for the First Time'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Git', 'GitHub', 'push', '初回']
en_tags: ['Git', 'GitHub', 'push', 'first push']
description: 'Step-by-step guide to creating a GitHub repository and pushing a local project to it for the first time.'
---
## What I Wanted to Do

Push a local project to GitHub for the first time.

## Steps

### 1. Create a Repository on GitHub

1. Log in to github.com
2. Top right "+" → "New repository"
3. Enter a repository name → "Create repository"

### 2. Initialize Git Locally

```bash
git init
git add .
git commit -m "first commit"
```

### 3. Connect to GitHub and Push

```bash
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

## Common Pitfalls

- If you add a README when creating the repo on GitHub, the first push will cause a conflict
- Password authentication is deprecated — use a Personal Access Token (PAT) or SSH key

Setting up SSH authentication means you never have to type a password. See [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github).

## Related Posts

- [How to Install Git on Windows and Configure It](/en/windows-git-install)
- [How to Undo a Git Commit](/en/git-commit-undo)
- [Git Branch Basics: Create and Switch Branches](/en/git-branch-basics)
- [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
