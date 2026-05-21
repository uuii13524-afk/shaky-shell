---
title: 'How to Clear npm Cache and Fix Install Issues'
date: '2026-05-09'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
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
