---
title: 'Fix: npm ci Fails With "can only install packages when...are in sync"'
date: '2026-09-06'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Right after adding a dependency to package.json, npm ci in CI fails with a lock file mismatch error. Here is the cause and how to fix it by running npm install before npm ci.'
en_tags: ['Node.js', 'npm', 'npm ci']
---

## What I Was Trying to Do

I added `dayjs` as a new dependency to an internal test project. Locally, I only edited `package.json` directly and never touched `package-lock.json`. To reproduce the exact steps CI runs, I ran `npm ci` on my machine.

```bash
cd npmci-repro
npm ci
```

Instead of starting the install, it stopped immediately with an error.

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
npm error
npm error Clean install a project
```

Since I normally only use `npm install`, it wasn't obvious why adding a line to `package.json` alone wasn't enough — why did I need to go through `npm install` first?

## Environment

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Project: started with only `lodash` as a dependency, then `dayjs` was added to `package.json` by hand (`package-lock.json` was never regenerated)

## What I Tried

My first guess, based on the `code EUSAGE` string alone, was that my npm version was too old. I checked with `npm -v` and got 10.9.7, which isn't unusually old.

Next I assumed a stale `node_modules` was the problem, so I removed it and ran `npm ci` again.

```bash
rm -rf node_modules
npm ci
```

Same result — the exact same `Missing: dayjs@1.11.23 from lock file` message came back. That ruled out `node_modules` as the cause.

Only then did I actually check the contents of `package-lock.json`.

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

`package.json` listed `dayjs`, but `package-lock.json` had zero entries for it. That's when it clicked: `npm ci` doesn't resolve dependencies from `package.json` at all.

## Root Cause

`npm install` reads `package.json` on every run and resolves dependencies, updating `package-lock.json` as needed. `npm ci`, on the other hand, installs **exactly** what's recorded in `package-lock.json` (or `npm-shrinkwrap.json`) — it does no dependency resolution of its own, and if what's in `package.json` doesn't match what's in the lock file, it refuses to proceed and errors out.

In this case, `dayjs` had been added to `package.json`, but `npm install` had never been run afterward, so `package-lock.json` still had no record of it. `npm ci` detected that mismatch and rejected it with `EUSAGE`.

The line `Missing: dayjs@1.11.23 from lock file` is pointing at exactly that gap: `package.json` requests a version range (`^1.11.10`), but the lock file has no resolved version recorded for it. `npm ci` doesn't try to fix this automatically — it just tells you to run `npm install` first and stops. Given that the whole point of using `npm ci` in CI is to pin installs to an exact, reproducible set of versions, refusing to silently resolve a new dependency on the fly is the intended safety behavior, not a bug.

## How I Fixed It

### 1. Check the lock file's state

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

Confirmed the dependency added to `package.json` wasn't reflected in `package-lock.json`.

### 2. Sync the lock file with npm install

```bash
npm install
```

```text
added 2 packages, and audited 3 packages in 923ms

found 0 vulnerabilities
```

This updates `package-lock.json` to match `package.json`.

### 3. Confirm the dependency is now in the lock file

```bash
grep -c '"dayjs"' package-lock.json
```

```text
1
```

The count went from 0 to 1.

### 4. Run npm ci again

```bash
npm ci
```

```text
added 2 packages, and audited 3 packages in 833ms

found 0 vulnerabilities
```

It completed without any error.

## Verify It Works

I checked `node_modules` to confirm both packages were actually installed.

```bash
ls node_modules | wc -l
```

```text
2
```

`lodash` and `dayjs` were both present, and the same `npm ci` command now succeeds in CI as well. Going forward, the rule is: whenever `package.json` changes, run `npm install` locally and commit the updated `package-lock.json` in the same commit.

## Takeaways

- `npm ci` does not resolve dependencies from `package.json` — it strictly reproduces what's already recorded in `package-lock.json`. Any mismatch between the two makes it fail with `EUSAGE`.
- Editing `package.json` by hand and committing it without running `npm install` afterward will break `npm ci` in CI, even though a plain `npm install` locally would have "worked" and hidden the problem.
- The `Missing: <package>@<version> from lock file` line tells you exactly which package is out of sync — check the lock file for that package with `grep` before assuming something else (npm version, cached `node_modules`) is at fault.

## FAQ

**Q: Why does CI use `npm ci` instead of `npm install`?**
`npm install` can resolve dependencies slightly differently depending on the environment and timing, while `npm ci` strictly reproduces `package-lock.json`, making it much easier to guarantee the same dependency tree locally and in CI. That strictness is exactly why it refuses to tolerate any mismatch.

**Q: Is it fine to leave `package-lock.json` out of version control?**
Not recommended. `npm ci` assumes `package-lock.json` exists and is authoritative — removing it from version control defeats the reproducibility that `npm ci` is meant to provide.

**Q: I added just one dependency, but `npm install` produces a large, unrelated diff in the lock file. Is that normal?**
If other dependencies have loose version ranges, updates to npm's resolution algorithm or to the registry's metadata can shift unrelated packages too. Running `npm install <package>` for just the package you're adding, instead of a bare `npm install`, tends to keep the diff smaller.

## Related Articles

- [Managing Node.js Versions with nvm](/en/node-version-management-nvm)
- [Fixing the ERESOLVE Error During npm install](/en/npm-eresolve-error)
- [How to Clear the npm Cache](/en/npm-cache-clear)
- [Caching Node.js Dependencies in GitHub Actions](/en/github-actions-node-cache)
