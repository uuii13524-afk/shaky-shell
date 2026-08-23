---
title: 'Fix: npm ci Fails with EUSAGE "package.json and package-lock.json Are Not in Sync"'
date: '2026-08-23'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm install works fine but npm ci fails with an EUSAGE error. The cause was a dependency added by hand to package.json without running npm install afterward. Here is how to resync the lockfile and fix it.'
en_tags: ['Node.js', 'npm', 'npm ci', 'build error']
---

## What I Was Trying to Do

I have a small Node.js project where, to keep CI reproducible, local development uses `npm install` while the Docker build used in the CI pipeline uses `npm ci`. I wanted to start using `dayjs` for date handling, so I added an entry directly to `dependencies` in `package.json` and committed it as-is.

```json
{
  "dependencies": {
    "lodash": "^4.17.20",
    "dayjs": "^1.11.10"
  }
}
```

Locally I had run `npm install` right after editing, so everything worked without issue. But when I tried a clean install from scratch (no `node_modules`, no fresh lock history) using `npm ci`, the install itself failed.

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

My first assumption was that this was some transient difference in behavior between `npm ci` and `npm install` that would sort itself out, so I deleted `node_modules` and ran `npm ci` again. Same exact error.

## Environment

- OS: Ubuntu 24.04.4 LTS (kernel 6.18.x)
- Node.js: v22.22.2
- npm: 10.9.7
- package-lock.json: `lockfileVersion: 3`
- Dependency I was adding: `dayjs@^1.11.10`

## What I Tried

I first suspected a stale npm cache, so I cleared it and retried.

```bash
npm cache clean --force
npm ci
```

Same `EUSAGE` error, unchanged. That ruled out the cache as the cause.

Next I actually read the error message carefully instead of skimming it. It says "`npm ci` can only install packages when your package.json and package-lock.json ... are in sync", followed by a specific pointer: "Missing: dayjs@1.11.23 from lock file". That's when I realized I had edited `package.json` but never touched `package-lock.json` at all.

Searching the lockfile confirmed it — there wasn't a single `dayjs` entry in it.

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

The dependency existed only in `package.json`; `package-lock.json` had never picked it up.

## Root Cause

`npm install` reads `package.json` on every run and recalculates/updates `package-lock.json` as needed before installing. So even right after hand-editing `package.json`, running `npm install` papers over the inconsistency, which is exactly why this is easy to miss.

`npm ci`, on the other hand, treats `package-lock.json` (or `npm-shrinkwrap.json`) as the single source of truth and exists specifically to reproduce exactly what's recorded there. If `package.json` and `package-lock.json` disagree, it doesn't try to reconcile them — it fails immediately. In this case, I had added `dayjs` to `package.json`'s `dependencies` by hand-editing the file and committing directly, without ever going through `npm install`, so `package-lock.json` never picked up the change and the two files sat in the repo out of sync with each other.

The whole reason to use `npm ci` in CI or a Docker build is this strictness — it reproduces `node_modules` exactly from the lockfile regardless of local `node_modules` state or npm version differences. So when `package.json` looks correct but only `npm ci` fails, the first thing to suspect is a sync mismatch between `package.json` and `package-lock.json`.

## How I Fixed It

### 1. Confirm the package is missing from package-lock.json

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

Confirmed: present in `package.json`, absent from the lockfile.

### 2. Resync the lockfile with npm install

Instead of `npm ci`, deliberately run `npm install` to let npm recalculate `package-lock.json` against the current `package.json`.

```bash
npm install
```

```text
added 1 package, and audited 3 packages in 753ms

1 high severity vulnerability

To address all issues, run:
  npm audit fix
```

### 3. Verify package-lock.json picked up the change

```bash
grep -A2 '"dayjs"' package-lock.json
```

```text
    "dayjs": "^1.11.10",
    "lodash": "^4.17.20"
  }
```

I also confirmed the resolved entry under `node_modules/dayjs` now records `version: "1.11.23"`.

### 4. Re-run npm ci to confirm it now succeeds

```bash
npm ci
```

```text
added 2 packages, and audited 3 packages in 900ms

1 high severity vulnerability

To address all issues, run:
  npm audit fix
```

No `EUSAGE` error — the clean install completed normally.

## Verify It Works

I confirmed dependency resolution succeeds with `npm ci` alone, starting from a fully deleted `node_modules`, to reproduce the exact conditions the CI pipeline runs under.

```bash
rm -rf node_modules
npm ci
```

```text
added 2 packages, and audited 3 packages in 900ms
```

`node_modules` came back with no errors, and `npm ls dayjs lodash` confirmed both packages were installed at the expected versions.

## Takeaways

- `npm ci` treats `package-lock.json` as the single source of truth and fails immediately with `EUSAGE` the moment it disagrees with `package.json`, without attempting to reconcile the two.
- If you hand-edit `package.json` to add or change a dependency, always run `npm install` afterward so `package-lock.json` gets recalculated. Skipping that step and committing directly can make things look fine locally (since `npm install` papers over the mismatch) while `npm ci` in CI or a Docker build fails on the exact same commit.
- The "Missing: `<package>@<version>` from lock file" line in the error message points directly at which package is out of sync, which is the fastest way to diagnose this.

## FAQ

**Q: Do I need to run `npm install` every time I edit package.json?**
Only when you change dependencies (`dependencies`, `devDependencies`, etc.). Adding packages via `npm install <package>` updates `package.json` and `package-lock.json` together automatically, which avoids this kind of mismatch altogether — safer than hand-editing.

**Q: Why use `npm ci` instead of `npm install` in CI at all?**
`npm ci` reproduces exactly what's recorded in `package-lock.json`, guaranteeing the same resolved dependency tree on every run. Unlike `npm install`, which can be influenced by the local npm cache or resolution order, `npm ci` gives CI a deterministic `node_modules` from the same lockfile every time.

**Q: Should package-lock.json be committed to Git?**
Yes. The only reason I could spot the mismatch between `package.json` and `package-lock.json` in this case was that both were tracked in Git and visible as a diff. Gitignoring the lockfile removes any way to catch this kind of inconsistency in review.

## Related Articles

- [Fix ERESOLVE Errors When Running npm install](/en/npm-eresolve-error)
- [Fix EACCES Permission Errors When Running npm install](/en/npm-install-permission-denied)
- [Managing Node.js Versions with nvm (Windows/Mac)](/en/node-version-management-nvm)
- [Using package.json Scripts to Streamline Your Workflow](/en/npm-package-json-scripts)
