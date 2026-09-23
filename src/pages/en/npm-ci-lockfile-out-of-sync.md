---
title: 'Fix: npm ci Fails With "package.json and package-lock.json ... in sync" Error (npm 10.9 / Node.js 22)'
date: '2026-09-23'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Running npm ci right after adding a dependency to package.json stops with an EUSAGE error saying the lock file is out of sync. Here is the cause and how to fix it by running npm install first.'
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## What I Was Trying to Do

I wanted to add a small dependency to a little Node.js test project. I edited `package.json` directly, adding one line under `dependencies`, and then ran `npm ci` to check that it would install the same way it would in CI.

```bash
npm ci
```

Before any package got installed, it stopped with a red error.

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
npm error
npm error Clean install a project
npm error
npm error Usage:
npm error npm ci
```

I normally only use `npm install`, so this error was unfamiliar. My first guesses were a corrupted lock file or an outdated npm version.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Git: 2.43.0
- Project: a minimal test project with just `package.json` and `package-lock.json` (one dependency, `left-pad@1.3.0`)

## What I Tried

First I suspected `package-lock.json` itself was corrupted, so I opened it in an editor and checked it. The JSON was valid — no parse errors.

Next I thought a stale npm cache might be the cause, so I cleared it and ran the command again.

```bash
npm cache clean --force
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

Same error, word for word. That's when I slowed down and actually read the message closely. The line `Missing: is-odd@3.0.1 from lock file` names the exact package I had just added to `package.json` by hand.

Checking the recent diff confirmed it: only `package.json` had changed, and `package-lock.json` had never been updated to match.

```bash
git diff --stat
```

```text
 package.json | 1 +
 1 file changed, 1 insertion(+)
```

## Root Cause

`npm install` reads `package.json` and, when needed, rewrites `package-lock.json` to match while resolving and installing dependencies. `npm ci`, by contrast, is a "clean install only" command: it installs strictly what's recorded in `package-lock.json` (or `npm-shrinkwrap.json`) and never modifies it. Editing `package.json` by hand to add a new dependency has no effect on the lock file at all. So a package that exists in `package.json` but not in `package-lock.json` — here, `is-odd` and its own dependency `is-number` — shows up as "Missing", the two files are judged out of sync, and the install is aborted before it starts.

This is deliberate, not a bug. `npm ci` exists specifically to reproduce the exact dependency tree recorded in the lock file, identically, in every environment and every CI run. Any mismatch between `package.json` and `package-lock.json`, however small, fails the command immediately rather than silently reconciling it the way `npm install` would.

## How I Fixed It

### 1. Confirm the lock file didn't change

```bash
git diff --stat package.json package-lock.json
```

```text
 package.json | 1 +
 1 file changed, 1 insertion(+)
```

No diff showed up for `package-lock.json`, confirming the update never happened.

### 2. Run npm install to update the lock file

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 490ms

found 0 vulnerabilities
```

This resolves `is-odd@3.0.1` (and its dependency `is-number@6.0.0`) from the entry I added to `package.json`, and writes the result into `package-lock.json`.

### 3. Confirm the lock file was actually updated

```bash
git diff --stat package.json package-lock.json
```

```text
 package-lock.json | 24 +++++++++++++++++++++---
 package.json      |  1 +
 2 files changed, 22 insertions(+), 3 deletions(-)
```

`package-lock.json` now shows a diff, where before it showed none.

### 4. Run npm ci again

```bash
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 663ms

found 0 vulnerabilities
```

It completed with no errors.

## Verify It Works

I checked that the newly added package and its dependency actually landed in `node_modules`.

```bash
npm ls
```

```text
npmci-test@1.0.0
├── is-odd@3.0.1
└── left-pad@1.3.0
```

As a final check, I removed `node_modules` entirely and ran `npm ci` once more to confirm it's reproducible now that the lock file and `package.json` are committed together.

```bash
rm -rf node_modules
npm ci
```

```text
added 3 packages, and audited 4 packages in 601ms

found 0 vulnerabilities
```

Same result after a clean install, confirming the lock file and `package.json` are properly in sync.

## Takeaways

- `npm ci` never touches `package-lock.json` — it installs exactly what's already recorded there. Hand-editing `package.json` and immediately running `npm ci` will surface any mismatch as an error right away.
- The error message's `Missing: <package> from lock file` line tells you exactly which package is missing — read that line first instead of guessing.
- The fix is just running `npm install` once to refresh `package-lock.json`, committing that diff alongside the `package.json` change, and then `npm ci` works again. In CI, this almost always means someone forgot to commit the updated lock file locally — the same steps apply there.

## FAQ

**Q: Why use `npm ci` instead of `npm install` at all?**
`npm ci` installs the exact versions recorded in `package-lock.json`, so the result is identical across every developer's machine and every CI run. It also deletes any existing `node_modules` before installing, unlike `npm install`.

**Q: Why does this only show up in CI and not locally?**
Most local workflows keep using `npm install`, which quietly updates the lock file whenever `package.json` changes, so the mismatch never becomes visible. It's only when a CI pipeline runs `npm ci` that an un-committed lock file update gets caught.

**Q: How can I avoid forgetting to commit the lock file diff?**
Make it a habit to run `npm install` and then check `git status` for a `package-lock.json` diff any time you touch `package.json`. A pre-commit hook that verifies both files changed together also catches this before it reaches CI.

## Related Articles

- [Fix ERESOLVE Errors When Running npm install](/en/npm-eresolve-error)
- [Clearing the npm Cache to Fix Install Issues](/en/npm-cache-clear)
- [Using package.json Scripts to Streamline Your Workflow](/en/npm-package-json-scripts)
- [Managing Node.js Versions with nvm](/en/node-version-management-nvm)
