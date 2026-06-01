---
title: 'How to Set and Check Environment Variables on Windows'
date: '2026-05-18'
category: 'Windows'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Windows', '環境変数', 'PATH', 'PowerShell']
en_tags: ['Windows', 'environment variables', 'PATH', 'PowerShell']
description: 'How to set and verify system and user environment variables on Windows using both the GUI and the command line, including PATH edits.'
---
## Set via GUI

1. Search "environment variables" → "Edit the system environment variables"
2. "Environment Variables" → select "Path" → "Edit" → "New"
3. Click OK → restart your terminal

## Check via Command Line

```powershell
$env:PATH -split ";"    # PowerShell
echo %PATH%             # Command Prompt
```

## Set Temporarily

```powershell
$env:MY_KEY = "my_value"    # PowerShell (session only)
set MY_KEY=my_value          # Command Prompt (session only)
```

## Common Pitfalls

- Changes don't apply until the terminal is restarted
- User environment variables only affect the current user account

If npm still doesn't work after fixing the PATH, see [npm Command Not Working on Windows](/en/windows-npm-not-working).

## Related Posts

- [npm Command Not Working on Windows](/en/windows-npm-not-working)
- [How to Install Git on Windows and Configure It](/en/windows-git-install)
- [Install WSL2 on Windows](/en/wsl2-install-windows)
- [Set Up Windows Terminal](/en/windows-terminal-setup)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
