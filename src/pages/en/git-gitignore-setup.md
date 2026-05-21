---
title: 'How to Set Up .gitignore and Exclude Files from Git'
date: '2026-05-09'
category: 'Git'
---

## What I Wanted to Do

Keep `node_modules`, `.env` files, and build output out of my Git repository.

## What Is .gitignore?

A file that tells Git which files and folders to ignore. Place it at the root of your project named `.gitignore`.

## Basic Syntax

```
# Comment

# Ignore a specific file
secret.txt

# Ignore a folder
node_modules/

# Ignore by extension
*.log
*.env

# Ignore build output
dist/
.cache/
```

## Recommended .gitignore for Astro Projects

```
node_modules/
dist/
.env
.env.local
.astro/
*.log
.DS_Store
```

## When .gitignore Doesn't Work

If a file was already committed, adding it to `.gitignore` won't help — Git keeps tracking it.

### Fix

```bash
git rm -r --cached filename-or-folder
git add .
git commit -m "stop tracking filename"
```

The `--cached` flag removes the file from Git tracking without deleting it from your disk.

## Generate a .gitignore Automatically

Visit https://www.toptal.com/developers/gitignore and enter your tech stack (Node, Astro, Windows, etc.) to generate a tailored `.gitignore`.

## Key Points

- Place `.gitignore` at the project root
- Never commit `.env` files — they often contain API keys and secrets
- The trailing `/` on a folder name (e.g. `node_modules/`) means ignore the directory
- Already-committed files need `git rm --cached` to stop being tracked

## Related Articles

- [How to Create Your First GitHub Repository and Push](/en/github-actions-basic)
- [How to Undo a Git Commit](/en/git-commit-undo)
- [GitHub Actions: Using Secrets for Sensitive Data](/posts/github-actions-secrets)
