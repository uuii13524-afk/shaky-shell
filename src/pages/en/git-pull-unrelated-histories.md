---
title: 'Fix "fatal: refusing to merge unrelated histories" in git pull'
date: '2026-09-07'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git pull fails with "fatal: refusing to merge unrelated histories" when you connect a local project to a GitHub repo created separately with its own README. Here is why, and how to merge them safely with --allow-unrelated-histories.'
en_tags: ['Git', 'unrelated histories', 'git pull']
---

## What I Was Trying to Do

I had already started a project called `myapp` locally, and only afterward created a matching repository on GitHub. On GitHub I had checked "Add a README file" when creating it, so it already had its own initial commit. Locally, I already had an initial commit containing `src/index.js`.

```bash
git remote add origin /path/to/remote-repo
git pull origin main --no-rebase
```

```text
From /path/to/remote-repo
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

`git pull` failed immediately with `fatal`, and neither the remote's `README.md` nor the local `src/index.js` got merged. `git status` showed no changes at all — the working tree was still just my original local commit.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- Local repository: one initial commit on `main` (containing `src/index.js`)
- Remote repository: one initial commit on `main`, created on GitHub with "Add a README file" checked (containing `README.md`)
- The two histories share no common commit — the remote was only connected afterward with `git remote add`

## What I Tried

My first attempt was just running `git pull origin main`, assuming Git would figure out how to combine the two.

```bash
git pull origin main
```

```text
From /path/to/remote-repo
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
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

With `pull.rebase` unset, Git 2.43 stops here first. Since I wanted a merge, I followed the hint and re-ran with `--no-rebase`.

```bash
git pull origin main --no-rebase
```

```text
From /path/to/remote-repo
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

This time the reason was explicit: unrelated histories. Comparing both branches with `git log --oneline --all` confirmed it — there wasn't a single commit in common between the two commit graphs.

## Why This Happens

By default, Git refuses to merge two branches that share **no common ancestor commit**. It treats this not as an intentional integration but as a likely accident — merging two repositories that happen to be unrelated.

That's exactly what had happened here:

- Local: history starting from `4a0ec66 Initial local commit`
- Remote: history starting from `1922d36 Initial commit (created on GitHub)`

Both are "first commits," but neither is an ancestor of the other. Checking "Add a README file" when creating a repository on GitHub generates an initial commit that has nothing to do with any local history you already have. Connecting that repo later with `git remote add` will always produce this situation. This isn't a bug — it's Git's safety guard against silently mixing unrelated history.

## Solution

### 1. Confirm merging unrelated histories is actually intended

Compare the contents of both repositories with `git log --oneline --all` and by looking at the actual files, to rule out accidentally merging two unrelated projects. In my case, the intent was clear: keep the local implementation and just pull in the README from GitHub. So I proceeded.

### 2. Re-run with `--allow-unrelated-histories`

```bash
git pull origin main --no-rebase --allow-unrelated-histories
```

```text
From /path/to/remote-repo
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

No file paths overlapped, so Git created the merge commit automatically with no conflicts.

### 3. Resolve conflicts if any file paths overlap

If both repositories contain a file with the same path, it shows up as a normal merge conflict. Open the file, resolve it manually, then stage and commit.

```bash
git status
git add <competing-file>
git commit
```

## Verify It Works

```bash
git log --oneline --graph --all
```

```text
*   db77580 Merge branch 'main' of /path/to/remote-repo
|\  
| * 1922d36 Initial commit (created on GitHub)
* 4a0ec66 Initial local commit
```

`git status` reported `nothing to commit, working tree clean`, and `ls` confirmed both the remote's `README.md` and the local `src/index.js` were present in the working tree.

## Gotchas

- Running `git pull` alone first stops at the `pull.rebase` hint, before you even get to the `unrelated histories` error. If you search for `--allow-unrelated-histories` online and tack it on without also passing `--no-rebase` (or setting `pull.rebase false`), you'll keep getting stuck at the same earlier step.
- `--allow-unrelated-histories` only tells Git it's okay to merge two histories with no common ancestor — it does not resolve content conflicts for you. Any file that exists in both repositories under the same path still turns into a normal merge conflict, so comparing the two repos' contents beforehand is worth the extra minute.
- Checking "Add a README file" when creating a repo on GitHub is what produces an initial commit unrelated to any local history. If you already have local commits before creating the remote repo, creating it empty (unchecked) avoids this problem entirely.

## FAQ

**Q: Is it safe to just add `--allow-unrelated-histories`?**
It's safe once you've confirmed the two histories genuinely belong to the same project. If you use it to force through a merge with a truly unrelated project, you'll end up with a repository containing files that were never meant to be mixed together.

**Q: Which comes first, the `pull.rebase` hint or the `unrelated histories` error?**
Since Git 2.9, running `git pull` with `pull.rebase` unset stops at the "divergent branches" hint first. Only after you explicitly choose a reconciliation method (`--no-rebase`, `--rebase`, etc.) does Git go on to check for a common ancestor and surface the `unrelated histories` error.

**Q: How do I avoid this situation from the start?**
When creating a remote repository on GitHub for a project that already has local commits, uncheck "Add a README file" (and license/gitignore) so the remote starts empty, and do your first push from the local repository instead of pulling from the remote.

## Related Articles

- [Fix a Rejected git push](/en/git-push-rejected-fix)
- [Fix "fatal: not a git repository"](/en/git-fatal-not-a-git-repository)
- [Managing Git Remotes (add/remove/rename)](/en/git-remote-operations)
- [Resolving Merge Conflicts on git pull](/en/git-pull-merge-conflict)
- [Basic Git Branch Operations](/en/git-branch-basics)
