---
title: 'Fix: npm ci Fails with "in sync" EUSAGE Error in GitHub Actions'
date: '2026-09-12'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm ci fails in GitHub Actions with an EUSAGE error because package.json and package-lock.json are out of sync. Here is the root cause and how to fix it by regenerating the lock file with npm install.'
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## What I Was Trying to Do

I was adding `dayjs`, a date formatting library, to a small personal tool. I hadn't run `npm install dayjs` locally yet — I just added one line directly to `dependencies` in `package.json` and committed it.

```json
{
  "name": "npmci-repro",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "lodash": "^4.17.21",
    "dayjs": "^1.11.10"
  }
}
```

After pushing, the GitHub Actions CI job failed at the dependency install step. The workflow uses `npm ci` instead of `npm install` for reproducibility.

```bash
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
npm error
npm error Clean install a project
```

Since `npm run build` worked fine locally, my first assumption was that something was specific to the CI environment, so I went after Node.js version differences and caching first.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Command: `npm ci` (both inside the GitHub Actions job and reproduced locally)
- package.json: `dayjs` added manually to `dependencies`; `package-lock.json` still from before that edit

## What I Tried

I first suspected the Node.js version in CI and pinned `actions/setup-node` to match my local `v22.22.2`, but the error message didn't change.

Next I assumed the npm cache in GitHub Actions was stale, so I changed the cache key and re-ran the job. Same `EUSAGE` error again.

Only then did I reproduce it locally by clearing `node_modules` and running `npm ci` directly.

```bash
rm -rf node_modules
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
```

This confirmed it wasn't a CI-only issue — it reproduced locally every time. Reading the error text carefully, it already stated the cause directly: `package.json` and `package-lock.json` were out of sync, and `dayjs@1.11.23` was missing from the lock file.

## Root Cause

Unlike `npm install`, `npm ci` trusts `package-lock.json` as the exact source of truth for what to install. It does not reconcile or auto-update the lock file if it disagrees with `package.json` — it just fails immediately with `EUSAGE` the moment a mismatch is detected.

In my case, I had added `dayjs` to `dependencies` by hand without ever running `npm install` (or `npm install dayjs`). So `package-lock.json` had no entry for `dayjs` at all, and `npm ci` refused to install because what was declared in `package.json` didn't match what was recorded in the lock file.

`npm install` automatically updates the lock file when it detects this kind of drift, which is likely why the problem never surfaced locally when I ran `npm run build` (assuming an `npm install` had run at some point). CI deliberately uses `npm ci` instead, precisely to guarantee reproducible installs — and that's exactly what exposed the drift.

## How I Fixed It

### 1. Check the current state of the lock file

```bash
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
```

The `Missing: dayjs@1.11.23 from lock file` line identified exactly which package was missing.

### 2. Regenerate the lock file with npm install

```bash
npm install
```

```text
added 2 packages, and audited 3 packages in 755ms

found 0 vulnerabilities
```

This adds `dayjs` and its dependencies into `package-lock.json`.

### 3. Verify the lock file actually changed

```bash
grep -c '"dayjs"' package-lock.json
```

```text
1
```

Confirmed that `dayjs` was now present in `package-lock.json`.

### 4. Commit the lock file together with package.json

```bash
git add package.json package-lock.json
git commit -m "add: dayjs dependency"
git push
```

The root cause was committing `package.json` without `package-lock.json`, so both files need to go into the same commit going forward.

### 5. Confirm npm ci no longer fails

```bash
rm -rf node_modules
npm ci
```

```text
added 2 packages, and audited 3 packages in 535ms

found 0 vulnerabilities
```

No `EUSAGE` error, and the install completed cleanly.

## Verify It Works

After pushing the fix, the GitHub Actions log showed the install step succeeding. I also re-ran `rm -rf node_modules && npm ci` locally to confirm the failure no longer reproduces.

## Takeaways

- `npm ci` requires `package.json` and `package-lock.json` to match exactly. It won't reconcile a mismatch for you — it fails fast with `EUSAGE` instead.
- Hand-editing a dependency into `package.json` without running `npm install` leaves the lock file stale and triggers this error. The `Missing: <package>@<version> from lock file` line in the error output tells you exactly what's missing.
- Always run `npm install` after adding or changing a dependency, and commit `package.json` and `package-lock.json` together. If CI uses `npm ci`, running `rm -rf node_modules && npm ci` locally before pushing catches this same failure before it reaches CI.

## FAQ

**Q: Why does npm ci exist at all if npm install already installs dependencies?**
`npm install` is designed to be flexible — it updates `package-lock.json` for you whenever it finds a discrepancy, and it can also modify `package.json` (for example when you add a new package). `npm ci` intentionally removes that flexibility: it deletes `node_modules` first, then installs strictly from `package-lock.json` without ever touching either file. That's what makes it a good fit for CI, where you want the exact same dependency tree every single run rather than whatever npm decides to resolve on the day.

**Q: Would this have been caught earlier if I'd run npm install locally after editing package.json?**
Yes. `npm install` would have updated `package-lock.json` to include `dayjs` in the same step where I added it, so the two files would never have drifted apart in the first place. The mistake here was treating a manual `package.json` edit as equivalent to actually installing the package.

## Related Articles

- [How to Fix npm ERESOLVE Dependency Tree Error](/en/npm-eresolve-error/)
- [How to Fix npm EACCES Permission Denied Error](/en/npm-install-permission-denied/)
- [How to Resolve Merge Conflicts After git pull](/en/git-pull-merge-conflict/)
- [Speed Up GitHub Actions Builds with Node.js npm Cache](/en/github-actions-node-cache/)
