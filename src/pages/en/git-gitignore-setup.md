---
title: 'How to Set Up .gitignore and Exclude Files from Git'
date: '2026-05-09'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
---

## Basic Syntax

```
node_modules/
dist/
.env
*.log
.DS_Store
```

## When .gitignore Doesn't Work

```bash
git rm -r --cached filename
git add .
git commit -m "stop tracking filename"
```

## Generate Automatically

Visit https://www.toptal.com/developers/gitignore

## Key Points

- Never commit `.env` files
- Already-committed files need `git rm --cached`

## Related Articles

- [How to Undo a Git Commit](/en/git-commit-undo)
- [GitHub Actions Secrets](/posts/github-actions-secrets)
