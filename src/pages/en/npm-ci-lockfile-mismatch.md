---
title: 'Fix: npm ci Fails With "package.json and package-lock.json ... are in sync"'
date: '2026-09-03'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm install works fine locally, but npm ci fails in CI with an EUSAGE error. Here is why package-lock.json falls out of sync with package.json, and how npm install fixes it.'
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## What I Was Trying to Do

I needed to add the `is-odd` package to a small Node.js test project. In a hurry, instead of running `npm install is-odd`, I added a line directly into the `dependencies` field of `package.json` and committed it.

```json
{
  "dependencies": {
    "left-pad": "^1.3.0",
    "is-odd": "^3.0.1"
  }
}
```

`npm install` kept working fine locally after that, so I didn't notice anything wrong. But the `npm ci` step in the CI pipeline started failing.

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
npm error
npm error Clean install a project
```

Running `npm install` locally against the exact same `package.json` produced no error at all, so my first guess was that the CI environment's npm cache was corrupted.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Package management: npm (using `package-lock.json`)
- CI: a job that runs a clean install with `npm ci`

## What I Tried

I suspected the CI cache first, so I cleared it and re-ran the install.

```bash
npm cache clean --force
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
```

The same error came back, so the cache wasn't the issue. Next, I compared `package.json` and `package-lock.json` directly.

```bash
grep -A2 '"is-odd"' package.json
grep -m1 '"is-odd"' -A2 package-lock.json
```

```text
"is-odd": "^3.0.1"
```

`is-odd` existed in `package.json`, but there was no matching entry at all in `package-lock.json`. That's when it became clear this wasn't a CI-specific problem — the lock file simply hadn't caught up with `package.json`.

## Root Cause

`npm ci` treats the lock file as an exact blueprint and requires `package.json` and `package-lock.json` to match completely before it will do a clean install. I had added `is-odd` to `dependencies` by hand and never ran `npm install`, so `package-lock.json` never picked up an entry for `is-odd` or its own dependency, `is-number`.

`npm install`, by contrast, looks at the difference between `package.json` and the actual dependency tree and quietly patches the lock file as it installs — which is exactly why the problem stayed invisible locally. `npm ci` intentionally skips that patching step: any mismatch and it stops immediately with `EUSAGE`. That behavior is the whole point of using `npm ci` in CI — it exists specifically to catch dependencies that were never properly recorded in the lock file, and in this case it did exactly that.

It's worth remembering that `npm ci` also deletes the existing `node_modules` directory before installing, which is a separate but related reason it's the recommended command for CI: every run starts from the lock file alone, with no leftover state from a previous install to mask a drifted dependency tree. A local `npm install`, run against a `node_modules` that already has most packages in place, has far less to reconcile and is much less likely to surface this kind of gap. That asymmetry is exactly why the same `package.json` behaved differently in the two environments.

## How I Fixed It

### 1. Compare package.json and package-lock.json

```bash
grep -A2 '"is-odd"' package.json
grep -m1 '"is-odd"' -A2 package-lock.json
```

I confirmed which package existed in `package.json` but was missing from `package-lock.json`.

### 2. Regenerate the lock file with npm install

```bash
npm install
```

```text
added 2 packages, and audited 4 packages in 403ms

found 0 vulnerabilities
```

`package-lock.json` was updated to match `package.json`, adding entries for `is-odd` and its dependency `is-number`.

### 3. Commit the updated lock file

```bash
git add package.json package-lock.json
git commit -m "fix: sync package-lock.json with is-odd dependency"
```

I kept the lock file update in the same commit as the `package.json` change rather than splitting them apart.

### 4. Re-verify with npm ci

```bash
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 408ms

found 0 vulnerabilities
```

The clean install completed with no `EUSAGE` error.

## Verify It Works

I checked that the newly added dependency was actually installed under `node_modules`.

```bash
ls node_modules | grep -E "left-pad|is-odd|is-number"
```

```text
is-number
is-odd
left-pad
```

Both `is-odd` and its dependency `is-number` were present, confirming the regenerated lock file was applied correctly.

## Takeaways

- `npm ci` requires `package.json` and `package-lock.json` to match exactly, so hand-editing `package.json` alone isn't enough.
- `npm install` silently patches over lock file drift locally, which is exactly why this kind of mismatch is easy to miss until CI catches it. Always add or change dependencies with `npm install <package-name>` so both files update together.
- If you've already hand-edited `package.json`, just run `npm install` once to regenerate the lock file, then commit `package.json` and `package-lock.json` together — `npm ci` will pass again.
- On a team, this same failure shows up whenever someone resolves a merge conflict in `package.json` by hand and forgets to re-run `npm install` afterward. A pre-commit or pre-push hook that runs `npm ci --dry-run` (or simply `npm install` and checks whether `package-lock.json` changed) catches the drift before it ever reaches CI, rather than after a pipeline turns red.

## Related Articles

- [npm install ERESOLVE Error: How to Fix It](/en/npm-eresolve-error)
- [How to Clear the npm Cache (npm cache clean --force)](/en/npm-cache-clear)
- [npm vs yarn: Key Differences](/en/npm-vs-yarn)
- [Managing Node.js Versions with nvm (Windows/Mac)](/en/node-version-management-nvm)
