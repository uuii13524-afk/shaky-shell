---
title: 'Set Up Windows Terminal'
date: '2026-05-15'
category: 'Windows'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Windows', 'Windows Terminal', 'ターミナル', '開発環境']
en_tags: ['Windows', 'Windows Terminal', 'terminal', 'dev environment']
description: 'How to install Windows Terminal and configure it for daily development use. Covers keyboard shortcuts, changing the default shell, and WSL2 integration.'
---
## Install

```bash
winget install Microsoft.WindowsTerminal
```

Or search "Windows Terminal" in the Microsoft Store.

## Keyboard Shortcuts

```
Ctrl + Shift + T    # New tab
Ctrl + Shift + W    # Close tab
Alt + Shift + D     # Split pane
```

## Change the Default Shell

Settings (Ctrl + ,) → Startup → "Default profile"

## Common Pitfalls

- Windows 11 ships with Windows Terminal pre-installed
- After installing WSL2, Ubuntu appears automatically as a profile

Pairing Windows Terminal with WSL2 gives you a full Linux development environment on Windows. See [Install WSL2 on Windows](/en/wsl2-install-windows).

## Related Posts

- [Install WSL2 on Windows](/en/wsl2-install-windows)
- [How to Install Git on Windows and Configure It](/en/windows-git-install)
- [npm Command Not Working on Windows](/en/windows-npm-not-working)
- [How to Set and Check Environment Variables on Windows](/en/windows-env-variables)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
