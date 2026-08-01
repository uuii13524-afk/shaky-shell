---
title: 'Fix "npm ci can only install packages when your package.json and package-lock.json are in sync"'
date: '2026-08-01'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm ci fails in CI with "can only install packages when your package.json and package-lock.json are in sync" after a manual edit to package.json. Here is why this happens and how to regenerate the lockfile correctly.'
en_tags: ['Node.js', 'npm', 'package-lock.json']
---

## What I Was Trying to Do

I wanted to bump a dependency version, so instead of running `npm install`, I just edited one line directly in `package.json`'s `dependencies` and committed it. Locally everything kept working fine because `node_modules` was already installed, but the `npm ci` step in GitHub Actions started failing.

```bash
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Invalid: lock file's dayjs@1.11.10 does not satisfy dayjs@1.11.11
npm error
npm error Clean install a project
```

`npm install` had been passing silently every time locally, so at first I had no idea what was actually "out of sync."

## Environment

- OS: Ubuntu 22.04.4 LTS (GitHub Actions `ubuntu-latest` runner)
- Node.js: v20.14.0
- npm: 10.7.0
- CI: GitHub Actions (`actions/setup-node@v4` + `npm ci`)
- The manual edit: added `"dayjs": "^1.11.11"` directly to `dependencies` in `package.json`, without touching `package-lock.json`

## What I Tried

First I ran `npm ci` again locally to see if the failure reproduced outside CI.

```bash
npm ci
```

```text
npm error code EUSAGE
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error Invalid: lock file's dayjs@1.11.10 does not satisfy dayjs@1.11.11
```

It reproduced locally too, which meant this wasn't a CI-only quirk — the `package-lock.json` committed to the repo genuinely disagreed with `package.json`. Checking `git diff` on the most recent commit confirmed only `package.json` had changed; `package-lock.json` hadn't been touched.

```bash
git log --oneline -3 -- package.json package-lock.json
```

```text
a1b2c3d Update dependency version in package.json
```

No commit had touched `package-lock.json` at all, which confirmed the manual edit was the cause.

## Why This Happens

`npm install` reads `package.json` on every run and, if needed, automatically updates `package-lock.json` to match. `npm ci` works the opposite way: **it treats `package-lock.json` as the source of truth and installs exactly what's listed there, without resolving anything itself.**

I had changed the `dayjs` version constraint in `package.json` from `^1.11.10` to `^1.11.11` by hand, but the corresponding entry in `package-lock.json` still pointed at the old resolved version, `1.11.10`. `npm ci` checks upfront whether the two files agree, and refuses to install anything if they don't. `npm install` never surfaced this locally because it silently fixes the mismatch and moves on — which is exactly why I didn't notice the repo was already broken.

## Solution

### 1. Confirm the lockfile state

```bash
npm ci --dry-run
```

Confirms the `EUSAGE` error and shows which package is out of sync.

### 2. Regenerate the lockfile with `npm install`

Treat `package.json` as the source of truth and regenerate `package-lock.json` from it.

```bash
npm install
```

```text
added 0 packages, removed 0 packages, changed 1 package, and audited 842 packages in 3s
```

### 3. Check the diff

Confirm the affected package's version was actually updated in the lockfile.

```bash
git diff package-lock.json | grep -A 2 '"dayjs"'
```

```diff
-      "version": "1.11.10",
+      "version": "1.11.11",
```

### 4. Commit the updated lockfile

```bash
git add package.json package-lock.json
git commit -m "fix: sync package-lock.json with package.json"
git push
```

### 5. Re-verify with `npm ci`

```bash
rm -rf node_modules
npm ci
```

Confirming `npm ci` passes locally before pushing fixes the CI failure at the same time.

## Verify It Works

```bash
npm ci
```

```text
added 842 packages, and audited 843 packages in 12s
found 0 vulnerabilities
```

Installation completed with no errors, and re-running the GitHub Actions workflow confirmed the `npm ci` step passed.

## Gotchas

- `npm install` silently auto-fixes any mismatch between `package.json` and `package-lock.json`, which is exactly why I didn't catch this locally. Now I avoid hand-editing `dependencies` directly and instead always go through an npm command like `npm install <package>@<version>`.
- Because CI was already set up to use `npm ci` instead of `npm install`, this got caught before merge instead of shipping to production with an unintended version.
- `package-lock.json` conflicts are common in merges, and resolving them by hand tends to reintroduce this exact problem. If it conflicts, don't edit it manually — delete and regenerate it with `npm install`.

## FAQ

**Q: Do I need to run `npm install` every time I edit `package.json`?**
Yes. If you edit `dependencies` or `devDependencies` directly, run `npm install` before committing so `package-lock.json` stays in sync. Adding or changing versions through npm itself, e.g. `npm install <package>@<version>`, makes this hard to forget.

**Q: Should CI use `npm ci` or `npm install`?**
Use `npm ci` for CI and deployments, anywhere reproducibility matters. It skips dependency resolution and installs exactly what's in the lockfile, which makes it both faster and able to catch mismatches like this one early.

**Q: Should `package-lock.json` be committed to the repo at all?**
Yes, for application projects it should be committed. Without it, different machines and CI runs can resolve different dependency versions, and `npm ci` won't work at all.

## Related Articles

- [Fixing npm ERESOLVE Errors](/en/npm-eresolve-error)
- [Fixing npm install Permission Denied Errors](/en/npm-install-permission-denied)
- [How to Clear the npm Cache](/en/npm-cache-clear)
- [npm vs yarn: Key Differences](/en/npm-vs-yarn)
- [Switching Node.js Versions with nvm](/en/node-version-management-nvm)
