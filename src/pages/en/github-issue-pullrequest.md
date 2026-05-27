---
title: 'GitHub Issues and Pull Requests: How to Use Them'
date: '2026-05-21'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['GitHub', 'Issue', 'Pull Request', 'チーム開発']
en_tags: ['GitHub', 'Issue', 'Pull Request', 'team development']
description: 'How to use GitHub Issues for task tracking and Pull Requests for code review. Covers the basic team development workflow from branch to merge.'
---
## What Are Issues?

Issues are used for bug reports, feature requests, and task tracking.

### Create an Issue

1. Open the repository on GitHub
2. "Issues" tab → "New issue"
3. Enter a title and description → "Submit new issue"

### Useful Issue Template

```markdown
## Problem
What is happening?

## Steps to Reproduce
1.
2.
3.

## Expected Behavior
What should happen?

## Environment
- OS:
- Version:
```

## What Are Pull Requests?

Pull Requests let you propose code changes and get them reviewed before merging.

### Pull Request Workflow

```bash
# 1. Create a branch
git switch -c feature/fix-bug

# 2. Make changes and commit
git add .
git commit -m "fix: resolve the bug"

# 3. Push to GitHub
git push -u origin feature/fix-bug
```

4. Create a Pull Request on GitHub
5. Request a review
6. Merge after approval

### Link a PR to an Issue

Adding these keywords to the PR body automatically closes the linked issue on merge:

```
fix #123
closes #123
resolves #123
```

## Common Pitfalls

- Avoid pushing directly to `main` without a review
- Use descriptive branch names that convey the purpose
- Issue numbers can be auto-linked to PRs

Before opening a PR, consider cleaning up commits with [git rebase Basics](/en/git-rebase-basics) to make the diff easier to review.

## Related Posts

- [How to Push Your First Repository to GitHub](/en/github-first-push)
- [Git Branch Basics: Create and Switch Branches](/en/git-branch-basics)
- [GitHub Actions: Basic Auto-Deploy Setup](/en/github-actions-basic)
- [Generate an SSH Key and Add It to GitHub](/en/ssh-key-github)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
