---
title: 'npm Command Not Working on Windows'
date: '2026-05-06'
category: 'Windows'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Windows', 'npm', 'Node.js', 'トラブルシューティング']
en_tags: ['Windows', 'npm', 'Node.js', 'troubleshooting']
description: "How to fix 'npm is not recognized' errors on Windows. Covers Node.js installation, PATH setup, and PowerShell execution policy fixes."
---
## Symptom

```
'npm' is not recognized as an internal or external command,
operable program or batch file.
```

## Cause 1: Node.js Is Not Installed

Download and install the LTS version from https://nodejs.org

## Cause 2: PATH Is Not Set

1. Search "environment variables" → edit "Path"
2. Add the Node.js install path (e.g., `C:\Program Files\nodejs\`)
3. Restart the terminal

## Cause 3: PowerShell Execution Policy

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Cause 4: Terminal Not Restarted

Always restart the terminal after installing Node.js.

For a better terminal experience, see [Set Up Windows Terminal](/en/windows-terminal-setup).

## Related Posts

- [How to Install Git on Windows and Configure It](/en/windows-git-install)
- [Manage Node.js Versions with nvm](/en/node-version-management-nvm)
- [Fix npm Cache Problems](/en/npm-cache-clear)
- [How to Handle Paths with Spaces on Windows](/en/windows-path-with-spaces)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
