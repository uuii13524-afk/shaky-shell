---
title: 'How to Install Git on Windows and Configure It'
date: '2026-05-07'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Git', 'Windows', 'インストール', '初期設定']
en_tags: ['Git', 'Windows', 'install', 'initial setup']
description: 'Step-by-step guide to installing Git for Windows and running the initial git config setup including username, email, and default branch name.'
---
## Steps

### 1. Download Git

Go to https://git-scm.com and click "Download for Windows".

### 2. Install

Key options during setup:
- Change the default branch name to `main`
- Select "Git from the command line and also from 3rd-party software"

### 3. Verify the Installation

```bash
git --version
```

### 4. Initial Configuration

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## Common Pitfalls

- Restart the terminal after installation
- Without setting `user.name` and `user.email`, commits will throw an error
- Set the default branch to `main` during install (not `master`)

After installing Git, set up SSH authentication so you don't need to enter a password every time. See [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github).

## Related Posts

- [How to Push Your First Repository to GitHub](/en/github-first-push)
- [How to Undo a Git Commit](/en/git-commit-undo)
- [Git Branch Basics: Create and Switch Branches](/en/git-branch-basics)
- [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
