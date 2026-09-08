---
title: 'Fix npm ci "lock file does not satisfy" EUSAGE Error (2026, Node.js 22)'
date: '2026-09-08'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm ci fails with an EUSAGE error reading "Invalid: lock file''s ... does not satisfy ...", blocking clean installs and CI. Here is why the version in package.json and package-lock.json drift apart, and how to resync them safely.'
en_tags: ['Node.js', 'npm', 'package-lock.json']
---

## What I Was Trying to Do

After hand-editing a dependency's version range in `package.json`, I ran `npm ci` to rebuild `node_modules` from scratch, expecting a clean install.

```bash
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Invalid: lock file's left-pad@1.3.0 does not satisfy left-pad@1.1.0
npm error
npm error Clean install a project
npm error
npm error A complete log of this run can be found in: /root/.npm/_logs/2026-09-08T00_09_57_762Z-debug-0.log
```

I was using `npm ci` instead of `npm install` specifically to mirror what CI does — a strict, lockfile-driven install. Instead, it failed immediately, right after I'd edited `package.json`.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Package involved: `left-pad` (version range in `package.json` hand-edited from `^2.0.0` to `1.1.0`; `package-lock.json` left untouched)

## What I Tried

My first assumption was that since I'd only changed a version *range*, not the actual dependency set, `npm ci` would still handle it fine. Here's what `package.json` looked like right after the edit:

```json
{
  "name": "npm-ci-test",
  "version": "1.0.0",
  "dependencies": {
    "left-pad": "1.1.0"
  }
}
```

Running `npm ci` against this failed immediately with the `EUSAGE` error above. The message itself said to run `npm install` to update the lock file first, so I re-ran `npm ci` once more just to confirm it wasn't a fluke — it wasn't; same error every time.

I also considered hand-editing `package-lock.json` directly, changing the `left-pad` version field to `1.1.0`. But `package-lock.json` doesn't just store a version number — it also carries `resolved` (the tarball URL) and `integrity` (a content hash). Getting all three consistent by hand isn't realistic, and a partial edit would just trade this error for an integrity-mismatch failure instead.

## Why This Happens

Unlike `npm install`, `npm ci` never re-resolves the dependency tree. `package-lock.json` is treated as the single source of truth, and `npm ci` simply unpacks exactly what's recorded there into `node_modules`. This is a deliberate design choice: it guarantees the same dependency tree gets installed everywhere, preventing the classic "works on my machine, breaks in CI" class of bug caused by npm resolving slightly different versions in different environments.

Because of that, `npm ci` runs a consistency check before touching anything. It compares each dependency's version range in `package.json` (here, an exact pin of `1.1.0` for `left-pad`) against the version actually recorded as resolved in `package-lock.json` (here, `1.3.0`). If the locked version doesn't satisfy the new range, it stops with `Invalid: lock file's <pkg>@<locked version> does not satisfy <pkg>@<range in package.json>` and an `EUSAGE` exit code.

In my case, `package-lock.json` still held `left-pad@1.3.0` — a leftover from an earlier `^2.0.0` range that, since no `2.x` release of `left-pad` exists, had actually resolved against `1.3.0` (the version an earlier `^1.3.0` range had locked). That locked `1.3.0` doesn't satisfy the new exact pin of `1.1.0`. Nothing was broken; I had simply edited `package.json` and forgotten to regenerate the lock file to match.

## Solution

### 1. Update the lock file

As the error message says, run `npm install` to regenerate `package-lock.json` from the current `package.json`.

```bash
npm install
```

```text
npm warn deprecated left-pad@1.1.0: use String.prototype.padStart()

added 1 package, and audited 2 packages in 584ms

found 0 vulnerabilities
```

### 2. Confirm the lock file actually changed

```bash
grep -A3 '"node_modules/left-pad"' package-lock.json
```

```text
    "node_modules/left-pad": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/left-pad/-/left-pad-1.1.0.tgz",
      "integrity": "sha512-C8cw/7VpfXLj8Yjlmux8lqb3mfIe3vEXTdik/cXTuzZ8FXJnu45UAWp94XlWWmcW7Yxl74wvHw8w10wIHNGHRQ==",
```

`version`, `resolved`, and `integrity` all update together to match the new pin — the whole point of this step is that you never hand-edit these fields yourself.

### 3. Commit the updated lock file alongside package.json

```bash
git add package.json package-lock.json
git commit -m "chore: pin left-pad to 1.1.0 and sync lockfile"
```

If you commit `package.json` without also committing the regenerated `package-lock.json`, CI hits the exact same `EUSAGE` error again.

## Verify It Works

With the lock file back in sync, `npm ci` completes cleanly.

```bash
npm ci
```

```text
npm warn deprecated left-pad@1.1.0: use String.prototype.padStart()

added 1 package, and audited 2 packages in 466ms

found 0 vulnerabilities
```

No more `EUSAGE` error, and the dependency installs at exactly the version now pinned in `package.json`.

## Gotchas

- `npm ci` never touches the network to re-resolve anything — it only compares the range in `package.json` against what's already recorded in `package-lock.json`. Any manual edit to `package.json` needs a follow-up `npm install` to keep the lock file honest.
- Hand-editing `package-lock.json` is a trap. Even if you get the `version` field right, a mismatched `integrity` hash just trades this failure for a content-verification failure instead.
- A bare CI log usually just says "dependency install failed," which isn't very actionable on its own. The real detail is on the line reading `Invalid: lock file's <pkg>@<locked version> does not satisfy <pkg>@<range in package.json>` — it names the exact package and both versions involved, and reading it is the fastest way to diagnose this.

## FAQ

**Q: Can I just always use `npm install` instead of `npm ci` to avoid this error entirely?**
You can, but that doesn't fix the underlying issue — it works around it. `npm install` re-resolves dependencies each time, which can produce slightly different versions across machines. For reproducible CI and deploy builds, keep using `npm ci`, and when it errors, resync the lock file with the steps above rather than switching commands.

**Q: What if I just remove package-lock.json from the repo entirely?**
Don't. The lock file exists specifically so every teammate and every CI run installs the same dependency versions. Removing it trades this error for the far less debuggable "works on my machine" class of problem.

**Q: Does this only happen when I hand-edit package.json?**
No. It also shows up when you pull someone else's `package.json` change without also pulling their updated `package-lock.json`, or when a merge resolves a conflict in `package-lock.json` incorrectly. The root cause is always the same — `package.json` and `package-lock.json` disagree — and the fix is always the same `npm install` resync.

## Related Articles

- [How to Fix npm ERESOLVE Dependency Tree Error](/en/npm-eresolve-error)
- [How to Clear npm Cache and Fix Install Issues](/en/npm-cache-clear)
- [How to Fix npm EACCES Permission Denied Error](/en/npm-install-permission-denied)
- [Manage Node.js Versions with nvm (Windows and Mac)](/en/node-version-management-nvm)
- [Speed Up GitHub Actions Builds with Node.js npm Cache](/en/github-actions-node-cache)
