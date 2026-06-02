---
title: 'How to Set Up Aliases in Linux to Speed Up Your Workflow (.bashrc/.zshrc)'
date: '2026-06-02'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'bash', 'zsh', 'エイリアス', 'シェル設定']
en_tags: ['Linux', 'bash', 'zsh', 'alias', 'shell configuration']
description: 'How to set up aliases in .bashrc or .zshrc to shorten commands on Linux. Practical examples for Git, Docker, and shell functions included.'
---
## What I Wanted to Do
Typing `git status` or `docker-compose up -d` in full every time got tedious fast.
Adding aliases to `.bashrc` or `.zshrc` lets you register short custom commands without installing anything.

## Basic Alias Syntax
Add alias definitions to `~/.bashrc` (for bash) or `~/.zshrc` (for zsh):

```bash
# Add to ~/.bashrc or ~/.zshrc
alias gs='git status'
alias gp='git push'
alias ll='ls -la'
alias dc='docker-compose'
```

Apply the changes without restarting the terminal:

```bash
source ~/.bashrc
# or
source ~/.zshrc
```

## Useful Alias Examples

### Git Shortcuts
```bash
alias gs='git status'
alias ga='git add .'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline --graph'
alias gd='git diff'
```

### Docker Shortcuts
```bash
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dps='docker ps -a'
alias drm='docker rm $(docker ps -aq)'
```

### General Linux Shortcuts
```bash
alias ll='ls -la'
alias la='ls -A'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias mkdir='mkdir -pv'
```

## Using Shell Functions for Multi-Step Commands
When a single alias is not enough, define a function instead:

```bash
# Create a directory and immediately cd into it
mkcd() {
  mkdir -p "$1" && cd "$1"
}

# Git add + commit + push in one command
gacp() {
  git add .
  git commit -m "$1"
  git push
}
```

Functions go in the same `.bashrc` / `.zshrc` file as aliases.

## Check What Aliases Are Defined
```bash
# List all current aliases
alias

# Check a specific alias
alias gs
```

## Common Pitfalls
- Forgetting to run `source ~/.bashrc` — changes won't take effect until you reload or open a new terminal
- Editing `.zshrc` when your shell is actually bash (check with `echo $SHELL`)
- Naming an alias after an existing command silently overrides it (use `which dc` to check first)
- `alias gc='git commit -m'` needs the message as an argument: use it as `gc "your message"`
- On some servers the login shell is `/bin/sh`, so `.bashrc` may not be loaded automatically

## Related Articles
- [Linux Basic Commands Cheatsheet (ls/cd/mkdir/rm)](/en/linux-basic-commands)
- [SSH Basics on Linux (How to Connect to a VPS)](/en/linux-ssh-basics)
- [How to Use ~/.ssh/config to Simplify SSH Connections](/en/ssh-config-file)
- [How to Schedule Cron Jobs on Linux for Automated Task Execution](/en/linux-cron-setup)
- [Linux Process Management (ps/kill/top)](/en/linux-process-management)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
