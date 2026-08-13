---
title: 'Fix: npm ci Fails Because package.json and package-lock.json Are Out of Sync'
date: '2026-08-13'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'A GitHub Actions build breaks with an EUSAGE error from npm ci. Adding a dependency to package.json without updating package-lock.json triggers it. Here is the cause and how to fix it with npm install.'
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## What I Was Trying to Do

I wanted to add the `is-odd` package as a dependency to a small Node.js tool. I edited `package.json` directly in my editor, adding `"is-odd": "^3.0.1"` to `dependencies`, then committed and pushed.

```bash
git add package.json
git commit -m "add is-odd dependency"
git push origin main
```

I hadn't run `npm install` locally — I assumed the CI pipeline's `npm ci` step would just install whatever was in `package.json`. It didn't. The GitHub Actions build failed with this error:

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
```

Since I hadn't run `npm install` or `npm run build` locally after the edit, I decided to reproduce the same steps on my own machine first.

## Environment

- OS: Ubuntu (containerized CI runner / sandbox)
- Node.js: v22.22.2
- npm: 10.9.7
- Packages: `left-pad@1.3.0` (existing dependency), `is-odd@3.0.1` (newly added)
- CI: GitHub Actions, using `npm ci` in the install step

## What I Tried

First, I removed `node_modules` locally and ran the exact command CI uses, to see if it reproduced.

```bash
rm -rf node_modules
npm ci
```

The exact same `EUSAGE` error showed up locally.

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
```

That ruled out a CI-specific environment difference — the problem was in what I'd actually pushed. Next I checked whether `package-lock.json` contained `is-odd` at all.

```bash
grep -c '"is-odd"' package-lock.json
```

```text
0
```

I had added `is-odd` to `package.json` but never touched `package-lock.json`, so of course there was no matching entry. Reading the error more carefully, it wasn't just complaining about `is-odd` itself — it also flagged `is-number@6.0.0`, one of `is-odd`'s own dependencies, as missing from the lock file. That's when it clicked: `npm ci` installs exactly what `package-lock.json` describes, and it never resolves or rewrites the lock file to match changes in `package.json` on its own.

## Root Cause

`npm install` and `npm ci` sound interchangeable but do different jobs. `npm install` reads `package.json`, resolves the dependency tree as needed, and updates `package-lock.json` to match — it's the "resolve and install" command. `npm ci`, on the other hand, installs exactly what's already recorded in `package-lock.json` (or `npm-shrinkwrap.json`), with no resolution step at all — it's a fast, reproducible install meant for CI.

So when a new package is added to `dependencies` in `package.json` but the corresponding update to `package-lock.json` is skipped, `npm ci` detects that the two files disagree and refuses to install anything. This isn't a CI quirk — it's npm working exactly as designed, catching a lock file that was never regenerated after a manual edit.

## How I Fixed It

### 1. Run `npm install` locally to update the lock file

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 425ms

found 0 vulnerabilities
```

This pulled in `is-odd` and its dependency `is-number`, and updated `package-lock.json` accordingly.

### 2. Confirm the package now shows up in the lock file

```bash
grep -c '"is-odd"' package-lock.json
```

```text
1
```

```bash
node -p "require('./package-lock.json').packages['node_modules/is-odd'].version"
```

```text
3.0.1
```

`package-lock.json` now had a proper `is-odd@3.0.1` entry under `packages`.

### 3. Verify `npm ci` passes locally before pushing again

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 413ms

found 0 vulnerabilities
```

No more `EUSAGE` error — the install completed cleanly.

### 4. Commit both package.json and package-lock.json together

```bash
git add package.json package-lock.json
git commit -m "sync package-lock.json with is-odd dependency"
git push origin main
```

Committing `package-lock.json` alongside `package.json` is the actual fix here, not just a follow-up step.

## Verify It Works

After pushing, the `npm ci` step in the GitHub Actions build log completed successfully. I also reproduced the whole flow from a clean state locally to double-check.

```bash
rm -rf node_modules package-lock.json
npm install
rm -rf node_modules
npm ci
```

```text
added 3 packages, and audited 4 packages in 0.9s

found 0 vulnerabilities
```

Even starting from a freshly regenerated `package-lock.json`, `npm install` followed by `npm ci` completed without error.

## Summary

- `npm ci` reproduces exactly what `package-lock.json` describes — it never resolves or reconciles differences with `package.json` on its own. Any manual edit to `package.json` needs a follow-up `npm install` to keep the lock file in sync.
- The `Missing: <package>@<version> from lock file` line in the error tells you exactly what's missing — including transitive dependencies pulled in by the package you added, not just the package itself.
- If your CI uses `npm ci`, running `rm -rf node_modules && npm ci` locally before pushing catches this kind of drift before it ever reaches the build log.

## Related Articles

- [Fix: npm install ERESOLVE Error](/en/npm-eresolve-error)
- [Fix: npm install Fails with EACCES Permission Denied](/en/npm-install-permission-denied)
- [How to Clear the npm Cache](/en/npm-cache-clear)
- [Caching node_modules in GitHub Actions](/en/github-actions-node-cache)
- [Switching Node.js Versions with nvm](/en/node-version-management-nvm)
