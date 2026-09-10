---
title: 'Fix: npm ci Fails With "Missing: … from lock file"'
date: '2026-09-10'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Running npm ci after manually adding a dependency to package.json fails with "Missing: is-odd@3.0.1 from lock file" in CI. Here is why npm ci enforces a synced lockfile and how to fix it with npm install.'
en_tags: ['Node.js', 'npm', 'npm ci']
---

## What I Was Trying to Do

I needed to quickly add an odd-number check to a small Node.js utility script. The project only depended on `left-pad` at the time, and I knew `is-odd` would do the job. Instead of running `npm install is-odd`, I took a shortcut and added the line directly to `package.json` myself.

```json
{
  "dependencies": {
    "left-pad": "^1.3.0",
    "is-odd": "^3.0.1"
  }
}
```

I assumed `require('is-odd')` would just work locally, so I committed and pushed. The CI build step, which runs `npm ci`, failed with an error I hadn't seen before.

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
```

`npm run build` had worked fine locally, so my first instinct was to suspect something broken in the CI environment itself.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Command that failed: `npm ci` (used in CI/Docker builds, not `npm install`)
- Change made: added `is-odd` to `dependencies` in `package.json` by hand (`package-lock.json` was never updated)

## What I Tried

First I checked whether I could reproduce the same failure locally. Since I had only ever run `npm install` on this machine, I tried `npm ci` directly.

```bash
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
```

The exact same `EUSAGE` error reproduced locally. That ruled out my "broken CI environment" theory right away.

Next, I searched `package-lock.json` for `is-odd`.

```bash
grep -c '"is-odd"' package-lock.json
```

```text
0
```

`package.json` listed `is-odd`, but `package-lock.json` had no trace of it at all. That's when it clicked: editing `package.json` by hand doesn't touch `package-lock.json`, and I had never run `npm install` after making the change.

## Root Cause

Unlike `npm install`, `npm ci` never performs dependency resolution. It only reads `package-lock.json` (or `npm-shrinkwrap.json`, if present) and reproduces exactly what's recorded there into `node_modules`. In exchange, it strictly verifies that `package.json` and `package-lock.json` agree with each other — a single mismatch is enough to make it fail immediately with `EUSAGE`, without attempting to resolve anything.

In my case, I had added `is-odd@^3.0.1` to `dependencies` by hand but never ran the `npm install` that would actually resolve and download it. As a result, `package-lock.json` had no entry for `is-odd`, nor for its own dependency `is-number`. The lines `Missing: is-odd@3.0.1 from lock file` and `Missing: is-number@6.0.0 from lock file` were literally telling me those packages didn't exist in the lock file.

`npm install` automatically updates the lock file whenever `package.json` changes, but `npm ci` deliberately skips that step by design — it's meant to guarantee reproducible installs in CI/CD and Docker builds. This wasn't a bug; it was `npm ci` working exactly as intended.

## How I Fixed It

### 1. Confirm the mismatch in package-lock.json

```bash
grep -c '"is-odd"' package-lock.json
```

```text
0
```

Confirmed there was no `is-odd` entry, pinning down the out-of-sync lock file as the cause.

### 2. Re-sync the lock file with npm install

```bash
npm install
```

```text
added 2 packages, and audited 4 packages in 358ms

found 0 vulnerabilities
```

Running `npm install` resolved `is-odd` and its dependency `is-number`, and wrote both into `package-lock.json`.

### 3. Confirm package-lock.json was updated

```bash
grep -c '"is-odd"' package-lock.json
```

```text
1
```

The count went from `0` to `1`, confirming `is-odd` was now recorded in `package-lock.json`.

### 4. Confirm npm ci now succeeds

```bash
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 354ms

found 0 vulnerabilities
```

`npm ci` completed without error. The deprecation warning for `left-pad` was already present before this issue and isn't related to the failure — safe to ignore.

## Verify It Works

I checked that `node_modules` contained exactly what was expected.

```bash
ls node_modules | grep -E "left-pad|is-odd|is-number"
```

```text
is-number
is-odd
left-pad
```

Both `is-odd` and its dependency `is-number` were installed correctly. I committed the updated `package.json` together with `package-lock.json`, pushed, and confirmed the CI `npm ci` step passed cleanly.

## Takeaways

- `npm ci` never resolves dependencies — it just reproduces whatever `package-lock.json` already records. Any mismatch with `package.json` triggers an immediate `EUSAGE` failure.
- Hand-editing `package.json` does not update `package-lock.json`. Whenever you add or change a dependency, run `npm install` so the lock file stays in sync.
- The `Missing: <package>@<version> from lock file` message means exactly that — the package isn't recorded in the lock file. When you see this pattern, `grep` the package name in both `package.json` and `package-lock.json` first; it's the fastest way to confirm the mismatch.

## FAQ

**Q: Would this have been avoided by using `npm install <package>` instead of editing package.json directly?**
Yes. `npm install <package>` updates both `package.json` and `package-lock.json` in the same step, so this kind of mismatch can't happen. In my case, the root cause was simply typing the dependency into the editor by hand because I was in a hurry.

**Q: Should CI always use npm ci instead of npm install?**
Yes. `npm ci` reproduces `package-lock.json` exactly, so local and CI environments end up with identical dependency versions, which makes builds far more reproducible. Catching a lock file mismatch early, like in this case, is one of the benefits of using `npm ci` in CI.

**Q: Would removing package-lock.json from version control avoid this kind of error entirely?**
It would, but at the cost of reproducibility — different environments could end up installing different dependency versions, which is a worse problem. The recommended approach is to keep `package-lock.json` under version control and always run `npm install` after changing dependencies.

## Related Articles

- [Fix: npm ERESOLVE Error When Installing Dependencies](/en/npm-eresolve-error)
- [Fix: npm install Fails With Permission Denied](/en/npm-install-permission-denied)
- [How to Clear the npm Cache (npm cache clean)](/en/npm-cache-clear)
- [npm vs yarn: Key Differences and When to Use Each](/en/npm-vs-yarn)
- [How to Cache Node.js Dependencies in GitHub Actions](/en/github-actions-node-cache)
