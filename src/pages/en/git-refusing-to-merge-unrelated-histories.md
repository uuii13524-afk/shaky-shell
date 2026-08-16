---
title: 'How to Fix Git "fatal: refusing to merge unrelated histories"'
date: '2026-08-16'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Pulling a GitHub-created repo into an existing local project can fail with fatal: refusing to merge unrelated histories. This post explains why it happens and how to merge the two histories safely.'
ja_tags: ['Git', 'unrelated histories', 'git pull']
en_tags: ['Git', 'unrelated histories', 'git pull']
---

## What I Was Trying to Do

I already had a local project with `git init` run and a few commits in place. I created a brand-new repository on GitHub with the "Add a README file" box checked, added it as a remote with `git remote add origin`, and ran `git pull origin main` expecting it to just merge in the README. Instead, nothing got pulled and I hit this:

```text
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint:
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
hint:
fatal: Need to specify how to reconcile divergent branches.
```

Following the hint, I set `git config pull.rebase false` and ran the pull again. This time the error changed:

```text
From /path/to/remote
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

`git log` still showed zero commits from the remote on my local branch, so my first reaction was confusion — I hadn't actually merged anything yet, so why was Git refusing?

## Environment

- OS: Ubuntu 22.04.4 LTS
- Git: 2.43.0
- Local side: an already-initialized repo with `package.json` committed
- Remote side: a GitHub repo created with "Add a README file" checked, containing only `README.md` and `.gitignore`

## What I Tried

My first assumption was that I just hadn't configured a reconciliation strategy, so I explicitly set the merge strategy and tried again:

```bash
git config pull.rebase false
git pull origin main
```

```text
From /path/to/remote
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

The error message changed but the pull was still refused. Next, I tried just fetching the remote's commits without merging, to see what Git actually had:

```bash
git fetch origin
git log --oneline --graph --all
```

```text
* 989fccd (origin/main) Initial commit on GitHub
* ea52b33 (HEAD -> main) Initial local commit
```

The graph made it obvious: these weren't two commits on a shared branch that had diverged — they were two completely separate histories with no common ancestor at all. That's when I realized this wasn't a missing-config problem; I was trying to merge two repositories that had never shared a starting point.

## Why This Happens

`git pull` is shorthand for `git fetch` followed by `git merge` (or `rebase`). A normal merge computes the diff between two branches starting from their common ancestor commit. In this case, both the local repo (via `git init`) and the remote repo (via GitHub's initial commit) started as independent histories with no shared ancestor whatsoever. Git detects this as an "unrelated histories" situation and refuses to merge by default, to prevent an accidental merge of two unrelated projects. This has been the default behavior since Git 2.9 — merging without a common ancestor is exactly the kind of operation that's easy to trigger by mistake (e.g. in CI), so it requires an explicit opt-in.

## Solution

### 1. Explicitly allow the unrelated-histories merge

Once you know the root cause is "no common ancestor," the fix is just telling Git that you're doing this on purpose:

```bash
git pull origin main --allow-unrelated-histories
```

```text
From /path/to/remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 .gitignore | 1 +
 README.md  | 1 +
 2 files changed, 2 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 README.md
```

In my case there were no filename collisions, so Git auto-generated the merge commit with no conflicts. If both repos happen to have a file with the same name but different content (a `README.md` on both sides, for example), it shows up as a standard merge conflict at this point — open the file, resolve it by hand, `git add` it, and complete the merge as usual.

### 2. Verify the merge result

```bash
git log --oneline --graph --all
```

```text
*   5b1c0b3 Merge branch 'main' of /path/to/remote
|\
| * 989fccd Initial commit on GitHub
* ea52b33 Initial local commit
```

If both independent histories now show up joined by a single merge commit, and your working tree contains both the local `package.json` and the remote's `README.md`/`.gitignore`, the merge succeeded.

### 3. Push as normal

Once the merge is done, `git push origin main` works exactly as it would for any other commit — the merge commit already contains both histories, so nothing special is needed to push it.

```bash
git push origin main
```

## Gotchas

- I initially fixated on the first error (`Need to specify how to reconcile divergent branches`) and assumed a missing `pull.rebase` setting was the whole problem. The real cause — no common ancestor — only showed up in the second error message, so it's worth reading both instead of stopping at the first hint.
- `--allow-unrelated-histories` sounds dangerous, but it only permits Git to attempt the merge calculation without a common ancestor. Conflict detection still works exactly as it would in a normal merge, so it won't silently overwrite one side's changes.
- This fix assumes you're on the `merge` reconciliation strategy (`pull.rebase false`). If you had `pull.rebase true` configured instead, the failure mode is different and you'd need something like `git rebase --root` rather than this approach.

## FAQ

**Q: Can `--allow-unrelated-histories` wipe out files from one of the two repositories?**
Not by itself. The flag only allows Git to attempt a merge without a shared ancestor — file-level diffing and conflict detection work exactly as they do in any other merge. If the same filename exists with different content on both sides, it's flagged as a normal merge conflict rather than silently overwritten.

**Q: Is there a way to make this the default so I don't have to type the flag every time?**
There's no persistent config option for this. Merging unrelated histories isn't something that happens in a normal day-to-day workflow, so Git requires it to be an explicit, one-time opt-in rather than a default — that's the whole point of the safeguard.

**Q: Could I have avoided this by unchecking "Add a README file" when creating the GitHub repo?**
Yes. If you create the remote as a completely empty repository and push your existing local history to it as the very first commit, there's no second, independent history on the remote side, so this conflict never comes up. If you've already created it with a README and hit this error, the steps above are the quickest way out.

## Related Articles

- [Fixing "git push" Rejected Errors](/en/git-push-rejected-fix)
- [Resolving Merge Conflicts on git pull](/en/git-pull-merge-conflict)
- [A Complete Guide to Your First git push](/en/github-first-push)
- [Adding, Changing, and Removing Git Remotes](/en/git-remote-operations)
- [Fixing "fatal: not a git repository"](/en/git-fatal-not-a-git-repository)
