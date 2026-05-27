---
title: 'How to Handle Paths with Spaces on Windows'
date: '2026-05-08'
category: 'Windows'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Windows', 'パス', 'スペース', 'ターミナル']
en_tags: ['Windows', 'path', 'spaces', 'terminal']
description: 'How to fix errors caused by spaces in Windows file paths. Covers quoting paths in the terminal and tips for avoiding spaces in project folders.'
---
## Symptom

```
cd C:\Users\user\My Documents\project
# Error: 'Documents\project' is not recognized
```

## Fix: Wrap the Path in Double Quotes

```bash
cd "C:\Users\user\My Documents\project"
```

## Prevention: Use Space-Free Folder Names

Keep your development folders space-free:

```
C:\Users\username\projects\project-name
```

For a better terminal experience when working with paths, see [Set Up Windows Terminal](/en/windows-terminal-setup).

## Related Posts

- [npm Command Not Working on Windows](/en/windows-npm-not-working)
- [How to Install Git on Windows and Configure It](/en/windows-git-install)
- [Fix npm Cache Problems](/en/npm-cache-clear)
- [Install Docker on Windows](/en/docker-install-windows)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
