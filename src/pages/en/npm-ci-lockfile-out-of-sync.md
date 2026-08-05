---
title: 'Fix "npm ci" EUSAGE Error: package.json and package-lock.json Out of Sync'
date: '2026-08-05'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm ci fails with an EUSAGE error saying package.json and package-lock.json are out of sync. Here is why npm install hides the problem, and how to fix the lock file so npm ci works again.'
en_tags: ['Node.js', 'npm', 'npm ci']
---

## What I Was Trying to Do

I wanted to reproduce the exact install step used in our Dockerfile, so instead of `npm install` I ran `npm ci` locally for a clean install.

```bash
rm -rf node_modules
npm ci
```

It stopped partway through with this error:

```text
npm ERR! code EUSAGE
npm ERR!
npm ERR! `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm ERR!
npm ERR! Invalid: lock file's date-fns@2.30.0 does not satisfy date-fns@3.6.0
npm ERR!
npm ERR! Missing: zod@3.23.8 from lock file
```

`npm install` had always worked fine on this same project, so seeing `npm ci` fail was confusing at first.

## Environment

- OS: Ubuntu 22.04 (WSL2)
- Node.js: v20.11.1
- npm: 10.2.4
- Project: a Next.js app with `package-lock.json` committed to git

## What I Tried

First I ran `npm install` again just to confirm it still worked.

```bash
npm install
```

It completed with no errors and `node_modules` was created normally, so dependency resolution itself wasn't broken. Next I compared the relevant entries in `package.json` and `package-lock.json`.

```bash
grep -A2 '"date-fns"' package.json
grep -A2 '"date-fns"' package-lock.json | head -5
```

`package.json` specified `"date-fns": "^3.6.0"`, but the `packages` section in `package-lock.json` still listed `date-fns` at `2.30.0`. `zod` had been added to `dependencies` in `package.json`, but there was no entry for it in `package-lock.json` at all.

I checked recent commit history for both files.

```bash
git log --oneline -- package.json package-lock.json | head -5
```

The most recent commit had edited `package.json` by hand — bumping `date-fns` from `^2.x` to `^3.x` and adding `zod` — without running `npm install` afterward, so `package-lock.json` was committed unchanged.

## Root Cause

`npm install` tolerates a mismatch between `package.json` and `package-lock.json`: it re-resolves dependencies on the spot and updates both files. `npm ci`, by design, trusts `package-lock.json` as the single source of truth and installs exactly what's written there — if it doesn't match `package.json`, it refuses to proceed and errors out instead of silently resolving anything.

In this case, `package.json` had been hand-edited to change a version range and add a new dependency, but the follow-up `npm install` step that would have kept `package-lock.json` in sync was skipped before committing. Since local development only ever used `npm install`, the drift went unnoticed until `npm ci` was run for the first time.

This is exactly the trade-off `npm ci` is designed around. `npm install` is meant for day-to-day development, where you expect the dependency tree to shift as you add or bump packages. `npm ci` is meant for reproducible installs — CI pipelines, Docker builds, anything where you want the exact tree that was tested and committed, not whatever the resolver decides today. That strictness is the whole point of the command, but it also means any manual edit to `package.json` that isn't followed by a lock file update becomes a hard failure the moment `npm ci` runs, instead of a silent version drift.

## The Fix

Regenerate `package-lock.json` from the current `package.json`.

```bash
npm install
```

This updates `package-lock.json` to match the dependencies declared in `package.json`. Check the diff.

```bash
git diff package-lock.json | head -30
```

`date-fns` was bumped to the `3.6.0` line and a new entry for `zod` was added, as expected. Commit the updated lock file.

```bash
git add package-lock.json
git commit -m "fix: update package-lock.json to match package.json"
```

Then confirm `npm ci` passes.

```bash
rm -rf node_modules
npm ci
```

## Verifying the Fix

```bash
npm ci
```

```text
added 412 packages, and audited 413 packages in 8s

52 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

The install completed with no errors. I also checked the installed versions directly.

```bash
npm ls date-fns zod
```

```text
myapp@1.0.0 /home/dev/myapp
├── date-fns@3.6.0
└── zod@3.23.8
```

Both matched what `package.json` specified.

## Things I Got Wrong Along the Way

- After hand-editing `package.json`, even a single version bump needs a follow-up `npm install` to keep `package-lock.json` in sync. I assumed a small manual edit was harmless — it wasn't.
- Because local development only ever used `npm install`, the drift stayed invisible until I ran `npm ci` in a Docker-style clean-install context. Without that step, the mismatch could have shipped straight to CI.
- The `Invalid: lock file's ... does not satisfy ...` line in the error already names the exact package and version at fault. Before reaching for `rm package-lock.json` and starting over, it's worth reading that line first to scope the actual diff.

## FAQ

**Q: Does deleting `package-lock.json` and running `npm install` fix it too?**
Yes, but it can also bump unrelated dependencies to newer versions you didn't intend to change. Try a plain `npm install` first so only the packages that actually drifted get updated.

**Q: How do I catch this before it reaches CI?**
Run `npm ci` (not `npm install`) in your pull request CI job. If CI only ever runs `npm install`, this kind of drift slips through unnoticed.

**Q: Does the same fix apply to `npm-shrinkwrap.json`?**
Yes — `npm-shrinkwrap.json` has to stay in sync with `package.json` the same way `package-lock.json` does, so running `npm install` after a manual edit resolves it the same way.

**Q: Is it safe to just edit `package.json` by hand at all?**
It's fine for small changes as long as you treat `npm install` as a mandatory follow-up step, not an optional one. The safer habit is to let npm write both files for you — `npm install <package>@<version>` or `npm uninstall <package>` — since those commands update `package.json` and `package-lock.json` together in one step, removing the chance of forgetting the second half.

## Related Posts

- [Fix npm ERR! ERESOLVE Dependency Resolution Errors](/en/npm-eresolve-error)
- [How to Clear the npm Cache](/en/npm-cache-clear)
- [Fix npm install Permission Denied Errors](/en/npm-install-permission-denied)
- [npm vs yarn: Key Differences](/en/npm-vs-yarn)
- [Caching npm Dependencies in GitHub Actions](/en/github-actions-node-cache)
