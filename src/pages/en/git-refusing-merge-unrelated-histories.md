---
title: 'Fix "fatal: refusing to merge unrelated histories" on git pull (Git 2.43)'
date: '2026-10-06'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git pull or git merge fails with "fatal: refusing to merge unrelated histories". How to confirm there is no common ancestor, merge with --allow-unrelated-histories, and resolve the README add/add conflict.'
ja_tags: ['Git', 'unrelated histories', 'git pull', 'merge']
en_tags: ['Git', 'unrelated histories', 'git pull', 'merge']
---

## What I Was Trying to Do

I had started a project locally with `git init`, then added a remote repository that was created on GitHub with a README already in it. I wanted to bring the two together, so I ran `git pull origin main` and got this:

```text
From ../remote
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

`git merge origin/main` fails with the same message:

```text
fatal: refusing to merge unrelated histories
```

I reproduced this with a local bare repository, so the remote shows as `../remote.git` instead of a GitHub URL. Everything else below is real output from that run.

## Environment

- OS: Linux (kernel 6.18)
- Git: 2.43.0
- Setup: a bare repository (`remote.git`) plus a separate repository created with `git init`
- Branch: `main`

## What I Tried

Pushing first is the natural move, and it is rejected:

```bash
git push -u origin main
```

```text
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '../remote.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally.
```

A bare `git pull` with no `pull.rebase` setting then stops on a different error:

```text
hint: You have divergent branches and need to specify how to reconcile them.
fatal: Need to specify how to reconcile divergent branches.
```

That one only asks you to choose merge or rebase. With `--no-rebase`, the real error appears:

```bash
git pull origin main --no-rebase
```

```text
fatal: refusing to merge unrelated histories
```

## Why This Happens

The two branches have **no common ancestor commit**. A merge starts from the merge base, and without one Git refuses by default (since Git 2.9). You can confirm it directly:

```bash
git fetch origin
git merge-base main origin/main
echo "exit=$?"
```

```text
exit=1
```

With a shared history, `merge-base` prints a commit hash. Here it prints nothing and exits with `1`. Each side starts from its own root commit, which is why `git log --oneline --all` shows two unconnected commits:

```text
125e717 first local commit
3616893 Initial commit (remote)
```

Common ways to end up here: running `git init` locally and then adding a GitHub repo created with a README or LICENSE; combining two separately initialized projects; or deleting `.git`, re-running `git init`, and pulling from the old remote.

## Solution

### 1. Make sure the histories should be joined

`--allow-unrelated-histories` tells Git you really mean it. If you pointed at the wrong remote, you would mix two unrelated projects, so check first:

```bash
git remote -v
git log --oneline origin/main
```

### 2. Merge with --allow-unrelated-histories

```bash
git pull origin main --allow-unrelated-histories --no-rebase --no-edit
```

If no file names overlap, this finishes cleanly:

```text
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

```text
*   5ba6043 Merge branch 'main' of ../remote
|\  
| * 3616893 Initial commit (remote)
* 125e717 first local commit
```

### 3. Resolve add/add conflicts

The more common case is that both sides have a `README.md`:

```text
Auto-merging README.md
CONFLICT (add/add): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

`git status -sb` marks the file `AA` (added on both sides):

```text
## main
AA README.md
```

The file contains ordinary conflict markers:

```text
# my-app

<<<<<<< HEAD
local notes
=======
Created on GitHub
>>>>>>> origin/main
```

Edit the file to keep what you want, remove the markers, then:

```bash
git add README.md
git commit --no-edit
```

Use `git merge --abort` to back out.

### 4. Rebase instead

Rebase also works, and it did not need `--allow-unrelated-histories` in my test, because it replays your commits on top of the target rather than computing a merge base. With a conflicting README it stops per commit:

```bash
git rebase origin/main
```

```text
Could not apply a2112a0... first local commit
```

Fix the file, `git add` it, then `git rebase --continue` (or `git rebase --abort`).

## Merge or Rebase: Which One to Pick

Both ended in the same place in my reproduction, but they leave different history. The merge keeps both root commits and adds one merge commit, so you can see exactly where the two lines of work were joined. That is the safer choice when the remote already has commits other people have pulled, because nothing that is already shared gets rewritten.

The rebase produces a straight line by re-creating your local commits on top of the remote ones. Their hashes change, which is harmless for a local-only history like the one here, but a problem if you had already pushed those commits somewhere else. If you are unsure, merge. It is also the easier one to undo: before you push, `git reset --hard ORIG_HEAD` returns you to the state just before the merge, while an interrupted rebase is abandoned with `git rebase --abort`.

One more check that costs nothing: run `git log --oneline --all --graph` before and after. Before, you see two separate lines with no connection. After, you see them join at a single merge commit. If the graph still shows two disconnected lines, the merge did not happen and the push will fail the same way as before.

## Verify the Fix

After merging, the push is a normal fast-forward:

```bash
git push -u origin main
```

```text
To ../remote.git
   3616893..5ba6043  main -> main
branch 'main' set up to track 'origin/main'.
```

`git merge-base main origin/main` now prints a hash and exits with `0`.

## Summary

- The error means the two branches share no ancestor. An empty `git merge-base` output confirms it.
- Once you know the histories belong together, use `git pull origin main --allow-unrelated-histories` and resolve any `add/add` conflicts by hand.
- To avoid it next time, create the GitHub repo empty (no README) and push your local repo to it, or `git clone` first and work in the clone.

## FAQ

**Q: Is `--allow-unrelated-histories` safe?**
Yes if you have verified the remote is the right project. If you merged the wrong one, `git reset --hard ORIG_HEAD` undoes the merge before you push.

**Q: Why do I also get "divergent branches" hints?**
That is a separate message about choosing merge or rebase. Setting `git config --global pull.rebase false` (or `true`) silences it, but it does not fix unrelated histories.

**Q: I want the local copy to replace the remote history.**
`git push --force-with-lease` does that, but it discards the remote history. Agree on it with collaborators first.

## Related Articles

- [Fix git pull Merge Conflicts](/en/git-pull-merge-conflict)
- [Fix git push Rejected Errors](/en/git-push-rejected-fix)
- [How to Create a GitHub Repository and Push for the First Time](/en/github-first-push)
- [Git Remote Repository Operations (remote/fetch/pull/push)](/en/git-remote-operations)
