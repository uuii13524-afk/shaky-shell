---
title: 'Fix "fatal: refusing to merge unrelated histories" in Git'
date: '2026-07-27'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'How to fix "fatal: refusing to merge unrelated histories" when running git pull or git merge, a common case when a GitHub repo is created with an auto-generated README before the first local push.'
en_tags: ['Git', 'GitHub', 'fatal', 'unrelated histories', 'merge']
---

## What I Was Trying to Do

I ran `git init` locally, made a few commits, then created the matching repository on GitHub. I'd left the "Add a README file" checkbox ticked when creating it, so the remote already had one commit of its own. After adding the remote, I tried to pull it in and hit an error I hadn't seen before.

```text
$ git remote add origin git@github.com:example/myproject.git
$ git pull origin main
warning: no common commits
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (3/3), 799 bytes | 799.00 KiB/s, done.
From github.com:example/myproject
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

Nothing was lost on either side — the local commits and the remote commit were both intact — but Git flatly refused to combine them.

## Environment

- OS: Ubuntu 24.04 LTS
- Git: 2.43.0 (installed via apt)
- Terminal: GNOME Terminal
- How the repo was set up: local `git init` first, then a new GitHub repository created with "Add a README file" checked, remote added afterward

## What I Tried

My first instinct was to just run the pull again, assuming it was a fluke.

```bash
git pull origin main
```

```text
fatal: refusing to merge unrelated histories
```

Same result. So I compared the commit logs on both sides.

```bash
git log --oneline
git log --oneline origin/main
```

```text
$ git log --oneline
a1b2c3d Initial commit (local scaffold)
$ git log --oneline origin/main
9f8e7d6 Initial commit (README from GitHub)
```

The two logs had completely different starting commits, with no shared ancestor at all — which is exactly what "unrelated histories" means.

## Why This Happens

Git normally assumes that any two branches being merged diverged from the same starting commit at some point. But running `git init` locally and separately creating a GitHub repository with an auto-generated README produces two branches that each start from their own, entirely independent initial commit — there's no common ancestor between them.

Since Git 2.9, `git merge` (and `git pull`, which calls merge internally) refuses this kind of "no shared ancestor" merge by default, as a safety measure. That refusal is exactly what shows up as `fatal: refusing to merge unrelated histories`. It's intentional behavior meant to stop two genuinely unrelated projects from being accidentally combined into one repository — not a bug.

## Solution

### 1. Confirm the histories are unrelated for a benign reason

Compare `git log --oneline` against `git log --oneline origin/main` first, to confirm this is just "both sides got initialized independently" rather than something more serious. If either side has commits you can't afford to lose, cut a backup branch before merging.

```bash
git branch backup-local
```

### 2. Re-run the pull with `--allow-unrelated-histories`

If merging the two unrelated histories is actually what you want, pass the flag explicitly.

```bash
git pull origin main --allow-unrelated-histories
```

```text
Merge made by the 'ort' strategy.
 README.md | 3 +++
 1 file changed, 3 insertions(+)
 create mode 100644 README.md
```

That combined the local initial commit and GitHub's README commit into a single history, and `git push` worked normally after that.

### 3. Resolve conflicts the normal way if they come up

If both sides happened to create the same file (for example, both have a `README.md`), it resolves like any other merge conflict.

```bash
git status
```

```text
both added:      README.md
```

```bash
# edit README.md to keep whatever content you actually want
git add README.md
git commit
```

### 4. Avoid the situation entirely next time

Going forward, creating the GitHub repository without the README/`.gitignore`/license auto-generation options, then pushing the local `git init` project into that empty repo, gives both sides a single shared history from the start — so this error never comes up.

```bash
git remote add origin git@github.com:example/myproject.git
git push -u origin main
```

## Gotchas

- Without knowing the `--allow-unrelated-histories` flag existed, the error message alone made it look like something was wrong with the remote configuration. In reality the remote URL and branch name were both correct — only the ancestry was the problem.
- Re-running `git pull` repeatedly without the flag just produced the same error every time.
- After merging with `--allow-unrelated-histories`, I'd also created a local `README.md` separately from GitHub's, so the merge itself succeeded but the file contents conflicted. Merging unrelated histories can succeed at the history level while still leaving file-level conflicts to resolve.

## FAQ

**Q: Isn't `--allow-unrelated-histories` risky to use?**
It is, if you're actually trying to merge two genuinely unrelated projects by mistake. Check `git log` on both sides first to confirm this is really just "both got initialized independently," then pass the flag.

**Q: Does `git fetch` + `git merge` behave the same way as `git pull`?**
Yes — the same merge logic runs underneath, so you'd need `git merge origin/main --allow-unrelated-histories` there too.

**Q: How do I avoid this happening again?**
When creating a new repository on GitHub, leave the README/`.gitignore`/license auto-generation unchecked so it starts empty, and do the first push from your local repository. That way both sides share one history from the very first commit.

## Related Articles

- [How to Push to GitHub for the First Time](/en/github-first-push)
- [How to Fix a Merge Conflict After git pull](/en/git-pull-merge-conflict)
- [Basic Git Branch Commands: Create and Switch via CLI](/en/git-branch-basics)
