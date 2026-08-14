---
title: 'Fix: npm ci Fails with EUSAGE Because package-lock.json Is Out of Sync'
date: '2026-08-14'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm ci in CI stops with an EUSAGE error saying package.json and package-lock.json are out of sync. Here is the cause and how to fix it by regenerating and committing the lock file.'
en_tags: ['Node.js', 'npm', 'npm ci', 'GitHub Actions']
---

## What I Was Trying to Do

I added `dayjs` to an internal dashboard project to simplify date formatting. Locally, `npm install` picked it up without any issue, so I committed the change and pushed.

```bash
npm install dayjs
```

```text
added 1 package, and audited 3 packages in 587ms
found 0 vulnerabilities
```

But the GitHub Actions build job failed at the `npm ci` step:

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.21 from lock file
npm error
npm error Clean install a project
```

Everything worked fine locally, so I had no idea why it was only breaking in CI.

## Environment

- CI runner: GitHub Actions (`ubuntu-24.04`)
- Local OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Package added: `dayjs@^1.11.10` (resolved to `1.11.21` at install time)

## What I Tried

I checked the workflow file first:

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '22'
- run: npm ci
- run: npm run build
```

Nothing looked wrong with the `npm ci` step itself. Next I suspected a local cache issue, so I removed `node_modules` and ran `npm install` again.

```bash
rm -rf node_modules
npm install
```

```text
added 1 package, and audited 3 packages in 587ms
found 0 vulnerabilities
```

Still succeeded locally. That's when it clicked: locally I was running `npm install`, but CI runs `npm ci`. I reproduced it locally by running the exact CI command.

```bash
rm -rf node_modules
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.21 from lock file
```

Checking `git status` and history confirmed it: `package.json` was in the latest commit, but the corresponding `package-lock.json` change never got staged and was still sitting one commit behind.

```bash
git log --oneline -1 -- package-lock.json
git log --oneline -1 -- package.json
```

Looking back at how it happened, I remembered running `git add src/` right after testing the change, then committing without ever running a plain `git status` to see the full list of modified files. `package-lock.json` showed up as modified in the working tree the whole time — I just never looked at it before committing. It's an easy mistake to repeat if `git add` is habitually scoped to a specific directory instead of reviewing the full diff first.

## Root Cause

`npm install` reads `package.json`, resolves dependencies, and updates `package-lock.json` as needed while it installs — so even right after editing `package.json`, running it once is enough to make everything consistent again.

`npm ci`, by contrast, only installs exactly what's already written in `package-lock.json`. It checks that the lock file matches `package.json` and, if it doesn't, fails immediately instead of trying to resolve anything. That strict, no-resolution behavior is exactly why `npm ci` is recommended for CI — it guarantees reproducible installs — but it also means a forgotten `package-lock.json` commit stays invisible locally and only surfaces in CI.

This is also why the error message specifically calls out `Missing: dayjs@1.11.21 from lock file` rather than something more generic like "install failed." npm already knows exactly which package is missing from the lock file because it diffs the dependency tree declared in `package.json` against what's recorded in `package-lock.json` before touching the filesystem at all. If even one entry doesn't line up, it refuses to guess at a resolution on your behalf.

## How I Fixed It

### 1. Regenerate the lock file

```bash
npm install
```

```text
added 1 package, and audited 3 packages in 587ms
found 0 vulnerabilities
```

### 2. Check the diff on package-lock.json

```bash
git diff package-lock.json | head -20
```

```text
        "dayjs": "^1.11.10",
        "lodash": "^4.17.21"
      }
```

Confirmed the `dayjs` entry was now present.

### 3. Commit both package.json and package-lock.json together

```bash
git add package.json package-lock.json
git commit -m "fix: sync package-lock.json for dayjs"
git push
```

### 4. Reproduce npm ci locally before pushing

```bash
rm -rf node_modules
npm ci
```

```text
added 2 packages, and audited 3 packages in 782ms
found 0 vulnerabilities
```

No errors — the install completed cleanly.

## Verify It Works

I checked the GitHub Actions run and confirmed the `npm ci` step passed, along with the build and test steps after it. As a final check, I cloned the branch fresh into a new directory and ran `npm ci` once more to make sure a clean checkout would also succeed.

## Takeaways

- `npm ci` only installs exactly what's in `package-lock.json` — it never resolves or updates dependencies. Any mismatch with `package.json` fails immediately with `EUSAGE`.
- `npm install` silently updates the lock file, which is why this kind of mismatch hides so easily on a local machine. Always commit `package.json` and `package-lock.json` together whenever dependencies change.
- Running `rm -rf node_modules && npm ci` locally before pushing catches this class of bug before CI does.

## FAQ

**Q: Should CI use `npm install` or `npm ci`?**
Use `npm ci`. It installs exactly what's recorded in `package-lock.json`, so CI and local environments stay reproducible. `npm install` can rewrite the lock file, which defeats that purpose.

**Q: Is it fine to gitignore package-lock.json?**
No — it should always be committed. Ignoring it means every developer and every CI run can resolve a different set of dependency versions, making mismatches like this one far more likely.

**Q: I only added one dependency, but the lock file diff is huge. Why?**
This can happen when the npm version differs between machines — formatting or `lockfileVersion` metadata can change even without a dependency change. Make sure your team and CI are using the same npm version.

**Q: Can a pre-commit hook catch this automatically?**
Yes. A simple pre-commit hook that runs `git diff --cached --name-only` and fails if `package.json` is staged without `package-lock.json` (or vice versa) catches this before it ever reaches a push, which is cheaper than waiting for CI to fail.

## Related Articles

- [Fixing an ERESOLVE Error During npm install](/en/npm-eresolve-error)
- [Clearing the npm Cache to Fix Install Issues](/en/npm-cache-clear)
- [Fixing a Rejected git push](/en/git-push-rejected-fix)
- [Using Secrets in GitHub Actions](/en/github-actions-secrets)
- [Managing Node.js Versions with nvm](/en/node-version-management-nvm)
