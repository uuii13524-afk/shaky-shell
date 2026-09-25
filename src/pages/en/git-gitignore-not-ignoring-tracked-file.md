---
title: 'Fix: .gitignore Has No Effect on a File git status Keeps Showing as Modified'
date: '2026-09-25'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Adding .env to .gitignore did not stop git status from showing it as modified on every edit. The cause was that the file was already tracked. Here is how to fix it with git rm --cached.'
en_tags: ['Git', '.gitignore', 'git rm --cached']
---

## What I Was Trying to Do

In a small Node.js side project, I kept database connection details in a `.env` file. I forgot to set up `.gitignore` before the very first commit, so `.env` ended up committed along with everything else. Once I noticed, I added it to `.gitignore` afterward.

```bash
printf 'node_modules/\n.env\n' > .gitignore
git status --short
```

```text
?? .gitignore
```

At that point `.env` didn't show up in `git status`, so I assumed it was already ignored. But after I edited `.env` to update a password and saved it, `git status` picked the change up anyway.

```bash
echo "DB_PASS=changed_after_gitignore" >> .env
git status --short
```

```text
 M .env
?? .gitignore
```

Even though `.env` was listed in `.gitignore`, its changes kept showing up every time. I assumed my `.gitignore` pattern syntax was wrong and spent a while second-guessing that instead.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- Node.js: v22.22.2
- npm: 10.9.7
- Project layout: a small repo with just `.env` (DB credentials), `.gitignore`, and `index.js`

## What I Tried

First I re-checked the contents of `.gitignore`.

```bash
cat .gitignore
```

```text
node_modules/
.env
```

The pattern itself looked correct. Next I checked whether the pattern actually matched `.env` using `git check-ignore`.

```bash
git check-ignore -v .env
echo "exit=$?"
```

```text
exit=1
```

No output, and the exit code was `1` (no match). It looked like the pattern wasn't being recognized at all, so I tried rewriting it as `/.env`, then `**/.env`, but nothing changed the result.

At that point I stopped guessing at syntax and instead checked what git actually considers tracked right now, with `git ls-files`.

```bash
git ls-files
```

```text
.gitignore
index.js
.env
```

`.env` showed up in the `git ls-files` output. In other words, `.env` was already **tracked** by git. No amount of rewriting `.gitignore` was ever going to change that.

## Root Cause

`.gitignore` only affects files that are not yet tracked by git. **It has no effect whatsoever on a file that has already been `git add`-ed and committed.**

In this case, the very first commit — made before `.gitignore` existed — included `.env` via `git add .`, so `.env` was tracked from day one. Adding `.env` to `.gitignore` afterward changes nothing, because git already decided, in a past commit, to track that file.

That also explains why `git check-ignore -v .env` produced no output (exit code `1`): by default, `git check-ignore` does not evaluate ignore patterns against files that are already tracked. It wasn't a syntax problem at all. In fact, running the exact same command again after untracking the file with `git rm --cached` does report a match:

```bash
git check-ignore -v .env
```

```text
.gitignore:2:.env	.env
```

Without knowing that `check-ignore` only evaluates untracked paths, it's easy to keep blaming the `.gitignore` syntax indefinitely.

## Resolution Steps

### 1. Remove the file from git's index only, not from disk

```bash
git rm --cached .env
```

```text
rm '.env'
```

The `--cached` flag removes `.env` from git's tracking (the index) while leaving the actual file on disk untouched. Forgetting `--cached` would delete the physical file as well, so it's worth double-checking before running this.

### 2. Check the status

```bash
git status --short
```

```text
D  .env
?? .gitignore
```

`.env` is now staged as removed (untracked), and `.gitignore` still shows as untracked alongside it.

### 3. Commit `.gitignore` together with the untrack change

```bash
git add .gitignore
git commit -m "add gitignore and untrack .env"
```

```text
[main 2f779ab] add gitignore and untrack .env
 2 files changed, 2 insertions(+), 1 deletion(-)
 create mode 100644 .gitignore
```

This records the fact that `.env` was deliberately untracked, right in the commit history.

### 4. Confirm future edits are now ignored

```bash
echo "DB_PASS=another_change" >> .env
git status --short
```

```text
(no output)
```

Editing `.env` again produces no output from `git status` at all. The `.gitignore` rule is finally taking effect.

## Verification

Just to be sure, I re-checked the list of tracked files with `git ls-files`.

```bash
git ls-files
```

```text
.gitignore
index.js
```

`.env` is gone from the list, leaving only `index.js` and `.gitignore` tracked. I also checked the commit log.

```bash
git log --oneline
```

```text
2f779ab add gitignore and untrack .env
570018c initial commit
```

The untrack commit is right there in the history, as expected.

## Summary

- `.gitignore` only applies to untracked files. Once a file has been `git add`-ed and committed, listing it in `.gitignore` does nothing.
- `git check-ignore -v <file>` produces no output (exit code `1`) for an already-tracked file. That's not a sign of a syntax error — it's a sign the file is out of scope for the check. Run `git ls-files` first to confirm whether the file is actually tracked before touching your `.gitignore` patterns.
- To fix a file that got tracked by mistake, run `git rm --cached <file>` to untrack it while keeping the file on disk, then commit that together with `.gitignore`. Note that any secret already baked into past commits (like the password in `.env` here) still lives in history even after `rm --cached` — for a repo that's already public, you'll also need to rotate the leaked credential and consider rewriting history.

## FAQ

**Q: Does `git rm --cached .env` delete my local `.env` file too?**
No. With `--cached`, only git's tracking (the index) is affected; the file itself stays on disk untouched. If you forget `--cached` and run plain `git rm .env`, the physical file gets deleted along with the tracking.

**Q: What about the contents of `.env` (like the password) that are already in past commits?**
`git rm --cached` only stops tracking it going forward — the file's contents remain in the commit history. If the repository is already public, you need to both scrub the history (e.g. with `git filter-repo`) and rotate any credential that may have been exposed, such as regenerating the password or API key.

**Q: I added a whole directory to `.gitignore`, but some files inside it still aren't ignored.**
This is usually the same root cause. If some files inside that directory were individually `git add`-ed in an earlier commit, they stay tracked regardless of the directory-level pattern. Run `git ls-files <directory>` to see what's actually tracked in there, and untrack the unwanted ones with `git rm --cached`.

## Related Articles

- [How to Set Up .gitignore and Exclude Files from Git](/en/git-gitignore-setup)
- [How to Undo a Git Commit (Before and After Push)](/en/git-commit-undo)
- [How to Manage Environment Variables with .env Files in docker-compose](/en/docker-compose-env-file)
- [How to Create a GitHub Repository and Push for the First Time](/en/github-first-push)
- [Linux File Permissions Guide (chmod/chown)](/en/linux-file-permissions)
