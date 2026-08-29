---
title: 'Fix: npm ci Fails Because package.json and package-lock.json Are Out of Sync'
date: '2026-08-29'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'A GitHub Actions deploy workflow fails on npm ci with an EUSAGE error saying package.json and package-lock.json are out of sync. Here is the cause and how to fix it by re-syncing the lock file with npm install.'
en_tags: ['Node.js', 'npm ci', 'package-lock.json']
---

## What I Was Trying to Do

I deploy a Node.js app to a VPS from GitHub Actions over SSH. The workflow is straightforward: instead of `npm install`, the dependency install step uses `npm ci`, since I want deterministic dependency resolution in CI. That was a deliberate choice, not an accident.

```yaml
- name: Install dependencies
  run: npm ci

- name: Build
  run: npm run build
```

A teammate wanted to add `dayjs` for date handling, so they added one line to `dependencies` in `package.json` directly and pushed. Locally they had forgotten to run `npm install`, but `dayjs` already happened to be sitting in `node_modules` from other work, so local testing showed no problem at all.

After the push, the `npm ci` step in GitHub Actions failed.

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
```

Since it never reproduced locally, my first assumption was that it was some CI-specific caching issue.

## Environment

- OS: Ubuntu 24.04.4 LTS (same family on both the GitHub Actions runner and the deploy VPS)
- Node.js: v22.22.2
- npm: 10.9.7
- `package-lock.json`: `lockfileVersion: 3`
- CI: GitHub Actions (`npm ci` for a clean install, then `npm run build`)

## What I Tried

I first suspected the `actions/setup-node` cache configuration. `cache: 'npm'` was set, but the cache key is just a hash of `package-lock.json`, so it seemed unlikely the cache itself was corrupted. Just in case, I temporarily added `cache: false` and re-ran the workflow.

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: false
```

Same error. Once caching was ruled out, I read the error message more carefully. The line `Missing: dayjs@1.11.23 from lock file` was npm plainly telling me that `dayjs` had no entry in `package-lock.json`. That's when it clicked: this wasn't a CI problem, it was the pushed commit itself.

Checking the repo locally confirmed it — `package-lock.json` had no `dayjs` entry.

```bash
grep '"dayjs"' package-lock.json || echo "dayjs is NOT in package-lock.json"
```

```text
dayjs is NOT in package-lock.json
```

Because `package.json` had been hand-edited without running `npm install`, the dependency graph was never recalculated, and the lock file was left stale.

## Root Cause

`npm ci` and `npm install` look similar but resolve dependencies fundamentally differently. `npm install` treats `package.json` as the source of truth and updates the lock file as needed. `npm ci` does the opposite: it treats `package-lock.json` (or `npm-shrinkwrap.json`) as the strict source of truth, and if it doesn't match `package.json`, it refuses to install anything and exits immediately with an error. That strictness is exactly why `npm ci` is recommended for CI and Docker builds — it guarantees an install that matches the lock file byte for byte. It's a deliberate design choice, not a bug.

Here's what actually happened, step by step:

1. `dayjs` was added by hand to `dependencies` in `package.json`.
2. `npm install` was never run, so `package-lock.json` stayed in its old state, unaware of `dayjs`.
3. `dayjs` happened to already exist in the local `node_modules` from unrelated work, so `npm run dev` and similar commands worked fine locally, hiding the inconsistency.
4. Both `package.json` and the (stale) `package-lock.json` were committed and pushed as-is.
5. On a fresh GitHub Actions environment, `npm ci` detected that `dayjs` existed in `package.json` but not in `package-lock.json`, and failed with EUSAGE.

So the root cause wasn't CI at all — it was a commit that changed `package.json` without regenerating the lock file. What made this hard to spot is that an existing local `node_modules` directory can mask the inconsistency entirely.

## How I Fixed It

### 1. Check the state of package-lock.json

```bash
grep '"dayjs"' package-lock.json || echo "dayjs is NOT in package-lock.json"
```

```text
dayjs is NOT in package-lock.json
```

Confirmed the newly added dependency wasn't reflected in the lock file.

### 2. Regenerate the lock file with npm install

```bash
npm install
```

```text
added 1 package, and audited 71 packages in 641ms

16 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

`npm install` looks at `package.json` and resolves only what's missing, so it didn't unnecessarily bump any existing dependency versions. Only the one package related to `dayjs` was added.

### 3. Confirm it's reflected in package-lock.json

```bash
grep -m1 '"dayjs"' package-lock.json
```

```text
"dayjs": "^1.11.11",
```

Confirmed `dayjs` was now correctly present in both the dependency entry and its resolved package.

### 4. Reproduce npm ci locally before pushing again

You can run the same check locally before pushing back to CI.

```bash
npm ci
```

```text
added 70 packages, and audited 71 packages in 998ms

16 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

It completed without error, which meant CI should now behave the same way.

### 5. Commit package-lock.json along with package.json and push

```bash
git add package.json package-lock.json
git commit -m "fix: sync package-lock.json after adding dayjs"
git push
```

It's easy to commit only `package.json` and forget to include the updated `package-lock.json`. Always check `git status` to make sure both are staged before committing.

## Verify It Works

After pushing, the GitHub Actions workflow re-ran and the `npm ci` step completed without error. I also re-verified locally from a completely clean state.

```bash
rm -rf node_modules
npm ci
```

```text
added 70 packages, and audited 71 packages in 998ms

16 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

Confirmed that dependencies reproduce correctly from the lock file even after removing `node_modules` entirely.

## Takeaways

- `npm ci` treats `package-lock.json` as the strict source of truth and fails immediately with EUSAGE if it doesn't match `package.json`. That's by design — it's what makes CI and Docker builds reproducible.
- An existing local `node_modules` can hide the inconsistency, since the package is already present even though the lock file doesn't know about it. Get in the habit of running `npm install` right after any manual edit to `package.json`, before committing.
- Running `npm ci` locally before pushing catches this kind of mismatch before CI does. Always commit `package.json` and `package-lock.json` together.

## FAQ

**Q: Why use `npm ci` instead of `npm install` in CI or Docker builds at all?**
`npm install` can install slightly different versions on different runs, depending on the version ranges (`^`, `~`) in `package.json`. `npm ci` only ever installs the exact versions recorded in `package-lock.json`. For CI and Docker builds where you want dependencies to stay identical across builds, `npm ci` is the better fit.

**Q: Does `--legacy-peer-deps` or `--force` work around this?**
No. This error isn't a peer dependency conflict — it's a genuine mismatch between the contents of `package.json` and `package-lock.json`. The only real fix is running `npm install` to regenerate the lock file so it matches `package.json` again.

**Q: Is it fine to not commit package-lock.json at all?**
`npm ci` requires the lock file to exist, so excluding `package-lock.json` from the repo means `npm ci` can't be used at all. If you want dependency versions pinned, `package-lock.json` needs to be committed too.

## Related Articles

- [Fix: npm ERESOLVE Error When Installing Packages](/en/npm-eresolve-error)
- [Fix: npm install Fails with EACCES Permission Error](/en/npm-install-permission-denied)
- [How to Clear the npm Cache](/en/npm-cache-clear)
- [Speeding Up GitHub Actions by Caching node_modules](/en/github-actions-node-cache)
- [Switching Node.js Versions with nvm](/en/node-version-management-nvm)
