---
title: 'How to Fix npm ERESOLVE Dependency Tree Error'
date: '2026-07-17'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Adding testing-library/react@14 to a React 17 app threw ERESOLVE unable to resolve dependency tree - its peer wants react@18. Downgrading to v13 fixed it.'
ja_tags: ['Node.js', 'npm', 'ERESOLVE', '依存関係']
en_tags: ['Node.js', 'npm', 'ERESOLVE', 'dependency']
---

## What I Was Trying to Do

I was working on a Next.js project pinned to React 17 and wanted to add proper testing, so I ran `npm install --save-dev @testing-library/react` to pull in the latest version. Instead of the usual install log, the terminal filled up with a wall of red text and the install just stopped.

```text
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
npm ERR!
npm ERR! While resolving: my-app@0.1.0
npm ERR! Found: react@17.0.2
npm ERR! node_modules/react
npm ERR!   react@"^17.0.2" from the root project
npm ERR!
npm ERR! Could not resolve dependency:
npm ERR! peer react@"^18.0.0" from @testing-library/react@14.0.0
npm ERR! node_modules/@testing-library/react
npm ERR!   dev @testing-library/react@"^14.0.0" from the root project
npm ERR!
npm ERR! Fix the upstream dependency conflict, or retry
npm ERR! this command with --force or --legacy-peer-deps
npm ERR! to accept an incorrect (and potentially broken) dependency resolution.
npm ERR!
npm ERR! See /home/user/.npm/eresolve-report.txt for a full report.
```

No `node_modules` got created, and `package-lock.json` was untouched. I'd run `npm install` hundreds of times before without seeing anything like this, and had no idea what was actually wrong.

## Environment

- OS: Ubuntu 22.04 LTS
- Node.js: v20.11.0
- npm: 10.2.4
- React: 17.0.2
- @testing-library/react: 14.0.0 (the version I was trying to install)

## What I Tried

At first I didn't understand what `npm ERR! See /home/user/.npm/eresolve-report.txt for a full report.` meant at the bottom of the error, so I just reran `npm install` as-is.

```text
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

Same exact error came back. That ruled out a flaky network issue — the problem was something structural in the dependency tree itself, not a one-off fetch failure.

Next I assumed the local cache might be corrupted, so I cleared it and tried again.

```bash
npm cache clean --force
npm install --save-dev @testing-library/react
```

Clearing the cache succeeded on its own, but the install still failed with the same `ERESOLVE unable to resolve dependency tree` message. That confirmed it wasn't a caching problem — it was a genuine version mismatch between packages declared in `package.json`.

## Why This Happens

Since npm 7, npm strictly enforces the version ranges a package declares in its `peerDependencies` field when resolving the dependency tree. In this case, the project's `react` was pinned to `17.0.2`, while `@testing-library/react@14` declares `peerDependencies` requiring `react@^18.0.0`.

npm can't simultaneously satisfy "the root project wants React 17" and "the package I'm installing wants React 18," so it aborts building the dependency tree instead of guessing. Before npm 7, a peer dependency mismatch like this only produced a warning and the install proceeded anyway — which is exactly why longtime npm users get caught off guard the first time they hit ERESOLVE.

## Solution

### 1. Align versions at the source

```bash
npm install --save-dev @testing-library/react@13
```

```text
added 1 package, and audited 842 packages in 4s
found 0 vulnerabilities
```

`@testing-library/react@13` declares `peerDependencies` of `react@^16.8.0 || ^17.0.0 || ^18.0.0`, which doesn't conflict with the project's React 17. Checking the offending package's changelog or release notes and stepping down to a version compatible with your current major version is the safest fix.

### 2. Fall back to --legacy-peer-deps when versions can't be aligned

```bash
npm install --save-dev @testing-library/react --legacy-peer-deps
```

```text
npm warn ERESOLVE overriding peer dependency
npm warn Found: react@17.0.2
npm warn Could not resolve dependency:
npm warn peer react@"^18.0.0" from @testing-library/react@14.0.0
added 7 packages, and audited 849 packages in 6s
```

`--legacy-peer-deps` restores npm 6's behavior: peer dependency mismatches drop to a warning instead of blocking the install. This usually doesn't break the build or test run itself, but it carries a real risk of a runtime error if the mismatched package ends up calling a React API that only exists in the newer major version. Treat this as a stopgap and prefer solution 1 whenever you can.

### 3. Confirm the resolved tree afterward

```bash
npm ls react
```

```text
my-app@0.1.0
├── react@17.0.2
└─┬ @testing-library/react@13.4.0
  └── react@17.0.2 deduped
```

`npm ls react` shows whether `react` has settled on a single version across the whole tree. If you still see multiple versions listed, you'll need the deeper `npm ls` inspection covered in the FAQ below.

## Gotchas

- I skipped past the two blocks in the error output — `While resolving` and `Could not resolve dependency` — and lost about thirty minutes not realizing which packages were actually in conflict. The first block tells you what npm is currently trying to install; the second tells you what's blocking it.
- I mixed up `--force` and `--legacy-peer-deps`. `--force` forcibly refetches and rebuilds everything, including cached packages unrelated to the conflict, while `--legacy-peer-deps` only relaxes the peer dependency check. I reached for `--force` first and ended up reinstalling a bunch of unrelated packages for nothing.
- I tried hand-editing `package-lock.json` to just change the version number directly, which produced a different error on the next install: `npm ERR! Invalid: lock file's react@18.2.0 does not satisfy react@17.0.2`. Never hand-edit the lockfile — always go through an npm command.
- Our GitHub Actions CI uses `npm ci`, so even after I'd resolved the install locally with `--legacy-peer-deps`, the exact same ERESOLVE error showed up again in CI. `npm ci` reads settings from `.npmrc`, so I had to add `legacy-peer-deps=true` there to keep CI and local behavior consistent.

## FAQ

**Q: Should I use `npm install --force` or `--legacy-peer-deps` to fix an ERESOLVE error?**
Try `--legacy-peer-deps` first — it only loosens the peer dependency check, so the blast radius is small. `--force` forcibly overwrites cached and existing packages too, which is far more likely to cause unrelated side effects. Only reach for `--force` if `--legacy-peer-deps` alone doesn't resolve it.

**Q: I don't want to type an option every time. Can I make this the default?**
Create a `.npmrc` file in the project root with a single line, and every future `npm install` in that project will behave the same way without any flags.

```text
# .npmrc
legacy-peer-deps=true
```

**Q: The error message doesn't make it obvious which packages are actually conflicting.**
Run `npm ls <package-name>` to see a tree view of everywhere that package is required from, and at what version.

```bash
npm ls react
```

## Related Articles

- [How to Clear the npm Cache to Fix Install Problems](/en/npm-cache-clear)
- [npm vs yarn: Command Differences and When to Use Each](/en/npm-vs-yarn)
- [Getting More Out of package.json Scripts](/en/npm-package-json-scripts)
- [Managing Node.js Versions with nvm](/en/node-version-management-nvm)
- [Fixing npm Command Not Recognized on Windows](/en/windows-npm-not-working)
