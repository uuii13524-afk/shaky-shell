---
title: 'Fix: git clone Leaves Files as Git LFS Pointer Text Instead of Real Content'
date: '2026-08-03'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'After git clone, files tracked by Git LFS stay as small pointer text (version/oid/size) instead of the real binary content. Here is the cause and how to fix it with git lfs install and git lfs pull.'
en_tags: ['Git', 'Git LFS', 'clone']
---

## What I Was Trying to Do

I set up a fresh machine and cloned a team repo called `design-assets`, which has used Git LFS for `*.psd` and `*.mp4` files for a while.

```bash
git clone git@github.com:example-team/design-assets.git
cd design-assets
ls -lh assets/banner_main.psd
```

The file, which should have been close to 100MB, was only 130 bytes.

```text
-rw-r--r-- 1 user user 130 Aug  3 09:12 assets/banner_main.psd
```

Printing its contents showed text instead of binary data:

```bash
cat assets/banner_main.psd
```

```text
version https://git-lfs.github.com/spec/v1
oid sha256:9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a
size 104857600
```

Photoshop refused to open it, reporting the file might be corrupted. Other teammates had no issue opening the same file, so I assumed something was specific to my machine.

## Environment

- OS: Windows 11 23H2 (working inside WSL2 Ubuntu 22.04.4)
- Git: 2.43.0
- Git LFS: not installed (the actual root cause)
- Repo: `design-assets` (GitHub, LFS configured via `.gitattributes`)
- File in question: `assets/banner_main.psd` (~100MB in reality)

## What I Tried

My first guess was that the clone itself had failed partway, so I removed the directory and cloned again.

```bash
rm -rf design-assets
git clone git@github.com:example-team/design-assets.git
```

Same result — `banner_main.psd` was still a 130-byte pointer. That ruled out a network issue: the clone completed successfully, but the file content was never materialized.

Next I checked whether `.gitattributes` was even present:

```bash
cat .gitattributes
```

```text
*.psd filter=lfs diff=lfs merge=lfs -text
*.mp4 filter=lfs diff=lfs merge=lfs -text
```

The LFS configuration was correctly committed to the repo. So I checked whether something was missing on my own machine instead, and ran the `git lfs` command directly.

```bash
git lfs version
```

```text
git: 'lfs' is not a git command. See 'git --help'.
```

That was the moment it clicked — the `git-lfs` extension itself wasn't installed on this machine. The smudge filter that `filter=lfs` in `.gitattributes` refers to (the step that swaps a pointer for real content on checkout) only gets registered by `git-lfs` itself. Without it installed, there's nothing to register.

## Root Cause

Git LFS replaces pointer files with real content during `clone`/`checkout` using Git's clean/smudge filter mechanism. That filter only gets wired into Git's config (`~/.gitconfig`) after running `git lfs install` — which in turn requires the `git-lfs` binary to exist in the first place.

So on a machine without `git-lfs` installed, cloning a repo whose `.gitattributes` declares LFS filters doesn't fail or warn — Git simply has no filter registered for `filter=lfs`, and writes out exactly what's actually committed in the repository: the three-line pointer text (`version` / `oid` / `size`). `git clone` reports success either way, which makes this easy to miss until you actually check a file's size.

## How I Fixed It

### 1. Install git-lfs

I was working inside WSL2's Ubuntu, so I installed it via APT.

```bash
sudo apt update
sudo apt install git-lfs
```

```text
Setting up git-lfs (3.4.0-1) ...
Git LFS initialized.
```

### 2. Register the filter with git lfs install

Installing the binary alone doesn't hook it into Git, so I registered it explicitly.

```bash
git lfs install
```

```text
Updated Git hooks.
Git LFS initialized.
```

I confirmed the filter config landed in `~/.gitconfig`:

```bash
git config --global --get-regexp filter.lfs
```

```text
filter.lfs.clean git-lfs clean -- %f
filter.lfs.smudge git-lfs smudge -- %f
filter.lfs.process git-lfs filter-process
filter.lfs.required true
```

### 3. Replace pointer files with real content in the existing clone

Rather than re-cloning, I used `git lfs pull` inside the existing working copy to swap the pointers for real content.

```bash
cd design-assets
git lfs pull
```

```text
Downloading LFS objects:  50% (1/2), 52 MB | 8.1 MB/s
Downloading LFS objects: 100% (2/2), 100 MB | 8.4 MB/s, done.
```

### 4. Check the file size again

```bash
ls -lh assets/banner_main.psd
```

```text
-rw-r--r-- 1 user user 100M Aug  3 09:41 assets/banner_main.psd
```

Back to the real file size.

## Verify It Works

I opened `assets/banner_main.psd` in Photoshop and confirmed the layers loaded correctly. As a final check, I cloned into a fresh directory to make sure a clean `clone` would now materialize real content from the start.

```bash
git clone git@github.com:example-team/design-assets.git design-assets-check
cd design-assets-check
ls -lh assets/banner_main.psd
```

```text
-rw-r--r-- 1 user user 100M Aug  3 09:55 assets/banner_main.psd
```

With `git lfs install` already done, the file was real content right after `clone`, no `pull` needed.

## Takeaways

- Without `git-lfs` installed, cloning an LFS-enabled repo leaves tracked files as small pointer text (`version` / `oid` / `size`) instead of real content — and `git clone` still reports success, so it's easy to miss until you check a file's actual size.
- The fix is installing `git-lfs` and running `git lfs install` to register the filter, plus `git lfs pull` for a clone that already happened. On a new machine, running `git lfs install` before cloning avoids this entirely.
- This shows up most with the kinds of files people tend to put under LFS — videos, design files, model weights. If `cat`-ing a suspiciously small file prints `version https://git-lfs.github.com/spec/v1`, this is almost certainly the cause.

## FAQ

**Q: Do I need to run `git lfs install` per repository?**
No — it's a one-time, machine-wide Git config change. Once set, every LFS-enabled repo you clone on that machine gets the filter automatically. What you do need per machine is the `git-lfs` binary itself.

**Q: If I already cloned and got pointer files, do I need to re-clone?**
No. Install `git-lfs`, run `git lfs install`, then run `git lfs pull` inside the existing working copy — it replaces the pointer files with real content in place.

**Q: Does this happen in CI too?**
Yes. If the CI image doesn't have `git-lfs` installed, checkout steps will leave LFS files as pointers, and any build step expecting real file content will fail. CI environments need `git-lfs` installed and `git lfs install` run (or the LFS option enabled on whatever checkout action you're using) just like a local machine.

## Related Articles

- [Fix "remote rejected" on git push: File Exceeds GitHub's 100MB Limit](/en/git-push-large-file-rejected)
- [Basic git remote Operations](/en/git-remote-operations)
- [Troubleshooting My First Push to GitHub](/en/github-first-push)
- [Recovering Commits with git reflog](/en/git-reflog)
- [Adding an SSH Key to GitHub](/en/ssh-key-github)
