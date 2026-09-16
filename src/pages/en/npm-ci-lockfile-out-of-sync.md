---
title: 'Fix: npm ci Fails With "can only install packages when your package.json and package-lock.json...are in sync"'
date: '2026-09-16'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm ci fails with an EUSAGE error in CI right after adding a dependency to package.json without updating the lockfile. Here is the cause and how to fix it by re-syncing package-lock.json with npm install.'
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## What I Was Trying to Do

I added one lightweight dependency to a test repo. Locally, I just added a line under `dependencies` in `package.json` and was about to commit without touching `package-lock.json`. To reproduce the CI steps locally before pushing, I removed `node_modules` and ran `npm ci`.

```bash
rm -rf node_modules
npm ci
```

Installation didn't even start — it failed immediately.

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
```

Since I normally only ever run `npm install`, this was the first time I'd seen this message, and I initially assumed the problem was deleting `node_modules` first, or an outdated npm version.

## Environment

- OS: Ubuntu 24.04 LTS (container)
- Node.js: v22.22.2
- npm: 10.9.7
- Before adding the dependency: `package.json` listed only `left-pad`, and `package-lock.json` matched it
- After adding the dependency: `is-odd` was added to `package.json`, but `package-lock.json` was still the old, unupdated version

## What I Tried

First I checked the npm version, which wasn't unusually old.

```bash
npm --version
```

```text
10.9.7
```

Next I suspected a cache issue and tried clearing it, but nothing changed.

```bash
npm cache clean --force
rm -rf node_modules
npm ci
```

```text
npm error code EUSAGE
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
```

The exact same error kept appearing. Only then did I actually read the message body carefully and realize the `Missing: is-odd@3.0.1 from lock file` line was pointing straight at the dependency I had just hand-added to `package.json`.

## Root Cause

Unlike `npm install`, `npm ci` treats `package-lock.json` (or `npm-shrinkwrap.json`) as the single source of truth and builds `node_modules` strictly according to what's written there. It cross-checks the lockfile against `package.json`, and if there is any mismatch at all, it **aborts immediately without installing anything**.

In this case, `is-odd` had been added to `dependencies` in `package.json`, but `package-lock.json` still only reflected `left-pad`. `npm ci` detected a dependency being required that wasn't recorded in the lockfile, and stopped with `Missing: is-odd@3.0.1 from lock file`.

`npm install` would have silently detected and fixed this mismatch by updating the lockfile for you, but `npm ci` has no such auto-repair behavior — by design. It exists specifically to guard against a lockfile silently drifting out of sync in CI environments, where you want the exact same dependency tree every single run, not whatever the resolver happens to pick that day. In practice, this means most cases of "it works locally with `npm install` but fails in CI's `npm ci` step" come down to exactly this: someone edited `dependencies` or `devDependencies` in `package.json` and forgot to commit the resulting lockfile update alongside it.

## How I Fixed It

### 1. Check package.json

```bash
cat package.json
```

```json
{
  "name": "npmci-test",
  "version": "1.0.0",
  "dependencies": {
    "left-pad": "^1.3.0",
    "is-odd": "^3.0.1"
  }
}
```

Confirmed `is-odd` was there.

### 2. Re-sync the lockfile with npm install

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 452ms

found 0 vulnerabilities
```

This resolved `is-odd` along with its own dependency, `is-number`, and wrote both into `package-lock.json`.

### 3. Confirm the lockfile was updated

```bash
grep -A2 '"is-odd"' package-lock.json
```

Entries for `is-odd` and `is-number` were now present in `package-lock.json`.

### 4. Re-run npm ci

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 457ms

found 0 vulnerabilities
```

This time it installed cleanly with no error.

## Verify It Works

I checked that `node_modules` contained exactly the expected packages.

```bash
ls node_modules
```

```text
is-number  is-odd  left-pad
```

`package.json`, `package-lock.json`, and `node_modules` were all consistent, and running `npm ci` repeatedly after that produced no further errors.

## Takeaways

- `npm ci` requires `package.json` and `package-lock.json` to match exactly — it will not auto-repair a mismatch the way `npm install` does.
- Whenever you add or change a dependency, run `npm install` once to refresh `package-lock.json` before committing. If your CI uses `npm ci`, forgetting to commit the updated lockfile will break the build every time.
- If something works locally but fails only in CI's `npm ci` step, check the `Missing: ... from lock file` line in the error first — it names the exact package that was added to `package.json` but never made it into the lockfile.

## FAQ

**Q: What's the benefit of `npm ci` over `npm install`?**
`npm ci` reproduces `package-lock.json` exactly, avoiding subtle version drift between different developers' machines and CI runs. It also always removes any existing `node_modules` before installing, so it doesn't inherit a dependency tree that's already gone stale or inconsistent.

**Q: Is it fine to gitignore package-lock.json?**
Not if you rely on `npm ci`. Without a `package-lock.json` in the repository, `npm ci` can't run at all and fails immediately with `The npm ci command can only install with an existing package-lock.json`.

**Q: How can CI catch this before it breaks the build?**
Add a check — in a pre-commit hook or a separate CI step — that runs `npm install --package-lock-only` and fails if it produces a diff in `package-lock.json`. That catches an out-of-sync lockfile before the real `npm ci` step ever runs.

**Q: Does this only happen after manually editing package.json?**
No. It also shows up after resolving a merge conflict that touches `package-lock.json`, after switching branches that added different dependencies, or after an editor's "quick fix" auto-adds an import without running an installer. Any path that changes what `package.json` requires without also regenerating the lockfile ends the same way.

## Related Articles

- [Fix ERESOLVE Errors During npm install](/en/npm-eresolve-error)
- [Fix EACCES Permission Errors During npm install](/en/npm-install-permission-denied)
- [How to Clear the npm Cache](/en/npm-cache-clear)
- [Speed Up CI Builds With Node.js Caching in GitHub Actions](/en/github-actions-node-cache)
- [How to Write package.json Scripts](/en/npm-package-json-scripts)
