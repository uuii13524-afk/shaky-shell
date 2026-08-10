---
title: 'Fix: git merge "fatal: refusing to merge unrelated histories"'
date: '2026-08-10'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Merging two separately-initialized git repos fails with "fatal: refusing to merge unrelated histories". Here is the cause and how to fix it with --allow-unrelated-histories, plus the add/add conflict that follows.'
en_tags: ['Git', 'merge', 'unrelated histories']
---

## What I Was Trying to Do

I had an old, small repo of personal scripts (`old-scripts`) that I wanted to fold into a newer, actively-developed repo (`main-project`). Just copying the files over would have thrown away the commit history — when and why each change was made — so instead I added `old-scripts` as a remote, fetched it, and tried to `merge` it in so the history would come along with it.

```bash
cd main-project
git remote add old-scripts ../old-scripts
git fetch old-scripts
git merge old-scripts/master
```

The merge was rejected immediately with this error:

```text
fatal: refusing to merge unrelated histories
```

The `fetch` itself had worked fine — `git log old-scripts/master` showed the remote's commits without any problem. Only the `merge` step was being blocked.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- Source repo: `old-scripts` (created with a standalone `git init`, one commit)
- Target repo: `main-project` (created with a standalone `git init`, one commit, with a history completely unrelated to `old-scripts`)

To confirm the exact behavior, I reproduced the same setup in a minimal test case:

```bash
mkdir repoA && cd repoA && git init -q
echo "# Project A" > README.md
git add README.md && git commit -q -m "Initial commit A"

cd .. && mkdir repoB && cd repoB && git init -q
echo "# Project B" > README.md
git add README.md && git commit -q -m "Initial commit B"

git remote add origin-a ../repoA
git fetch origin-a -q
git merge origin-a/master
```

```text
fatal: refusing to merge unrelated histories
```

Same error, reproduced.

## What I Tried

My first assumption was that I had set up the remote or the fetch incorrectly, so I checked that the remote was registered and that the commits were actually reachable.

```bash
git remote -v
```

```text
origin-a	/path/to/repoA (fetch)
origin-a	/path/to/repoA (push)
```

```bash
git log origin-a/master --oneline
```

```text
4dc2c0e Initial commit A
```

The remote was registered correctly and the fetch had worked — I could see `origin-a/master`'s commit locally. So fetching was fine; only merging was being refused. Searching for the exact phrase "unrelated histories" led me to the discovery that this is a safety mechanism Git added in version 2.9, not a bug.

## Root Cause

By default, `git merge` assumes the two branches being merged share a common ancestor commit. But two repositories that were each created with their own separate `git init` have no common ancestor at all — they are, structurally, completely unrelated projects.

Before Git 2.9, this merge would silently succeed, which occasionally caused real accidents — for example, running `git pull` in the wrong directory and unintentionally merging in the contents of an unrelated repository. To prevent that class of mistake, Git 2.9 introduced a guard: by default, it refuses to merge two histories that don't share a common ancestor. `fatal: refusing to merge unrelated histories` is exactly that guard firing — it's intentional, not a malfunction.

In my case, merging two genuinely unrelated histories on purpose was exactly the scenario this guard exists to flag, so bypassing it deliberately was the correct move.

## How I Fixed It

### 1. Merge with `--allow-unrelated-histories`

This flag tells Git to skip the common-ancestor check and proceed with the merge.

```bash
git merge origin-a/master --allow-unrelated-histories
```

```text
Auto-merging README.md
CONFLICT (add/add): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

The guard was bypassed, but now both repositories had a `README.md` with different content, so Git flagged an `add/add` conflict. This is expected when merging unrelated histories — it's resolved the same way as any other merge conflict.

### 2. Check the conflict state

```bash
git status
```

```text
On branch master
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both added:      README.md
```

```bash
cat README.md
```

```text
<<<<<<< HEAD
# Project B
=======
# Project A
>>>>>>> origin-a/master
```

Both the `HEAD` side (the `main-project` equivalent) and the `origin-a/master` side (the `old-scripts` equivalent) are shown between the conflict markers.

### 3. Resolve the conflict and commit

I manually edited the file to combine both, then removed the conflict markers.

```bash
cat > README.md <<'EOF'
# Project B

Merged history from Project A.
EOF

git add README.md
git commit -m "Merge project-a into project-b (unrelated histories)"
```

Noting `--allow-unrelated-histories` in the commit message makes it easier for anyone reading the history later to understand why this merge looks the way it does.

## Verify It Works

The commit graph after the merge shows the two independent histories joined into one.

```bash
git log --graph --oneline --all
```

```text
*   351b7cd Merge project-a into project-b (unrelated histories)
|\
| * 4dc2c0e Initial commit A
* 8215240 Initial commit B
```

And `git status` confirms the working tree is clean again.

```bash
git status
```

```text
On branch master
nothing to commit, working tree clean
```

All the commits that used to live only in `old-scripts` are now part of `main-project`'s history, joined in as a branch.

## Takeaways

- `fatal: refusing to merge unrelated histories` is a safety check introduced in Git 2.9 for merges between two histories that share no common ancestor commit — it's not a failure state, it's Git asking you to confirm this is intentional.
- If you genuinely want to combine unrelated histories, `git merge <branch> --allow-unrelated-histories` bypasses the check. That alone doesn't resolve file-level conflicts, though — expect an `add/add` conflict on any file that exists in both histories, and resolve it like any normal merge conflict.
- If you hit this error unexpectedly (wrong remote, wrong branch), don't reach for the flag right away — first confirm with `git remote -v` and `git log <remote>/<branch> --oneline` that you're actually merging what you think you're merging.

## FAQ

**Q: Is `--allow-unrelated-histories` always safe to use?**
It's safe when the two histories genuinely represent the same content that was tracked separately. If you point it at a completely unrelated project by mistake, though, its entire file tree gets pulled in — always check `git log <remote>/<branch> --oneline` before merging.

**Q: How do I back out of the merge partway through?**
As long as you haven't committed yet, `git merge --abort` returns you to the state before the merge started. In this walkthrough, that's still an option right after the `add/add` conflict appears, since nothing had been committed at that point.

**Q: Does `git pull` hit the same error?**
Yes. `git pull` is `fetch` plus `merge` under the hood, so pulling from a remote with no common ancestor produces the same `fatal: refusing to merge unrelated histories`. Fix it the same way: `git pull <remote> <branch> --allow-unrelated-histories`.

## Related Articles

- [Fix "remote rejected" on git push: File Exceeds GitHub's 100MB Limit](/en/git-push-large-file-rejected)
- [Resolving Merge Conflicts on git pull](/en/git-pull-merge-conflict)
- [Basic git remote Operations](/en/git-remote-operations)
- [Recovering Commits with git reflog](/en/git-reflog)
- [Fix: git clone Leaves Files as Git LFS Pointer Text Instead of Real Content](/en/git-clone-lfs-pointer-file)
