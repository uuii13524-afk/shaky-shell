---
title: 'Fix: npm ci Fails With "package.json and package-lock.json...are in sync" (EUSAGE)'
date: '2026-09-17'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm ci fails in CI with an EUSAGE error saying package.json and package-lock.json are not in sync. Here is why it happens after adding a dependency and how to fix it with npm install.'
en_tags: ['Node.js', 'npm', 'CI/CD error']
---

## What I Was Trying to Do

I added a new dependency (`is-odd`) to a project by editing `package.json` directly, without running an install command right away:

```json
{
  "name": "npmci-test",
  "version": "1.0.0",
  "dependencies": {
    "left-pad": "1.3.0",
    "is-odd": "3.0.1"
  }
}
```

Right after editing `package.json`, `package-lock.json` was still the old version, from before `is-odd` was added. To check that this would behave the same way it does in CI, I ran `npm ci`, and it failed immediately:

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
npm error
npm error Clean install a project
```

If a GitHub Actions workflow step is `npm ci` and you push a commit that only touches `package.json` without ever running `npm install` locally, CI hits the exact same error.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Command: `npm ci` (the clean-install command CI pipelines typically use, as opposed to `npm install`)

## What I Tried

My first instinct was that `package-lock.json` might be corrupted, so I considered deleting both `node_modules` and `package-lock.json` and starting over. Before doing that, I wanted to narrow down the actual cause, so I re-ran `npm ci` and read the error output more carefully.

```bash
npm ci
```

The line `Missing: is-odd@3.0.1 from lock file` was the key detail — npm was explicitly saying a package referenced in `package.json` was missing from the lock file. That's when I remembered I had only edited `package.json` and never run `npm install` afterward.

To confirm, I grepped the lock file directly:

```bash
grep -c "is-odd" package-lock.json
```

```text
0
```

`is-odd` was indeed nowhere in `package-lock.json`. `package.json` and `package-lock.json` had drifted apart — exactly the "not in sync" state the error message described.

## Root Cause

Unlike `npm install`, `npm ci` never resolves dependencies on its own. It trusts `package-lock.json` completely and rebuilds `node_modules` strictly according to what the lock file already records. So if you add a dependency to `package.json` and run `npm ci` before ever running `npm install`, npm sees a mismatch between what `package.json` requests and what the lock file has recorded, and refuses to proceed.

This is deliberate behavior, not a bug. `npm ci` skips dependency resolution specifically to give fast, reproducible installs, and that guarantee only holds when `package.json` and `package-lock.json` are fully in sync. In my case, editing `package.json` by hand without ever running `npm install` left the lock file stale, breaking that precondition.

When this shows up in CI, it's almost always one of two situations:

1. Someone edited `package.json` locally and committed/pushed without running `npm install` first.
2. On a team project, someone added a dependency and pushed `package.json`, but forgot to push the updated `package-lock.json` (or a merge only kept one of the two files).

## How I Fixed It

### 1. Reproduce and read the error

```bash
npm ci
```

```text
npm error code EUSAGE
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
```

The error message itself tells you the fix: update the lock file with `npm install`.

### 2. Update the lock file with `npm install`

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 315ms

found 0 vulnerabilities
```

`npm install` reads `package.json`, resolves dependencies again, and updates `package-lock.json` with the newly added `is-odd` and its own dependency, `is-number`.

### 3. Confirm the lock file was updated

```bash
grep -A2 '"is-odd"' package-lock.json
```

```text
        "is-odd": "3.0.1",
        "left-pad": "1.3.0"
      }
```

The `is-odd` entry now exists in `package-lock.json`.

### 4. Commit the updated lock file together with package.json

```bash
git add package.json package-lock.json
git commit -m "chore: add is-odd dependency"
```

Always commit `package.json` and `package-lock.json` together. Pushing only one of the two is exactly what sends CI back into the same `EUSAGE` error.

### 5. Confirm `npm ci` now passes

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 316ms

found 0 vulnerabilities
```

I removed `node_modules` entirely and re-ran `npm ci` to confirm a clean install now completes without errors.

## Verifying the Fix

I also checked the exit code to confirm this would pass as a CI step:

```bash
npm ci; echo "exit: $?"
```

```text
added 3 packages, and audited 4 packages in 316ms
found 0 vulnerabilities
exit: 0
```

`exit: 0` confirms the `npm ci` step would now succeed the same way in a GitHub Actions workflow.

## Summary

- `npm ci` never resolves dependencies — it strictly replays what `package-lock.json` already records. Any mismatch between `package.json` and `package-lock.json` causes an immediate `EUSAGE` failure.
- The cause is almost always editing `package.json` and committing without running `npm install` first. The `Missing: <package> from lock file` line tells you exactly which dependency triggered it.
- Fix it by running `npm install` to refresh the lock file, then commit `package.json` and `package-lock.json` together. Keep using `npm ci` in CI — the fix belongs in your local workflow, not in swapping CI to `npm install`.

## FAQ

**Q: Could I just use `npm install` in CI instead to avoid this error entirely?**
You could, but `npm install` re-resolves dependencies every run, which is slower and can produce slightly different results locally versus in CI. Rather than removing the safety net, it's better to keep `npm ci` and make sure the lock file is always updated and committed correctly.

**Q: Is it fine to gitignore `package-lock.json` and not commit it?**
No — `npm ci` requires `package-lock.json` to exist at all (it fails with a different error if it's missing). Lock files should always be committed, even for libraries, not excluded via `.gitignore`.

**Q: What if `package-lock.json` gets a merge conflict when pulling changes from teammates?**
Don't try to hand-resolve the conflict markers inside the lock file. Delete `package-lock.json` and run `npm install` again to regenerate it, then check that the resulting diff only reflects the dependency changes you expect before committing.

## Related Articles

- [Fix: npm ERESOLVE Error When Installing Packages](/en/npm-eresolve-error)
- [Speed Up CI with npm Caching in GitHub Actions](/en/github-actions-node-cache)
- [Building a Node.js App with Dockerfile: Basics and Layer Caching](/en/docker-dockerfile-basics)
- [How to Clear the npm Cache and Troubleshoot Install Issues](/en/npm-cache-clear)
