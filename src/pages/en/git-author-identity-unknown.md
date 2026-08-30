---
title: 'Fix "Please tell me who you are" Error on git commit'
date: '2026-08-30'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Git', 'git commit', 'user.name', 'user.email']
description: 'git commit fails with "Please tell me who you are" on a fresh machine. Here is why it happens and how to set user.name and user.email globally or per repository.'
---

## Quick Answer

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Run those two commands, then retry `git commit` — it will go through.

---

## What I Was Trying To Do

On a freshly set up container, I ran `git init`, added a file, and tried to make the first commit. It failed with this error instead:

```bash
git add README.md
git commit -m "init"
```

```
Author identity unknown

*** Please tell me who you are.

Run

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"

to set your account's default identity.
Omit --global to set the identity only in this repository.

fatal: empty ident name (for <>) not allowed
```

`git add` had already succeeded, so the file itself and the staging step were fine. The failure only happens at the `git commit` step.

---

## Environment

- Git: 2.43.0
- OS: Linux (fresh container, `$HOME` empty, no `git config` had ever been run)

---

## What I Tried

At first I assumed I'd forgotten to stage something, so I checked `git status` and `git diff --cached` — `README.md` was staged correctly. I then suspected the quoting in `-m "init"` and tried a few variations of the commit message, but the error stayed exactly the same: `Author identity unknown`.

Reading the message itself made the real cause obvious: Git is telling you directly to run `git config --global user.email` / `user.name`. The problem wasn't the file or the command syntax — it was that no author identity had ever been configured on this machine.

---

## Root Cause

Every commit object needs an `author` and `committer` field containing a name and an email address. Git reads those values from the `user.name` and `user.email` settings. On a brand-new machine, neither the global config (`~/.gitconfig`) nor the repository's local config (`.git/config`) had ever set them.

Checking directly confirmed both were empty:

```bash
git config --global user.name || echo "(unset)"
git config --global user.email || echo "(unset)"
```

```
(unset)
(unset)
```

If Git allowed the commit to proceed anyway, it would have to write an empty identity (`<>`) into the commit object, so it refuses with `fatal: empty ident name (for <>) not allowed`. This is a deliberate safeguard against corrupting the commit history, not a bug.

---

## The Fix

### 1. Set your name and email globally

If you want this identity applied to every repository for this user on this machine, use `--global`:

```bash
git config --global user.name "Test User"
git config --global user.email "test@example.com"
```

What each line does:

- `user.name`: the display name written into the author/committer field of every commit
- `user.email`: the email address written into the same field

### 2. Retry the commit

```bash
git add README.md
git commit -m "init"
```

```
[master (root-commit) b482ab7] init
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

Same command as before — this time it succeeds.

### 3. Using a different identity for one repository

If you switch between a work account and a personal account, you can set the identity for just the current repository by dropping `--global`:

```bash
git config user.name "Repo Local User"
git config user.email "repo-local@example.com"
```

A config set without `--global` is written to that repository's `.git/config` and takes priority over the global setting — useful when you juggle multiple GitHub accounts across projects.

---

## Verifying It Worked

Confirm the commit went through and the author identity is recorded correctly:

```bash
git log --oneline
```

```
b482ab7 init
```

You can also check which identity is currently in effect for the repository:

```bash
git config user.name
git config user.email
```

```
Repo Local User
repo-local@example.com
```

That lets you tell whether the local or the global setting is the one actually being used.

---

## Common Follow-up Issues

### `--global` doesn't seem to apply

If you've set the identity globally but keep getting asked anyway in a specific repository, check whether a stale local override exists in that repo's `.git/config` — local settings always win over global ones, so a leftover blank or wrong value there will keep blocking commits.

```bash
git config --local --list | grep user
```

### The same error keeps happening in CI

Disposable CI environments like GitHub Actions runners start with an empty `~/.gitconfig` every run, so the identity needs to be set explicitly inside the workflow before any job that commits. Setting it once near the top of the job is usually enough.

```bash
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
```

---

## FAQ

**Q: I don't want to expose my real email address. What can I use instead?**
On GitHub, you can use the `noreply` address GitHub generates for your account (e.g. `username@users.noreply.github.com`) as `user.email`, so commits don't carry your real address.

**Q: Which takes priority, the global setting or a local one?**
The repository-local setting (set without `--global`) always wins. The global setting is just the default used when a repository has no local override.

**Q: Once I set it globally, do I need to repeat this in every repository?**
No — a global setting applies to every repository for that user. Only set a local override in repositories where you specifically need a different identity.

**Q: Does this error only happen on the first commit?**
No. As long as `user.name` and `user.email` are unset, every subsequent commit attempt fails the same way with `Author identity unknown` until the identity is configured.

---

## Summary

- `git commit` requires `user.name` and `user.email` to build the author/committer field. If either is unset, it stops with `Please tell me who you are`.
- The fix is two `git config --global` lines — nothing was wrong with the file or the commit message.
- Use a local (non-`--global`) config when you need a different identity per repository, such as separating work and personal GitHub accounts, or in disposable CI runners.
- The same pattern — an empty required setting causing Git to stop as a safeguard rather than silently doing the wrong thing — shows up in other places too, like an unregistered SSH `known_hosts` entry or a missing GPG signing key. The general fix is the same: run the exact configuration command the error message points you to.

## Related Articles

- [How to Undo a git commit](/en/git-commit-undo)
- [Fixing "fatal: not a git repository"](/en/git-fatal-not-a-git-repository)
- [How to Write and Configure .gitignore](/en/git-gitignore-setup)
