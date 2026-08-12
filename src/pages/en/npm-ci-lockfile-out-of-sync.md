---
title: 'Fix: npm ci Fails with "package.json and package-lock.json...are in sync"'
date: '2026-08-12'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'A GitHub Actions npm ci step fails with "can only install packages when your package.json and package-lock.json...are in sync". Here is why editing package.json by hand breaks the lock file, and how to fix it with npm install.'
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json', 'GitHub Actions']
---

## What I Was Trying to Do

In a small Node.js side project, I wanted to add `is-odd` as a dependency. It was a quick fix, so instead of running `npm install is-odd`, I just added a line directly to `package.json`.

```json
"dependencies": {
  "left-pad": "^1.3.0",
  "is-odd": "^3.0.1"
}
```

I assumed `node_modules` already had what it needed locally, so I staged and pushed `package.json` as-is.

```bash
git add package.json
git commit -m "add: is-odd dependency"
git push origin main
```

Right after the push, the `build` workflow on GitHub Actions turned red. Opening the log, the failure was at the `npm ci` step.

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
```

`npm run build` had worked fine locally, so at first I had no idea what was wrong.

## Environment

- OS: Ubuntu 22.04 (local) / `ubuntu-latest` (GitHub Actions runner)
- Node.js: v22.22.2 (pinned via `actions/setup-node`)
- npm: 10.9.7
- Git: 2.43.0
- CI: GitHub Actions, install step configured to run `npm ci`

## What I Tried

First, I checked whether the exact CI error would reproduce locally. I removed `node_modules` and ran `npm ci`.

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

It reproduced exactly. That ruled out a CI-specific quirk — whatever I had pushed to the repo was already in a broken state.

The reason `npm run build` had worked locally became clear: `node_modules` still had a leftover copy of `is-odd` from an earlier `npm install`, unrelated to this change. `npm ci` always deletes `node_modules` first and installs strictly from `package-lock.json`, so whether files physically exist on disk doesn't matter — only the lock file's consistency with `package.json` does.

Next, I checked what was actually inside `package-lock.json`.

```bash
grep -A2 '"is-odd"' package-lock.json
```

`package.json` had `is-odd` listed under `dependencies`, but `package-lock.json` had no matching entry at all. That's when it clicked: editing `package.json` directly does nothing to `package-lock.json` — it has to be regenerated separately.

## Root Cause

Unlike `npm install`, `npm ci` never resolves dependencies on its own. It trusts `package-lock.json` (or `npm-shrinkwrap.json`) completely and cross-checks it strictly against `package.json`. If even one entry is out of sync, `npm ci` refuses to proceed and fails immediately with `EUSAGE`.

In this case, I had added `is-odd` to `package.json`'s `dependencies` by hand, but `package-lock.json` only updates when `npm install` actually runs. Had I run `npm install` even once locally, the lock file would have updated right then and I'd have noticed the diff. Editing the file directly skipped that step entirely, so the mismatch stayed invisible until it hit CI.

Many GitHub Actions workflows use `npm ci` instead of `npm install` for speed and reproducibility. Skipping dependency resolution makes it fast and CI-friendly, but it comes with a hard requirement: `package-lock.json` and `package.json` must match exactly. Developers used to an `npm install`-based local workflow tend to edit `package.json` alone without thinking about this, which is exactly how this kind of break usually gets discovered for the first time — in CI.

## How I Fixed It

### 1. Confirm the package.json change

I double-checked that the dependency I'd added was correct.

```bash
cat package.json
```

Confirmed `is-odd` was listed as `"^3.0.1"`.

### 2. Regenerate the lock file with npm install

With `package.json` as the source of truth, I regenerated the lock file.

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 484ms

found 0 vulnerabilities
```

I confirmed via `git diff` that both `is-odd` and its own dependency, `is-number`, were newly added to the lock file.

```bash
git diff package-lock.json | head -20
```

New entries for `is-odd` and `is-number` showed up in the diff.

### 3. Commit the updated lock file

```bash
git add package.json package-lock.json
git commit -m "fix: sync package-lock.json with is-odd dependency"
git push origin main
```

The key part here is staging and committing `package-lock.json` alongside `package.json`. Committing only one of the two brings the same failure right back.

### 4. Verify npm ci no longer fails

Before pushing, I re-ran a clean install locally under the same conditions CI uses, to confirm it would succeed.

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 333ms

found 0 vulnerabilities
```

It installed cleanly with no errors.

## Verify It Works

After pushing, I checked the GitHub Actions run again — the `npm ci` step completed successfully, and the build and test steps that follow it passed too. As a final check, I cloned the repo into a fresh directory and ran `npm ci` on its own to make sure it behaved the same way from a clean slate.

```bash
git clone https://github.com/example-user/example-app.git check-clone
cd check-clone
npm ci
```

```text
added 3 packages, and audited 4 packages in 401ms

found 0 vulnerabilities
```

The install completed with no issues in a clean environment as well.

## Takeaways

- `npm ci` strictly cross-checks `package.json` against `package-lock.json` and stops with `EUSAGE` on any mismatch. It skips dependency resolution entirely, which makes it fast and reproducible, but also strict.
- Editing `package.json` by hand to add or change a dependency does not update `package-lock.json`. Always run `npm install` afterward and commit the resulting lock file diff along with `package.json`.
- A successful local `npm run build` proves nothing here — `node_modules` may just have a stale copy left over from an earlier install. To reproduce CI's conditions locally, run `rm -rf node_modules && npm ci` before trusting a green local build.

## FAQ

**Q: Do I need to run `npm install` every time I touch package.json?**
Only when you add, remove, or change a version range under `dependencies` or `devDependencies` — in that case, run `npm install` (or `npm update`) to regenerate `package-lock.json` and commit both files together. Changes to `scripts` or other fields don't affect the lock file.

**Q: Can I avoid this by using `npm install` instead of `npm ci` in CI?**
Technically yes, but it's not a good idea. `npm install` will happily resolve and install even when `package.json` and `package-lock.json` disagree, which opens the door to CI and local machines ending up with different installed versions. `npm ci`'s strictness exists specifically to catch this kind of drift early — better to keep CI on `npm ci` and be disciplined about keeping the lock file in sync instead.

**Q: What's the right way to resolve merge conflicts in package-lock.json?**
Resolve the conflict in `package.json` first, then regenerate `package-lock.json` with `npm install` rather than hand-editing it. It's a generated file, and manually resolving conflicts in it almost always leaves it internally inconsistent.

## Related Articles

- [How to Fix npm ERESOLVE Dependency Tree Error](/en/npm-eresolve-error)
- [How to Fix npm EACCES Permission Denied Error](/en/npm-install-permission-denied)
- [How to Clear npm Cache and Fix Install Issues](/en/npm-cache-clear)
- [Speed Up GitHub Actions Builds with Node.js npm Cache](/en/github-actions-node-cache)
- [How to Resolve Merge Conflicts After git pull](/en/git-pull-merge-conflict)

## Recommended VPS / Cloud Hosting
Looking for developer-friendly infrastructure to deploy what you just fixed? These providers are solid choices for production workloads.
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - managed cloud hosting with one-click stacks.
- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - bare-metal and VPS optimized for demanding workloads.
