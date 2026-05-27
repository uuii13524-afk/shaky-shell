---
title: 'Generate an SSH Key and Add It to GitHub'
date: '2026-05-11'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['SSH', 'GitHub', 'Git', '認証']
en_tags: ['SSH', 'GitHub', 'Git', 'authentication']
description: 'Step-by-step guide to generating an SSH key pair and registering the public key on GitHub. Includes connection verification and switching a remote URL to SSH.'
---
## Steps

### 1. Generate an SSH Key

```bash
ssh-keygen -t ed25519 -C "your-github-email@example.com"
```

### 2. View the Public Key

```bash
cat ~/.ssh/id_ed25519.pub
```

### 3. Add the Public Key to GitHub

1. GitHub → Settings → "SSH and GPG keys"
2. "New SSH key" → paste the public key

### 4. Test the Connection

```bash
ssh -T git@github.com
```

### 5. Switch Your Remote URL to SSH

```bash
git remote set-url origin git@github.com:USERNAME/REPO.git
```

## Common Pitfalls

- Add the **public** key (`.pub`) to GitHub — never share the private key
- Existing repositories keep using HTTPS until you update the remote URL

SSH keys work for VPS connections too. You can reuse the same key or manage separate keys per host with [How to Use ~/.ssh/config to Simplify SSH Connections](/en/ssh-config-file).

## Related Posts

- [How to Push Your First Repository to GitHub](/en/github-first-push)
- [How to Install Git on Windows and Configure It](/en/windows-git-install)
- [GitHub Actions: Basic Auto-Deploy Setup](/en/github-actions-basic)
- [Git Remote Repository Operations](/en/git-remote-operations)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
