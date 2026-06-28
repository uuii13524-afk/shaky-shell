---
title: 'How to Set Environment Variables in Linux (export, .bashrc, Persistent)'
date: '2026-06-28'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Linux', 'environment variables', 'export', 'bashrc', 'shell']
description: 'Learn how to set, view, and persist environment variables in Linux. Covers export command, .bashrc, .bash_profile, and /etc/environment for system-wide settings.'
---

## Quick Answer

```bash
# Temporary (current session only)
export MY_VAR="hello"

# Persistent (survives reboot and new terminals)
echo 'export MY_VAR="hello"' >> ~/.bashrc
source ~/.bashrc
```

---

## What You're Trying to Do

You need to set an environment variable in Linux, but it disappears when you close the terminal. Or you want a tool or application to always have access to a specific variable without setting it every time.

---

## Environment

- OS: Ubuntu 22.04 / Debian 12 (works on most Linux distributions)
- Shell: bash / zsh

---

## Solution

### 1. View existing environment variables

```bash
# List all environment variables
env

# Check a specific variable
echo $HOME
echo $PATH
echo $MY_VAR
```

### 2. Set a temporary environment variable (current session only)

```bash
export MY_VAR="hello"
echo $MY_VAR
# → hello
```

This is lost when the terminal is closed.

### 3. Persist using .bashrc (per-user)

```bash
echo 'export MY_VAR="hello"' >> ~/.bashrc
source ~/.bashrc
```

`.bashrc` is loaded for every interactive shell session.

### 4. Use .bash_profile for login shells

```bash
echo 'export MY_VAR="hello"' >> ~/.bash_profile
source ~/.bash_profile
```

Loaded on SSH logins and initial login sessions.

### 5. System-wide variables using /etc/environment

```bash
sudo nano /etc/environment
```

Add variables in the following format (no `export` keyword):

```
MY_VAR="hello"
PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

Requires a re-login or reboot to take effect.

### 6. Unset an environment variable

```bash
unset MY_VAR
echo $MY_VAR
# → (empty)
```

### 7. Set a variable for a single command

```bash
MY_VAR="hello" node app.js
```

This sets the variable only for that process and does not affect the current shell.

---

## Common Errors

### `export: not valid in this context`

```
export: 'MY_VAR=hello world' is not valid in this context
```

**Cause:** The value contains spaces but is not quoted.  
**Fix:**

```bash
export MY_VAR="hello world"
```

### `source: command not found`

Occurs when running a script with `sh` instead of `bash`.  
**Fix:** Use `.` instead of `source` (they are equivalent):

```bash
. ~/.bashrc
```

### Environment variable disappears after reboot

If you added it to `.bashrc` but it still disappears, your login shell may only read `.bash_profile`.  
**Fix:** Call `.bashrc` from `.bash_profile`:

```bash
# Add to ~/.bash_profile
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi
```

### PATH is broken — `ls` and other commands not found

```bash
# Temporarily repair PATH for the current session
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

Then open `.bashrc` and fix the broken PATH entry.

---

## FAQ

**Q: What is the difference between `export VAR=value` and `VAR=value`?**  
`VAR=value` sets the variable only in the current shell. `export VAR=value` also makes it available to child processes (scripts and commands you run from that shell).

**Q: I use zsh — which file should I edit?**  
Add your exports to `~/.zshrc` for persistent variables in zsh. For login shells, use `~/.zprofile` or `~/.zlogin`.

**Q: What is the difference between `env` and `printenv`?**  
Both list environment variables. `printenv VAR` prints a single variable's value. `env` can also run a command in a modified environment.

**Q: Should I use .bashrc or .bash_profile?**  
Use `.bashrc` for variables you want in every terminal session. Use `.bash_profile` for variables that only need to be set once at login (e.g., on SSH). For most use cases, `.bashrc` is the right choice.

**Q: How do I set an environment variable for all users?**  
Edit `/etc/environment` (no `export` keyword needed). Alternatively, add a script under `/etc/profile.d/` — every file there is sourced at login.

**Q: Can Node.js and Python read these environment variables?**  
Yes. Variables set with `export` are accessible via `process.env.MY_VAR` in Node.js and `os.environ['MY_VAR']` in Python.

---

## Related Articles

- [Linux Basic Commands Cheat Sheet](/en/linux-basic-commands)
- [Linux File Permissions (chmod & chown)](/en/linux-file-permissions)
- [How to Create and Manage systemd Services](/en/linux-systemd-service)
- [Install WSL2 on Windows](/en/wsl2-install-windows)

## Recommended VPS / Hosting

If you want to build a production Linux environment, these VPS services are a great starting point:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
