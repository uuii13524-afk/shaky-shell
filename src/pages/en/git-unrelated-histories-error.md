---
title: 'Fixing "fatal: refusing to merge unrelated histories" in git pull'
date: '2026-08-09'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git pull fails with fatal: refusing to merge unrelated histories right after connecting to a GitHub repo created with a README. Here is why it happens and how to merge safely.'
ja_tags: ['Git', 'GitHub', 'unrelated histories', 'git pull', 'マージ']
en_tags: ['Git', 'GitHub', 'unrelated histories', 'git pull', 'merge']
---

## What I Was Trying to Do

I had an existing project where I'd run `git init` locally and already made a commit or two, with no `README.md` in it. Separately, I created a brand-new repository on GitHub through the web UI, checking the "Add a README file" option. When I registered it as a remote with `git remote add origin` and ran my usual `git pull origin main`, Git stopped me with this:

```text
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint:
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
hint:
hint: You can replace "git config" with "git config --global" to set a default
hint: preference for all repositories. You can also pass --rebase, --no-rebase,
hint: or --ff-only on the command line to override the configured default per
hint: invocation.
fatal: Need to specify how to reconcile divergent branches.
```

I took that at face value, ran `git config pull.rebase false` to pick a reconciliation strategy, and tried `git pull` again. That's when I hit a completely different, harder error:

```text
fatal: refusing to merge unrelated histories
```

I'd just done what the hint told me to do, so I didn't understand why the pull was still being rejected.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- Remote: GitHub (repository created via the web "Create repository" screen, with README and .gitignore added)
- Local: an existing project already `git init`'d, with commits that had nothing to do with the remote

## What I Tried

My first guess was that `pull.rebase` just wasn't configured. Following the hint, I set `git config pull.rebase false` and re-ran `git pull origin main` — but it failed again, this time with `fatal: refusing to merge unrelated histories`. At that point it was clear the "rebase vs. merge" question and the "unrelated histories" question were two separate problems.

Next I suspected I'd registered the wrong remote URL, so I checked what was actually configured:

```bash
git remote -v
```

```text
origin  /tmp/.../repoA (fetch)
origin  /tmp/.../repoA (push)
```

The URL was correct, and `git fetch origin` on its own completed without any error — `FETCH_HEAD` picked up the remote branch just fine. So this wasn't a connectivity or remote-config issue; only the "merge" half of `pull` (fetch + merge) was being refused.

I compared the two commit histories directly with `git log`:

```bash
git log --oneline
```

The local branch started from a `local: initial scaffold` commit; the remote's `origin/main` (visible after the fetch) started from `Initial commit from GitHub web UI`. Neither history shared a single common ancestor commit. That's exactly what happens when you check "Add a README file" while creating a repo on GitHub — it creates a root commit on the remote that has no relationship at all to whatever you already had locally from `git init`. Two histories with no shared root is literally what "unrelated histories" means.

## Root Cause

By default, Git refuses to merge two histories that don't share a common ancestor commit. This is a safety behavior introduced in Git 2.9 specifically to stop you from accidentally merging two completely unrelated repositories together by mistake.

In my case, the project I'd started locally with `git init` and the repository GitHub created "with a README" each had their own separate root commit. Setting `git config pull.rebase false` only tells Git which strategy to use *when a fast-forward isn't possible* — it says nothing about whether Git should be allowed to stitch together two histories that have no common root in the first place. That's a completely separate check, which is why the `pull.rebase` setting alone didn't fix anything.

## How I Fixed It

### 1. Confirm the histories really are unrelated, via fetch

Before forcing a merge, fetch first and inspect what you actually have:

```bash
git fetch origin
git log --oneline --graph --all
```

I could see the local branch and `origin/main` had no shared commit anywhere — the graph was two completely separate lines that never converged.

### 2. Pull with --allow-unrelated-histories

Once I'd confirmed that was really the situation (and not, say, a wrong remote), I explicitly allowed the merge:

```bash
git pull origin main --allow-unrelated-histories
```

```text
From /tmp/.../repoA
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`Merge made by the 'ort' strategy.` — the merge succeeded this time. The `README.md` that GitHub had created came in as part of a merge commit, without conflicting with anything I already had locally.

### 3. Verify the merge commit

```bash
git log --oneline --graph --all
```

```text
*   bd1bbdd Merge branch 'main' of /tmp/.../repoA
|\
| * 4adee1c Initial commit from GitHub web UI
* 2e85e09 local: initial scaffold
```

Both root commits — the local one and GitHub's — are still there, now joined by a single merge commit. If any files had actually collided, this step would have stopped for a normal conflict resolution (edit the file, `git add`, `git commit`), but in my case nothing overlapped, so the merge finished on its own.

## Verifying It Worked

After the merge, I checked that files from both sides were present in the working directory:

```bash
ls -la
```

```text
README.md
index.js
```

Both the `README.md` GitHub created and the `index.js` I already had locally were there together. From this point, `git push origin main` pushes the merged history back to the remote with nothing left unresolved.

## Summary

- `fatal: refusing to merge unrelated histories` just means Git is refusing, for safety, to merge two histories with no shared ancestor commit — it isn't a remote-configuration or network problem.
- `git config pull.rebase false/true` only controls how Git reconciles branches when a fast-forward isn't possible. It's a different setting from whether unrelated histories are allowed to merge at all, so it won't fix this by itself.
- `git pull origin <branch> --allow-unrelated-histories` explicitly permits the merge. If files collide, resolve the conflicts the normal way afterward.
- This shows up most often when you start a project locally before creating the GitHub repo with a README, or when you're trying to combine two previously separate repositories into one — the same diagnosis steps apply either way.

## Related Articles

- [How to Resolve a Git Merge Conflict After git pull](/en/git-pull-merge-conflict)
- [Fixing a Rejected git push](/en/git-push-rejected-fix)
- [How to Push to GitHub for the First Time](/en/github-first-push)
- [How to Recover Lost Commits with git reflog](/en/git-reflog)
- [Git Remote Commands: The Basics](/en/git-remote-operations)
