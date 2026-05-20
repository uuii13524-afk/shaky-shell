---
title: 'How to Clear npm Cache and Fix Install Issues'
date: '2026-05-09'
category: 'Node.js'
---

## Symptoms

- Package installs fail or hang
- Old version of a package keeps running despite updates
- Mysterious errors after switching Node.js versions

## Clear the Cache

```bash
npm cache clean --force
```

## Full Reset: Delete node_modules and Reinstall

This is the most reliable fix for stubborn issues.

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

## Verify Cache Is Clean

```bash
npm cache verify
```

## When to Use This

- npm install fails with a strange error
- A package update doesn't seem to take effect
- You switched Node.js versions and something broke
- You're resuming a project after a long break

## Key Points

- `--force` is required — without it, npm may skip the clean
- Deleting `node_modules` is safe — it can always be regenerated from `package.json`
- Deleting `package-lock.json` resets the dependency resolution — use with care in team projects

## Related Articles

- [npm vs yarn: Which Should You Use?](/posts/npm-vs-yarn)
- [Node.js Version Management with nvm](/posts/node-version-management-nvm)
- [Windows npm Command Not Found Fix](/posts/windows-npm-not-working)
