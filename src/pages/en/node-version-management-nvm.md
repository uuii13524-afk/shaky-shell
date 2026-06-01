---
title: 'Manage Node.js Versions with nvm (Windows and Mac)'
date: '2026-05-07'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Node.js', 'nvm', 'バージョン管理', 'Windows', 'Mac']
en_tags: ['Node.js', 'nvm', 'version management', 'Windows', 'Mac']
description: 'How to install and switch between Node.js versions using nvm on Windows and Mac. Includes .nvmrc setup for per-project version pinning.'
---
## What I Wanted to Do

Switch Node.js versions per project without reinstalling Node.js each time.

## Windows (nvm-windows)

Download `nvm-setup.exe` from https://github.com/coreybutler/nvm-windows/releases

```bash
nvm install 22
nvm use 22
```

## Mac

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 22
nvm use 22
```

## Common Commands

```bash
nvm install 22          # Install Node.js 22
nvm use 22              # Switch to version 22
nvm ls                  # List installed versions
nvm alias default 22    # Set default version
```

## Common Pitfalls

- On Windows, use `nvm-windows` — the original nvm is Unix-only
- Uninstall any existing Node.js before installing nvm-windows
- Without `nvm alias default`, the version resets every time you open a new terminal

If npm still doesn't work after switching versions on Windows, see [npm Command Not Working on Windows](/en/windows-npm-not-working).

## Related Posts

- [npm Command Not Working on Windows](/en/windows-npm-not-working)
- [Fix npm Cache Problems](/en/npm-cache-clear)
- [How to Install Git on Windows and Configure It](/en/windows-git-install)
- [npm vs yarn: Differences and When to Use Each](/en/npm-vs-yarn)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
