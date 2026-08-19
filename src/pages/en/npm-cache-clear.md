---
title: 'How to Clear npm Cache and Fix Install Issues'
date: '2026-05-09'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Fix broken npm installs with npm cache clean --force, or do a full reset by deleting node_modules and package-lock.json before running npm install again.'
---

## Clear the Cache

```bash
npm cache clean --force
```

## Full Reset

**Mac / Linux:**

```bash
rm -rf node_modules
rm package-lock.json
npm install
```

**Windows:**

```
rmdir /s /q node_modules
del package-lock.json
npm install
```

## When to Use This

- npm install fails with a strange error
- A package update doesn't take effect
- You switched Node.js versions and something broke

## Related Articles

- [npm vs yarn](/posts/npm-vs-yarn)
- [Node.js Version Management with nvm](/posts/node-version-management-nvm)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
