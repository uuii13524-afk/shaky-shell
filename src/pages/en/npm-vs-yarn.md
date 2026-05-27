---
title: 'npm vs yarn: Differences and When to Use Each'
date: '2026-05-11'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Node.js', 'npm', 'yarn', 'パッケージマネージャー']
en_tags: ['Node.js', 'npm', 'yarn', 'package manager']
description: 'A comparison of npm and yarn covering command syntax, lock files, and speed. Includes a quick-reference command table to help you decide which to use.'
---
## Command Comparison

| Action | npm | yarn |
|--------|-----|------|
| Install all deps | `npm install` | `yarn` |
| Add a package | `npm install pkg` | `yarn add pkg` |
| Run a script | `npm run script` | `yarn script` |
| Remove a package | `npm uninstall pkg` | `yarn remove pkg` |

## Which Should You Use?

- `package-lock.json` exists in the repo → use **npm**
- `yarn.lock` exists in the repo → use **yarn**
- Starting fresh with no preference → **npm** is fine

## Common Pitfalls

- Don't mix npm and yarn in the same project
- If working in a team, pick one and stick with it

The GitHub Actions cache setting differs between npm and yarn. See [Speed Up GitHub Actions Builds with Node.js npm Cache](/en/github-actions-node-cache) and use `cache: 'npm'` or `cache: 'yarn'` accordingly.

## Related Posts

- [npm Command Not Working on Windows](/en/windows-npm-not-working)
- [Fix npm Cache Problems](/en/npm-cache-clear)
- [Manage Node.js Versions with nvm](/en/node-version-management-nvm)
- [How to Use package.json Scripts to Automate Tasks](/en/npm-package-json-scripts)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
