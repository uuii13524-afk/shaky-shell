---
title: 'Fix: npm ci Fails With "package.json and package-lock.json...are in sync" on GitHub Actions'
date: '2026-09-28'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'On GitHub Actions, npm ci fails with an EUSAGE error saying package.json and package-lock.json are out of sync. Here is the cause and how to fix it by regenerating the lock file with npm install.'
en_tags: ['Node.js', 'npm', 'GitHub Actions']
---

## What I Was Trying to Do

I needed a small date-formatting helper for an internal tool repo, so I added a package directly to `dependencies` in `package.json` by hand.

```json
{
  "name": "npm-ci-repro",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "left-pad": "^1.3.0",
    "is-odd": "^3.0.1"
  }
}
```

Locally, my `node_modules` from an earlier `npm install` was still sitting there, so code using the new package worked fine when I tested it. I committed and pushed, and the GitHub Actions job turned red. The workflow sets up Node.js with `actions/setup-node` and then installs dependencies with `npm ci`.

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '22'
- run: npm ci
- run: npm test
```

Looking at the log, the failure happened at the `npm ci` step, before `npm test` even ran.

## Environment

- CI: GitHub Actions (`ubuntu-24.04` runner)
- Node.js: v22.22.2 (set via `actions/setup-node@v4`)
- npm: 10.9.7
- Local machine: Ubuntu 24.04 LTS
- Repo: internal tool (`package-lock.json` committed to the repo)

## What I Tried

My first guess was that the test code itself was broken, but the job never got as far as `npm test` — it stopped at `npm ci`. The log showed this:

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

I briefly suspected the runner's npm cache was corrupted, so I disabled the `cache: npm` option in `actions/setup-node` and re-ran without any cache. Same `EUSAGE` error. That ruled out a caching problem.

Reading the message more carefully, one line stood out: `Missing: is-odd@3.0.1 from lock file`. That's the exact package I had hand-added to `package.json`, along with its own dependency `is-number` — neither was recorded in `package-lock.json` at all.

My local `node_modules` already had `is-odd` installed from before, so `require` resolved fine and the local check never surfaced anything wrong. But `package-lock.json` itself had never been regenerated, so what got committed was "a `package.json` with a new dependency" paired with "a stale `package-lock.json`" that didn't know about it.

To confirm this was reproducible, I deleted `node_modules` locally and ran `npm ci` myself.

```bash
rm -rf node_modules
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

The exact same error showed up locally. That confirmed this wasn't a CI-specific quirk — the committed `package-lock.json` itself was stale.

## Root Cause

Unlike `npm install`, `npm ci` never re-resolves dependencies from `package.json`. It trusts `package-lock.json` (or `npm-shrinkwrap.json`) completely and installs exactly the versions listed there into `node_modules`. So if `package.json` and `package-lock.json` disagree, npm doesn't silently re-resolve — it stops with an error. That's a deliberate design choice meant to prevent locked dependency versions from silently drifting in CI or across a team.

The actual root cause here was straightforward: I edited `dependencies` in `package.json` by hand, forgot to run `npm install` afterward, and committed the stale `package-lock.json` along with it. It only looked fine locally because leftover `node_modules` from a previous install papered over the mismatch — I never went through `npm ci`'s stricter lock-file consistency check until CI did it for me.

## How I Fixed It

### 1. Run `npm install` locally to regenerate the lock file

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 409ms

found 0 vulnerabilities
```

`npm install` re-resolves dependencies against `package.json` and fills in the missing `is-odd` and its sub-dependency `is-number` in `package-lock.json`. Checking the lock file afterward confirmed the new dependency was recorded.

```bash
grep -A2 '"is-odd"' package-lock.json
```

```text
    "is-odd": "^3.0.1",
    "left-pad": "^1.3.0"
  }
```

### 2. Review the lock file diff before committing

```bash
git diff package-lock.json
```

I made sure the diff only added the new dependency and its sub-dependency, with nothing else changing unexpectedly. This is worth checking every time — an unrelated version bump elsewhere in the lock file is a signal something else is going on.

```bash
git add package.json package-lock.json
git commit -m "fix: update package-lock.json after adding is-odd dependency"
```

### 3. Confirm the lock file is consistent again with `npm ci`

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 352ms

found 0 vulnerabilities
```

This time it completed with no error. I confirmed `npm ci` passed locally before pushing.

### 4. Re-run GitHub Actions to confirm

After pushing, CI re-ran, `npm ci` completed cleanly, and the job continued on to `npm test` as expected.

## Verify It Works

I ran `npm ci` again locally to confirm dependencies install cleanly.

```bash
npm ci
```

```text
added 3 packages, and audited 4 packages in 352ms

found 0 vulnerabilities
```

In the CI logs, the `npm error code EUSAGE` that used to appear right after `npm ci` was gone, and the job reached `npm test`. I also kept a command handy for checking sync status before pushing, without actually installing anything:

```bash
npm ci --dry-run
```

## Takeaways

- `npm ci` never re-resolves dependencies from `package.json` — it trusts `package-lock.json` exactly as written, so any mismatch between the two stops the install with an `EUSAGE` error.
- Whenever you hand-edit `dependencies`, run `npm install` afterward so `package-lock.json` gets regenerated before you commit. Stale `node_modules` sitting around locally can hide this mismatch during your own testing.
- The same error shows up easily when multiple people add dependencies on separate branches and then merge. Running `rm -rf node_modules && npm ci` locally right after a merge catches it before CI does.

## FAQ

**Q: What's the actual benefit of `npm ci` over `npm install`?**
`npm ci` installs exactly what's recorded in `package-lock.json`, which helps avoid the classic "works on my machine, fails in CI" problem caused by dependency drift. The tradeoff is that it fails loudly, as it did here, when the lock file is out of date instead of silently re-resolving.

**Q: What should I actually look for when reviewing a `package-lock.json` diff?**
I check that only the dependency I intentionally added or updated — and its own sub-dependencies — actually changed. If unrelated packages show version bumps too, that's usually a sign of an npm version difference or a registry-side change, and I make sure `npm ci` passes locally before committing.

**Q: Is there a quick way to make CI pass without fixing the lock file?**
Swapping `npm ci` for `npm install` in the workflow would make CI pass temporarily, but that just defers the real problem and gives up the reproducibility guarantee the lock file is there for. The actual fix is running `npm install` locally to bring the lock file back in sync and committing that.

## Related Articles

- [How to Fix npm ERESOLVE Dependency Tree Error](/en/npm-eresolve-error)
- [How to Clear npm Cache and Fix Install Issues](/en/npm-cache-clear)
- [How to Use package.json Scripts to Automate Tasks](/en/npm-package-json-scripts)
- [Speed Up GitHub Actions Builds with Node.js npm Cache](/en/github-actions-node-cache)
- [Manage Node.js Versions with nvm (Windows and Mac)](/en/node-version-management-nvm)
