---
title: 'Fix "remote rejected" on git push: File Exceeds GitHub''s 100MB Limit'
date: '2026-08-02'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git push fails with "remote rejected" because a committed file exceeds GitHub''s 100MB limit. Here is how to strip it from history with git filter-repo and prevent it from happening again with Git LFS.'
en_tags: ['Git', 'GitHub', 'large file']
---

## What I Was Trying to Do

In a personal repo called `study-notes`, I added a sample video file for some docs, `assets/demo.mp4` (about 105MB), committed it, and tried to push to GitHub.

```bash
git add assets/demo.mp4
git commit -m "add demo video for docs"
git push origin main
```

The commit itself went through fine, but the push stopped partway with this error:

```text
remote: error: GH001: Large files detected. You may want to try Git Large File Storage - https://git-lfs.github.com.
remote: error: Trace: 3f5a1e2b8c9d4a7f6e2c1b0a9d8e7f6c5b4a3d2e
remote: error: See http://git.io/iEPt8g for more information.
remote: error: File assets/demo.mp4 is 105.34 MB; this exceeds GitHub's file size limit of 100.00 MB
To github.com:example-user/study-notes.git
 ! [remote rejected] main -> main (pre-receive hook declined)
error: failed to push some refs to 'github.com:example-user/study-notes.git'
```

What confused me at first was that `git commit` succeeded, only `git push` was rejected. Locally everything looked fine, so it wasn't obvious what was actually wrong.

## Environment

- OS: Ubuntu 22.04.4 LTS
- Git: 2.43.0
- Remote: GitHub.com (private repo, SSH)
- Git LFS: not installed yet (part of the root cause)
- File in question: `assets/demo.mp4` (105.34 MB)

## What I Tried

My first assumption was that since only the push failed, I just needed to remove the file and push again. So I added a new commit that deletes it.

```bash
git rm assets/demo.mp4
git commit -m "remove large demo video"
git push origin main
```

```text
remote: error: File assets/demo.mp4 is 105.34 MB; this exceeds GitHub's file size limit of 100.00 MB
To github.com:example-user/study-notes.git
 ! [remote rejected] main -> main (pre-receive hook declined)
error: failed to push some refs to 'github.com:example-user/study-notes.git'
```

The file was gone from both the working tree and the index, but I got the exact same rejection. That's when it clicked: the push isn't rejecting "the current file list" — it's rejecting every object contained in the commits it's about to send. Adding a new commit that removes the file doesn't touch the earlier commit, which still has the 105MB blob sitting in it, and that earlier commit was still part of what `push` was trying to send.

I confirmed where the blob actually lived in history:

```bash
git rev-list --objects --all | grep demo.mp4
```

```text
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 assets/demo.mp4
```

Sure enough, the object was still there. Deleting the file from the working tree was never going to be enough.

## Root Cause

GitHub's server-side `pre-receive` hook rejects any push containing a blob larger than 100.00 MB (files over 50MB only trigger a warning and still go through). This check runs against every object in the commits being pushed, not just the current tree state — so **removing a file in a later commit does nothing if an earlier commit in the same push still contains that file's blob.**

In my case, `git commit -m "remove large demo video"` only removed the file from the working directory going forward; `git log` still showed both the commit that added the file and the one that removed it, and push was trying to send both. Unless the history itself is rewritten, that 105MB blob stays part of the repository's object set and keeps getting sent — this is expected behavior on both Git's and GitHub's side, not a bug.

## How I Fixed It

### 1. Find the commit that introduced the large file

```bash
git log --oneline --all -- assets/demo.mp4
```

```text
7c8d9e0 remove large demo video
4b5c6d7 add demo video for docs
```

This confirms the blob is sitting in an earlier commit.

### 2. Re-clone into a separate directory before rewriting history

Rewriting history isn't reversible, so I didn't touch my existing working copy — I cloned fresh into a separate folder to work in.

```bash
git clone git@github.com:example-user/study-notes.git study-notes-cleanup
cd study-notes-cleanup
```

### 3. Strip the file from history with `git filter-repo`

`git filter-repo` is the officially recommended successor to `git filter-branch`. I used it to remove `assets/demo.mp4` from every commit.

```bash
sudo apt install git-filter-repo
git filter-repo --path assets/demo.mp4 --invert-paths
```

`--invert-paths` means "remove exactly this path from history," rather than "keep only this path."

### 4. Confirm the object is gone

```bash
git rev-list --objects --all | grep demo.mp4
```

Empty output means the blob has been removed from every commit.

### 5. Force-push the rewritten history

After confirming I was the only one working on this branch, I overwrote the remote with the rewritten history.

```bash
git push origin --force --all
git push origin --force --tags
```

```text
Enumerating objects: 42, done.
...
To github.com:example-user/study-notes.git
 + 4b5c6d7...9f8e7d6 main -> main (forced update)
```

This time there was no `pre-receive hook declined`, and the push completed normally.

### 6. Switch to Git LFS for large files going forward

To avoid repeating this, I moved video and other binary files that tend to grow large over to Git LFS.

```bash
git lfs install
git lfs track "*.mp4"
git add .gitattributes
git commit -m "track mp4 files with Git LFS"
```

## Verify It Works

```bash
git push origin main
```

```text
Everything up-to-date
```

After re-adding a file of similar size, it was tracked as an LFS pointer as configured, and the push succeeded without issue.

```bash
git add assets/demo.mp4
git commit -m "re-add demo video via LFS"
git push origin main
```

```text
Uploading LFS objects: 100% (1/1), 105 MB | 4.2 MB/s, done.
Enumerating objects: 4, done.
...
To github.com:example-user/study-notes.git
   9f8e7d6..1a2b3c4  main -> main
```

No more `pre-receive hook declined`, and the push reached the remote cleanly.

## Gotchas

- Adding a commit that deletes the file doesn't remove the blob from earlier commits — it only adds a new commit on top. Since push sends every commit in the range, the delete-only approach never actually solved anything.
- `git filter-repo` refuses to run by default unless you're working from a fresh clone, as a safety measure. Trying to run it directly in my existing working copy got blocked, so cloning fresh first was the faster path anyway.
- Force-pushing rewritten history diverges from anyone else's local copy of the branch. This was my own private repo, so it was fine, but on a shared branch this needs to be coordinated with the team first.
- GitHub's limit works in two tiers — a warning past 50MB, a hard rejection past 100MB. It's easy to miss the warning and only notice once you cross 100MB, like I did here.

## FAQ

**Q: Would Git LFS from the start have avoided this?**
Yes. Files tracked by LFS are stored as small pointer files in the regular Git history, not the actual binary content, so they never trigger the 100MB check. Setting up `.gitattributes` for large file types before adding them is the safer default.

**Q: Should I use `git filter-repo` or `BFG Repo-Cleaner`?**
Git's own docs now recommend `git filter-repo` over `git filter-branch`. For a simple "strip this path from all history" task either tool works, but I went with `git filter-repo` since it's actively maintained and has clearer options.

**Q: Can I push files between 50MB and 100MB?**
Yes, though you'll see a warning. I'd treat that warning as a signal to move the file to LFS before the repo grows further, rather than ignoring it until it becomes a hard rejection.

## Related Articles

- [Fixing "rejected" Errors on git push](/en/git-push-rejected-fix)
- [Basic git rebase Operations](/en/git-rebase-basics)
- [Recovering Commits with git reflog](/en/git-reflog)
- [How to Use git stash](/en/git-stash-usage)
- [Troubleshooting My First Push to GitHub](/en/github-first-push)
