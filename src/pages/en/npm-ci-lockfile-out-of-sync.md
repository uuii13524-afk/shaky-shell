---
title: 'Fix: npm ci Fails with EUSAGE — package.json and package-lock.json Out of Sync'
date: '2026-08-20'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm ci in CI fails with an EUSAGE error saying package.json and package-lock.json are out of sync. Here is why it happens and how to fix it by resyncing the lockfile with npm install.'
en_tags: ['Node.js', 'npm', 'CI/CD']
---

## What I Was Trying to Do

I added a new dependency, `dayjs`, to a Node.js project. Locally, I just edited one line into `package.json`'s `dependencies` block by hand, and committed without running `npm install` first.

```json
{
  "dependencies": {
    "left-pad": "^1.3.0",
    "dayjs": "^1.11.10"
  }
}
```

To reproduce what would happen in CI (a GitHub Actions style environment), I removed `node_modules` locally and ran `npm ci`. It failed immediately.

```bash
rm -rf node_modules
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
npm error
npm error Usage:
npm error npm ci
```

I don't normally run `npm ci` locally — I default to `npm install` — so I never noticed the mismatch before committing.

## Environment

- OS: Ubuntu 24.04 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Package manager: npm (no yarn/pnpm involved)
- Dependency added: `dayjs@^1.11.10`

## What I Tried

My first guess was a stale CI cache, so I considered bumping the `actions/cache` key to invalidate it. But reading the error more carefully, `Missing: dayjs@1.11.23 from lock file` pointed at the lockfile itself, not the cache.

Just to confirm, I grepped `package-lock.json` for `dayjs`.

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

Zero matches. `package.json` listed `dayjs`, but `package-lock.json` had no record of it at all. That's when it clicked: I had hand-edited `package.json` and never ran `npm install` afterward.

`npm ci`, unlike `npm install`, refuses to modify `package-lock.json` — that's a deliberate design choice meant to keep CI installs deterministic run after run. Editing `package.json` by hand without regenerating the lockfile is exactly the case that safeguard is built to catch.

It's an easy mistake to make precisely because nothing fails locally. `npm install` happily patches the lockfile and moves on, so a hand-edited `package.json` looks completely fine right up until someone — usually CI, sometimes a teammate who happens to run `npm ci` locally — hits the strict check.

## Root Cause

`npm ci` installs strictly from what's recorded in `package-lock.json` (or `npm-shrinkwrap.json`) and checks that it matches `package.json` exactly. Adding a package to `package.json`'s `dependencies` does nothing to the lockfile on its own — the resolved version, integrity hash, and position in the dependency tree only get written in when `npm install` runs and updates `package-lock.json`.

`npm install` tolerates a bit of drift and just updates the lockfile as it goes. `npm ci` makes the opposite assumption: it will not run unless the lockfile already matches `package.json` exactly, so an out-of-date lockfile fails immediately with EUSAGE. Because most CI pipelines use `npm ci` for reproducibility, this kind of mismatch tends to surface for the first time in CI, well after `npm install` locally made everything look fine.

## How I Fixed It

### 1. Confirm dayjs is missing from the lockfile

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

### 2. Resync the lockfile with npm install

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 2 packages, and audited 3 packages in 539ms

found 0 vulnerabilities
```

`npm install` reads `package.json` and regenerates `package-lock.json` to match.

### 3. Confirm dayjs is now in the lockfile

```bash
grep -A2 '"dayjs"' package-lock.json
```

```text
        "dayjs": "^1.11.10",
        "left-pad": "^1.3.0"
      }
```

### 4. Commit the updated lockfile together with package.json

```bash
git add package.json package-lock.json
git commit -m "chore: sync package-lock.json after adding dayjs"
```

Always commit the regenerated `package-lock.json` in the same commit as `package.json`. Committing only one of the two just reproduces the same failure for the next person who runs `npm ci`.

### 5. Re-run npm ci to confirm the fix

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 2 packages, and audited 3 packages in 523ms

found 0 vulnerabilities
```

It completed with no errors.

## Verify It Works

I checked the installed package versions with `npm ls` to confirm `dayjs` actually landed as intended.

```bash
npm ls --depth=0
```

```text
npm-ci-repro@1.0.0
+-- dayjs@1.11.23
`-- left-pad@1.3.0
```

`dayjs` is installed as expected, and `npm ci` now runs cleanly.

## Takeaways

- `npm ci` requires `package.json` and `package-lock.json` to match exactly. Hand-editing `package.json` alone never updates the lockfile.
- A `Missing: <package>@<version> from lock file` message is a strong hint — grep the lockfile for that package first before chasing anything else, like a stale CI cache.
- Whenever you add or change a dependency, run `npm install` and commit both `package.json` and `package-lock.json` together. If your CI uses `npm ci`, forgetting this produces the confusing case of "works locally, fails only in CI."

## FAQ

**Q: Should I use `npm install` or `npm ci`?**
Use `npm install` for day-to-day local development when adding or updating dependencies. Use `npm ci` in CI pipelines and Docker builds where you want an exact, reproducible install from the lockfile. Since `npm ci` deletes `node_modules` and reinstalls from scratch every time, it's overkill for routine local work.

**Q: Can I catch this before committing?**
A pre-commit hook (with `husky`, for example) that warns when only one of `package.json` or `package-lock.json` is staged catches this early. Alternatively, run `npm install --package-lock-only` to update just the lockfile, and add a CI step that fails if that produces a diff.

**Q: Does this happen with yarn or pnpm too?**
The mechanics differ, but the same class of problem exists. Yarn has `yarn install --frozen-lockfile` and pnpm has `pnpm install --frozen-lockfile` — both fail the same way `npm ci` does when the lockfile doesn't match.

**Q: What if the mismatch comes from someone else's branch merge instead of a manual edit?**
Same fix either way. Whether the drift came from a hand-edit or a merge that combined two branches with different dependency changes, running `npm install` and committing the regenerated `package-lock.json` resolves it. The only extra step after a merge is double-checking that the resulting lockfile still reflects every dependency change from both branches, not just one side's.

## Related Articles

- [Fix ERESOLVE Errors During npm install](/en/npm-eresolve-error)
- [Fix EACCES (Permission Denied) During npm install](/en/npm-install-permission-denied)
- [How to Clear the npm Cache (npm cache clean --force)](/en/npm-cache-clear)
- [package.json Scripts: A Quick Reference](/en/npm-package-json-scripts)
- [npm vs yarn: Key Differences](/en/npm-vs-yarn)
