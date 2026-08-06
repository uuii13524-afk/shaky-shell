---
title: 'Fix: npm ci Fails with "in sync" EUSAGE Error'
date: '2026-08-06'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'After adding a dependency directly to package.json, npm ci fails with an EUSAGE error saying package.json and package-lock.json are out of sync. Here is the cause and how to fix it with npm install.'
en_tags: ['npm', 'Node.js', 'package-lock.json']
---

## What I Was Trying to Do

I wanted to add `dayjs` for date handling to a personal Node.js project, so I added one line directly to the `dependencies` field in `package.json`, planning to run the actual install afterward.

```json
{
  "name": "npmci-repro",
  "version": "1.0.0",
  "dependencies": {
    "left-pad": "^1.3.0",
    "chalk": "^5.3.0",
    "dayjs": "^1.11.10"
  }
}
```

Since I wanted to check that a clean install would behave the same way it does in CI, I ran `npm ci` instead of `npm install`.

```bash
npm ci
```

Instead of the usual `added` log line, it failed immediately.

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.21 from lock file
npm error
npm error Clean install a project
```

Exit code was `1`, and `node_modules` was never created.

```bash
echo $?
```

```text
1
```

## Environment

- OS: Linux (container environment, Ubuntu-based)
- Node.js: v22.22.2
- npm: 10.9.7
- `package-lock.json`: `lockfileVersion: 3`
- Dependency I was adding: `dayjs@^1.11.10` (not yet present in the existing `package-lock.json`)

## What I Tried

My first guess was that `node_modules` was in a bad state, so I removed it and ran `npm ci` again.

```bash
rm -rf node_modules
npm ci
```

Same result — the same `Missing: dayjs@1.11.21 from lock file` message. That ruled out `node_modules` as the cause; the problem had to be in `package-lock.json` itself.

I checked whether `package-lock.json` even mentioned `dayjs`:

```bash
grep -c "\"dayjs\"" package-lock.json
```

```text
0
```

`package.json` had `dayjs` added, but `package-lock.json` had nothing about it at all. As the error message itself hints, `npm ci` only reproduces the dependency tree already recorded in `package-lock.json` (or `npm-shrinkwrap.json`) — unlike `npm install`, it does not resolve dependencies from `package.json`. Editing `package.json` by hand doesn't update `package-lock.json` automatically, so calling `npm ci` while the two files disagree fails exactly like this.

## Root Cause

`npm ci` exists to install packages exactly as recorded in the lock file, with no dependency resolution step of its own. Before installing anything, it checks that every dependency listed in `package.json` is present in `package-lock.json` with no mismatch.

Here, I had added `dayjs` straight into `package.json`'s `dependencies` but never ran anything (like `npm install`) that would update `package-lock.json` to match. That left `dayjs` present in `package.json` but absent from `package-lock.json` — a state `npm ci` treats as "not in sync" and refuses to proceed from.

Editing `package.json` directly isn't wrong by itself, but skipping the step that updates `package-lock.json` afterward means `npm install` will quietly paper over it locally, while any pipeline using `npm ci` — CI runs, Docker builds — will hit this error every time.

## How I Fixed It

### 1. Update the lock file with npm install

To bring `package-lock.json` in line with the change I'd made to `package.json`, I ran `npm install`.

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 770ms

1 package is looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

### 2. Confirm dayjs was added to package-lock.json

```bash
grep -c "\"dayjs\"" package-lock.json
```

```text
2
```

With `lockfileVersion: 3`, each package name shows up in two places — the top-level dependency listing and the `packages` block — so a count of `2` confirms it was registered correctly.

### 3. Re-run npm ci

To confirm a CI-style clean install would now succeed, I removed `node_modules` again and re-ran `npm ci`.

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 669ms

1 package is looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

This time it completed cleanly with `added 3 packages` and no error.

## Verify It Works

I checked that `dayjs` was actually present in `node_modules` and confirmed its resolved version.

```bash
node -e "console.log(require('./node_modules/dayjs/package.json').version)"
```

```text
1.11.21
```

`1.11.21` falls within the `^1.11.10` range specified in `package.json`, confirming it resolved correctly. Exit code was `0` as well.

```bash
echo $?
```

```text
0
```

## Takeaways

- `npm ci` reproduces exactly what's recorded in `package-lock.json`; it does not resolve dependencies from `package.json`. Hand-editing `package.json` alone never updates the lock file.
- After adding or changing a dependency, run `npm install` once locally to refresh `package-lock.json` before committing. Think of `npm ci` as the verification step that confirms the lock file alone is enough to reproduce the install.
- The same `EUSAGE` + `Missing: <package>@<version> from lock file` pattern shows up most often in a Dockerfile's `RUN npm ci` step or in CI pipelines. A local `npm install` can look fine while a strict `npm ci` environment still fails, so any PR that touches `package.json` should also carry the matching `package-lock.json` diff.

## FAQ

**Q: Why doesn't `npm install` also fail here?**
`npm install` resolves dependencies from `package.json` and updates `package-lock.json` to match as part of that process — it treats a mismatch as something to fix, not an error. `npm ci` is deliberately stricter: it assumes the lock file is already correct and only replays it, so any drift from `package.json` is treated as a hard failure instead of being silently resolved.

**Q: Is it safe to just delete package-lock.json and regenerate it?**
It works, but it throws away every pinned version across the whole tree, not just the package you changed. That can quietly upgrade unrelated dependencies and make the diff much harder to review. Running `npm install` after a targeted `package.json` edit only touches what actually needs to change.

**Q: How do I catch this before it hits CI?**
Run `npm ci` locally (or in a pre-commit hook) whenever `package.json` changes, before pushing. If it fails locally, `package-lock.json` needs an `npm install` and a commit; if it passes locally, the same clean-install step in CI or a Docker build will pass too.

## Related Articles

- [How to Clear the npm Cache](/en/npm-cache-clear)
- [npm vs yarn: What's the Difference](/en/npm-vs-yarn)
- [Fixing npm ERESOLVE Errors](/en/npm-eresolve-error)
- [Using package.json Scripts](/en/npm-package-json-scripts)
- [Managing Node.js Versions with nvm](/en/node-version-management-nvm)
