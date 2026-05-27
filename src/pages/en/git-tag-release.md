---
title: 'How to Manage Git Tags and Releases'
date: '2026-05-21'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Git', 'タグ', 'リリース', 'バージョン管理']
en_tags: ['Git', 'tag', 'release', 'version management']
description: 'How to create, push, and delete Git tags for version management. Also covers creating a GitHub Release from a tag.'
---
## What Are Tags?

Tags attach a name to a specific commit — commonly used for release version numbers.

## Create a Tag

### Lightweight Tag

```bash
git tag v1.0.0
```

### Annotated Tag (Recommended)

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
```

### Tag a Past Commit

```bash
git log --oneline
git tag -a v1.0.0 COMMIT_ID -m "Release version 1.0.0"
```

## View Tags

```bash
git tag              # List all tags
git tag -l "v1.*"    # Filter by pattern
git show v1.0.0      # Tag details
```

## Push Tags to Remote

```bash
git push origin v1.0.0        # Push a specific tag
git push origin --tags        # Push all tags
```

## Delete Tags

```bash
git tag -d v1.0.0                    # Delete local tag
git push origin --delete v1.0.0      # Delete remote tag
```

## Create a GitHub Release

1. Go to the repository on GitHub
2. "Releases" → "Create a new release"
3. Select a tag or type a new tag name
4. Add release notes → "Publish release"

## Common Pitfalls

- Tags don't push automatically — you must push them explicitly
- Annotated tags store author, date, and message; lightweight tags do not
- Semantic versioning (`v1.0.0`) is the standard convention

You can also trigger a GitHub Actions workflow on tag push. See [GitHub Actions: Basic Auto-Deploy Setup](/en/github-actions-basic).

## Related Posts

- [How to Push Your First Repository to GitHub](/en/github-first-push)
- [Git Branch Basics: Create and Switch Branches](/en/git-branch-basics)
- [GitHub Actions: Basic Auto-Deploy Setup](/en/github-actions-basic)
- [How to View Commit History with git log](/en/git-log-history)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
