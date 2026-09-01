---
title: 'Fix: npm ci Fails With "in sync" EUSAGE Error in CI'
date: '2026-09-01'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Right after adding a dependency by hand to package.json, npm ci fails with an EUSAGE error. Here is why the lock file falls out of sync and how npm install fixes it before CI runs.'
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## What I Was Trying to Do

I wanted to add `dayjs` to a small internal Node.js tool. In a hurry, instead of running `npm install dayjs`, I just typed the line straight into `package.json`'s `dependencies`.

```json
"dependencies": {
  "lodash": "^4.17.21",
  "dayjs": "^1.11.10"
}
```

Before committing, I tried to reproduce the exact command CI runs, `npm ci`, to sanity-check the change locally. It didn't install anything — it failed immediately.

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
npm error
npm error Clean install a project
```

I'd never seen this when adding dependencies through `npm install`, so my first guess was a JSON syntax mistake, and I spent a few minutes re-reading the file for a missing comma.

## Environment

- OS: Ubuntu 24.04 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Package in question: `dayjs@^1.11.10` (added to `package.json` by hand only)
- Lock file format: `lockfileVersion: 3`

## What I Tried

First I checked whether `package.json` was even valid JSON.

```bash
node -e "JSON.parse(require('fs').readFileSync('package.json', 'utf8'))"
```

It parsed without error, so the JSON itself was fine. Next I just ran `npm ci` again, hoping it was a fluke.

```text
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync.
```

Same result. That's when I actually read the second line of the error properly: `Missing: dayjs@1.11.23 from lock file`. I grepped the lock file directly to confirm.

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

`dayjs` was in `package.json` but had never made it into `package-lock.json` — a plain mismatch between the two files.

## Root Cause

Unlike `npm install`, `npm ci` never performs dependency resolution. It only trusts what's already recorded in `package-lock.json` (or `npm-shrinkwrap.json`) and rebuilds `node_modules` exactly from that. That's the whole point of the command — it guarantees CI reproduces the same dependency tree every time, rather than re-resolving version ranges like `^1.11.10` the way `npm install` does.

In my case, I had hand-edited `package.json` to require `dayjs` but never ran the command that updates `package-lock.json` to match. From `npm ci`'s point of view, `package.json` demanded a package that the lock file had no resolution recorded for — a contradiction it refuses to silently paper over. It's not that anything was broken; `npm ci` was doing exactly what it's designed to do: refuse an install it can't guarantee is reproducible.

## How I Fixed It

### 1. Confirm the lock file is actually out of date

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

Confirmed there was no `dayjs` entry at all in the lock file.

### 2. Run npm install to update the lock file

```bash
npm install
```

```text
added 1 package, and audited 3 packages in 755ms

1 high severity vulnerability

To address all issues, run:
  npm audit fix
```

`npm install` reads `package.json`, resolves the missing `dayjs` dependency, installs it into `node_modules`, and writes the resolution back into `package-lock.json`. The audit warning is an unrelated known-vulnerability notice, not something caused by this mismatch, so I ignored it for now.

### 3. Verify the lock file was actually updated

```bash
grep -A2 '"dayjs"' package-lock.json
```

```text
"dayjs": "^1.11.10",
"lodash": "^4.17.21"
}
```

Along with the `dependencies` entry, the resolved version `1.11.23` now had its own `node_modules/dayjs` record in the lock file.

### 4. Re-run npm ci to reproduce the exact CI step

```bash
npm ci
```

```text
added 2 packages, and audited 3 packages in 1s

1 high severity vulnerability

To address all issues, run:
  npm audit fix
```

`node_modules` rebuilt cleanly and `npm ci` exited successfully.

## Verify It Works

I confirmed the installed `dayjs` actually resolved to the version I expected.

```bash
node -e "console.log(require('./node_modules/dayjs/package.json').version)"
```

```text
1.11.23
```

`1.11.23` falls within the `^1.11.10` range I specified in `package.json`, and it matches what's recorded in `package-lock.json`. With the lock file in this state, `npm ci` in CI will reproduce the exact same install.

## Takeaways

- `npm ci` only trusts what's already written in `package-lock.json` — it never resolves version ranges from `package.json` on its own.
- Hand-editing `package.json` to add or change a dependency leaves `package-lock.json` stale, and `npm ci` fails with `EUSAGE`. The line `Missing: <package>@<version> from lock file` points straight at the mismatched package.
- Whenever a dependency changes — even by hand-editing `package.json` — run `npm install` once before committing so `package-lock.json` stays in sync. This kind of drift is easy to miss locally with `npm install`, since only `npm ci` (the command CI actually runs) enforces the mismatch.

## FAQ

**Q: What's the actual benefit of `npm ci` over `npm install`?**
`npm ci` rebuilds `node_modules` strictly from `package-lock.json`, so there's no resolution drift between runs, and it's faster than `npm install`. That makes it the right choice for CI pipelines and Docker builds, where reproducing the exact same dependency tree every time matters.

**Q: I'm not sure whether to trust package.json or package-lock.json anymore. What should I do?**
Deleting `package-lock.json` and `node_modules`, then running `npm install` again, re-resolves everything from `package.json`. Keep in mind this can shift transitive dependency versions, so run your test suite before committing the result.

**Q: Sometimes I see `Invalid` instead of `Missing` in the error. What's the difference?**
`Missing` means the lock file has no record of that package at all. `Invalid` means it does have a record, but the version doesn't satisfy what `package.json` requires. Either way, the fix is the same: run `npm install` to bring the lock file back in sync.

## Related Articles

- [Fix ERESOLVE Errors When Running npm install](/en/npm-eresolve-error)
- [How to Clear the npm Cache to Fix Install Issues](/en/npm-cache-clear)
- [Fix Permission Denied Errors During npm install](/en/npm-install-permission-denied)
- [Using package.json Scripts to Speed Up Your Workflow](/en/npm-package-json-scripts)
- [Managing Node.js Versions with nvm](/en/node-version-management-nvm)
