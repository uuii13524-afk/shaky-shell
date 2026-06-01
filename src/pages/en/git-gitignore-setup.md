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

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
