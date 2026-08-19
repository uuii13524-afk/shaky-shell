---
title: 'Fix: git clone Leaves Submodule Directories Empty and Breaks the Build'
date: '2026-08-19'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'After git clone, a submodule directory exists but is empty, and npm run build fails with a module resolution error. Here is the cause and how to fix it with git submodule update --init --recursive.'
en_tags: ['Git', 'Git Submodule', 'build error']
---

## What I Was Trying to Do

I was setting up the `internal-dashboard` repo on a new machine. It references a shared component library through a submodule at `packages/ui-kit`.

```bash
git clone git@github.com:example-org/internal-dashboard.git
cd internal-dashboard
npm install
npm run build
```

`npm install` finished without issue, but `npm run build` stopped with a resolution error.

```text
[vite]: Rollup failed to resolve import "../../packages/ui-kit/dist/index.js" from "src/App.tsx".
This is most likely unintended because it can break your application at runtime.
If you do want to externalize this module explicitly add it to
`build.rollupOptions.external`
```

The `packages/ui-kit` directory did exist, so my first guess was a broken path alias in `vite.config.ts`, and I went down that path first.

## Environment

- OS: Ubuntu 24.04 LTS
- Git: 2.45.2
- Node.js: v20.14.0
- npm: 10.7.0
- Repo: `internal-dashboard` (GitHub, references `packages/ui-kit` as a submodule)
- Build tool: Vite 5.3 (a plain React + Vite project, not Astro)

## What I Tried

I checked the alias configuration in `vite.config.ts` first, but the path itself was correct. Next I looked directly inside `packages/ui-kit`.

```bash
ls -la packages/ui-kit
```

```text
total 8
drwxr-xr-x  2 user user 4096 Aug 19 10:02 .
drwxr-xr-x 12 user user 4096 Aug 19 10:02 ..
```

The directory existed but was completely empty. That's when I realized this wasn't a build config problem at all — the files simply weren't there.

Just to be sure, I also checked `git status`, which reported nothing unusual.

```bash
git status
```

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

Because `git status` reported "clean", it wasn't obvious that the submodule had never been fetched. That's what kept me chasing the build config for longer than I should have.

Next I checked `.gitmodules`.

```bash
cat .gitmodules
```

```text
[submodule "packages/ui-kit"]
	path = packages/ui-kit
	url = git@github.com:example-org/ui-kit.git
	branch = main
```

The submodule definition itself was correct. Only at this point did I finally run `git submodule status`.

```bash
git submodule status
```

```text
-4f2a9c1e8b3d7a6f5e4d3c2b1a0f9e8d7c6b5a4f packages/ui-kit
```

There's a `-` prefix on that line. That turned out to be the actual signal I'd been missing.

## Root Cause

`git clone` only fetches the `.gitmodules` file and a gitlink pointing at the exact commit each submodule should be at — it does not fetch the submodule's actual file content by default. So the `packages/ui-kit` directory gets created during clone, but its contents stay empty.

The prefix Git prints in `git submodule status` output carries specific meaning: `-` means "registered but never checked out locally" (not initialized), `+` means "initialized, but the local commit doesn't match what's recorded", and no prefix at all means "initialized and up to date". In this case the `-` meant `git submodule init` hadn't even run yet, let alone `update`.

What made this harder to spot is that `git status` doesn't flag an uninitialized submodule by default. `packages/ui-kit` is tracked only as a gitlink reference; the state of files underneath it falls outside what a plain `git status` inspects. So the repo looked perfectly clean while only the build was failing — a confusing combination.

## How I Fixed It

### 1. Check the submodule's status

```bash
git submodule status
```

```text
-4f2a9c1e8b3d7a6f5e4d3c2b1a0f9e8d7c6b5a4f packages/ui-kit
```

Confirmed the `-` prefix, meaning the submodule was never initialized.

### 2. Initialize and fetch the submodule's content

```bash
git submodule update --init --recursive
```

```text
Submodule 'packages/ui-kit' (git@github.com:example-org/ui-kit.git) registered for path 'packages/ui-kit'
Cloning into '/home/user/internal-dashboard/packages/ui-kit'...
Submodule path 'packages/ui-kit': checked out '4f2a9c1e8b3d7a6f5e4d3c2b1a0f9e8d7c6b5a4f'
```

I added `--recursive` in case `ui-kit` itself had nested submodules (it didn't, in this case, but it's a habit I keep).

### 3. Check the directory contents again

```bash
ls packages/ui-kit
```

```text
dist  package.json  src  tsconfig.json
```

The directory that was empty now had the expected files.

### 4. Check the submodule status again

```bash
git submodule status
```

```text
 4f2a9c1e8b3d7a6f5e4d3c2b1a0f9e8d7c6b5a4f packages/ui-kit (heads/main)
```

The leading `-` is gone, and the local content matches the recorded commit.

### 5. Rebuild

```bash
npm run build
```

```text
vite v5.3.1 building for production...
✓ 214 modules transformed.
dist/index.html                  0.46 kB
dist/assets/index-C8kQmZ1a.js  186.32 kB
✓ built in 3.12s
```

The build completed without errors.

## Verify It Works

As a final check, I cloned into a fresh directory with `--recurse-submodules` to confirm the submodule content gets fetched right from the start.

```bash
git clone --recurse-submodules git@github.com:example-org/internal-dashboard.git internal-dashboard-check
cd internal-dashboard-check
ls packages/ui-kit
```

```text
dist  package.json  src  tsconfig.json
```

`packages/ui-kit` was populated as soon as `clone` finished, no extra step needed.

## Takeaways

- `git clone` only fetches a submodule's definition (`.gitmodules`) and the commit it's pinned to — not the actual file content. The directory gets created regardless, which makes it easy to overlook until something tries to read from it.
- `git status` doesn't warn about an uninitialized submodule by default, so the repo can look "clean" while only the build fails. `git submodule status` is the reliable way to check — look for a leading `-`.
- For new clones, use `git clone --recurse-submodules`. If you've already cloned and hit this, `git submodule update --init --recursive` fetches the missing content. Setting `git config --global submodule.recurse true` makes future `pull` and `checkout` commands keep submodules in sync automatically.

## FAQ

**Q: Does `git pull` alone bring the submodule content up to date?**
No. `git pull` only updates the commit reference the parent repo records for the submodule, not the submodule's own working directory. If someone else bumped the submodule to a newer commit, you still need to run `git submodule update` (or `git submodule update --remote`) locally.

**Q: I'll probably forget `--recurse-submodules` next time. Is there a way to avoid that?**
Setting `git config --global submodule.recurse true` makes `pull` and `checkout` — not just `clone` — keep submodules in sync automatically. It's a per-machine setting though, so it's still worth documenting the clone command in the README for teammates.

**Q: I keep forgetting what the `git submodule status` prefixes mean.**
`-` means not initialized, `+` means initialized but out of sync with the recorded commit, and no prefix means initialized and up to date. When `git status` looks clean but something's still broken, that command is the first thing worth checking.

## Related Articles

- [Fix: git clone Leaves Files as Git LFS Pointer Text Instead of Real Content](/en/git-clone-lfs-pointer-file)
- [Fix "is already used by worktree" When Running git worktree add](/en/git-worktree-already-checked-out)
- [Git Remote Repository Operations (remote/fetch/pull/push)](/en/git-remote-operations)
- [How to Create a GitHub Repository and Push for the First Time](/en/github-first-push)
- [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github)
