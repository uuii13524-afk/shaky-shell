---
title: 'Fix "Author identity unknown" When Running git commit in a Container'
date: '2026-08-07'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git commit fails with "Author identity unknown" inside a throwaway Docker container even though --global identity was set before. Here is why the config disappears on every restart, and how to fix it for good.'
en_tags: ['Git', 'git commit', 'Docker']
---

## What I Was Trying to Do

I spin up a disposable `ubuntu:24.04` container to test things locally before pushing to CI. I cloned a repo inside the container, edited one line, staged it, and ran my usual `git commit`. It failed immediately.

```bash
git add README.md
git commit -m "first commit"
```

```text
Author identity unknown

*** Please tell me who you are.

Run

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"

to set your account's default identity.
Omit --global to set the identity only in this repository.

fatal: unable to auto-detect email address (got 'root@vm.(none)')
```

On my host machine, `user.name` and `user.email` have been set with `git config --global` for a long time, so I had never seen this error before. Running the exact same `git commit -m "first commit"` on the host worked fine. It only broke inside the container.

## Environment

- OS (inside container): Ubuntu 24.04.4 LTS
- Git: 2.43.0
- Container startup: `docker run --rm -it ubuntu:24.04 bash`, then clone the repo fresh every time
- Host machine: `user.name` / `user.email` already configured in `~/.gitconfig` via `git config --global`

## What I Tried

First I checked whether the identity was really missing with `git config --list --show-origin`.

```bash
git config --list --show-origin
```

```text
(nothing printed)
```

Not a single `user.*` entry showed up. On the host, the same command prints a line like `file:/root/.gitconfig  user.name=...`, so this told me `~/.gitconfig` simply didn't exist inside the container.

```bash
ls -la ~/.gitconfig
```

```text
ls: cannot access '/root/.gitconfig': No such file or directory
```

Following the error message's own suggestion, I set the identity with `--global` and committed again.

```bash
git config --global user.email "dev@example.com"
git config --global user.name "Dev User"
git commit -m "first commit"
```

```text
[master (root-commit) a20a8cf] first commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

That worked. But once I exited the container and ran `docker run --rm -it ubuntu:24.04 bash` again, the exact same `Author identity unknown` error came right back. The `--global` setting from a moment ago didn't carry over at all.

## Why This Happens

The culprit was the `--rm` flag. A container started with `--rm` is deleted, along with any files written to its writable layer, the moment it exits. `git config --global` writes `user.name` / `user.email` into `$HOME/.gitconfig` (here, `/root/.gitconfig`) — but that file only exists inside that one container's layer.

In other words, "global" only means "persists for as long as this particular container is alive." Since I was throwing the container away and starting fresh every time, `$HOME` came back empty on every run. The host's `~/.gitconfig` and the container's `~/.gitconfig` are two completely separate files unless you explicitly bind-mount one into the other — which I wasn't doing.

## Solution

If you reuse the same container long-term, `--global` is fine as-is. But for a throwaway workflow like mine, the identity needs to come from outside the container. Two approaches worked:

### Option 1: Mount the host's `.gitconfig` into the container

```bash
docker run --rm -it -v "$HOME/.gitconfig:/root/.gitconfig:ro" ubuntu:24.04 bash
```

This passes the host's already-configured identity into the container read-only. No matter how many times the container gets recreated, it just reads the same file from the host.

```bash
git config --list --show-origin
```

```text
file:/root/.gitconfig  user.email=dev@example.com
file:/root/.gitconfig  user.name=Dev User
```

### Option 2: Set the identity locally, per repository, every time

If you'd rather not expose the whole host config, fold the identity setup into the same steps you already run right after cloning.

```bash
git clone https://example.com/sample-repo.git
cd sample-repo
git config user.email "dev@example.com"
git config user.name "Dev User"
git commit -m "first commit"
```

```text
[master (root-commit) a20a8cf] first commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

Without `--global`, this writes to `.git/config` inside the repo instead of `$HOME/.gitconfig`, so it doesn't depend on the container's lifecycle at all. For CI scripts, this is usually the more predictable choice, since it behaves the same no matter where it runs.

## Verify It Works

After Option 2, I checked what actually landed in `.git/config`.

```bash
cat .git/config | grep -A2 "\[user\]"
```

```text
[user]
	email = dev@example.com
	name = Dev User
```

`git log` confirmed the commit had the right author and committer.

```bash
git log --pretty=fuller -1
```

```text
commit a20a8cfb2e3fdf3572eb32021384b21dbba21a83
Author:     Dev User <dev@example.com>
AuthorDate: Fri Aug 7 00:16:28 2026 +0000
Commit:     Dev User <dev@example.com>
CommitDate: Fri Aug 7 00:16:28 2026 +0000

    first commit
```

I exited and recreated the container again with both Option 1 and Option 2, and the error didn't come back either way.

## Summary

- `Author identity unknown` means the shell's current `$HOME` has no `.gitconfig` with a `user.email` / `user.name` in it.
- Running `git config --global` inside a `--rm` Docker container only lasts until that container is removed — "global" only persists for the container's own lifetime.
- For throwaway environments, either bind-mount the host's `.gitconfig` read-only, or bake a local (non-`--global`) `git config user.email/user.name` step into your setup process. The same reasoning applies to CI runners like GitHub Actions.

## Gotchas

- Because the error message tells you to fix it with `--global` right there, it's easy to commit successfully once and move on without realizing the fix won't survive the next container restart.
- Checking `~/.gitconfig` with `cat` alone doesn't distinguish "file doesn't exist" from "file exists but is empty." `git config --list --show-origin` narrows down the cause faster.
- Mounting the host's `.gitconfig` is convenient, but if the host has multiple identities configured for different accounts (work vs. personal), you might end up committing under the wrong one without noticing. Double-check the host's `user.email` before mounting it in.

## FAQ

**Q: Can I just pass `--author="Name <email>"` to every commit instead?**
You can, but it's easy to forget in an automated environment. Setting the identity once via `git config` ahead of time is more reliable for scripts and CI.

**Q: If I mount `$HOME/.gitconfig` into the container, does that also bring in other settings like aliases?**
Yes — mounting the whole file brings everything in it, not just `user.name`/`user.email`. If you only want to pass the identity, Option 2 (setting it per repository) is the safer choice.

**Q: Does this happen with `actions/checkout` in GitHub Actions too?**
Not usually, since `actions/checkout` only clones and doesn't commit. But if your workflow has a step that runs `git commit` itself (an auto-commit job, for example), the runner needs `user.email`/`user.name` set explicitly first, or you'll hit the same error.

## Related Articles

- [How to Undo a git commit](/en/git-commit-undo)
- [Fixing "fatal: not a git repository"](/en/git-fatal-not-a-git-repository)
- [How to Push to GitHub for the First Time](/en/github-first-push)
- [How to Install Git on Windows](/en/windows-git-install)
