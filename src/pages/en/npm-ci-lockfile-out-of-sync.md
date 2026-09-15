---
title: 'Fix: npm ci Fails With "package.json and package-lock.json...are in sync"'
date: '2026-09-15'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm install works fine locally, but npm ci fails in CI with a lockfile sync error. Here is the root cause — a missing package-lock.json commit — and how to fix it.'
en_tags: ['Node.js', 'npm', 'CI']
---

## What I Was Trying to Do

I added `dayjs` to my team's `api-server` repo for date formatting.

```bash
npm install dayjs
git add package.json
git commit -m "feat: add dayjs for date formatting"
git push
```

`npm run build` worked fine locally, so I pushed without a second thought. But the GitHub Actions CI run failed — and not on the code I'd written. It failed at the very first step, installing dependencies.

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrapjson are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.11 from lock file
npm error
npm error Clean install a project
```

My first guess was a stale Actions cache, so I manually cleared it and re-ran the job. Same error, no change.

## Environment

- OS: macOS Sonoma 14.5 (local) / Ubuntu 22.04 (GitHub Actions runner)
- Node.js: v20.16.0
- npm: 10.8.2
- CI: GitHub Actions (`actions/setup-node@v4` + `npm ci`)
- Repo: `api-server` (Express + TypeScript)

## What I Tried

I checked the workflow definition first.

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: 'npm'
- run: npm ci
- run: npm run build
```

Nothing unusual — just a plain `npm ci`. I re-ran the job with "Re-run all jobs" to bypass the cache entirely, and it failed with the exact same `EUSAGE` error. That ruled out the cache as the cause.

Checking `git status` locally didn't raise any flags at first.

```bash
git status
```

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

It only clicked when I looked at what the last commit actually contained with `git show --stat`.

```bash
git show --stat HEAD
```

```text
 package.json | 1 +
 1 file changed, 1 insertion(+)
```

Only `package.json` had changed. `package-lock.json` wasn't in that commit at all, even though `npm install` should have updated it too.

## Root Cause

Looking at my local `package-lock.json` with `cat`, the `dayjs` entry was actually there — `npm install` had updated it correctly. The problem was that I'd staged the commit with `git add package.json`, naming the file explicitly, and never staged `package-lock.json` alongside it. It wasn't in `.gitignore`; I'd simply forgotten to add it, so the change sat in my working tree and never made it into the commit.

The underlying design difference is this: `npm install` tolerates a mismatch between `package.json` and `package-lock.json` — it fills in whatever's missing and rewrites both files as needed. `npm ci`, on the other hand, treats `package-lock.json` as the single source of truth and fails immediately the moment it doesn't line up with `package.json`, with no attempt to reconcile the two.

Since I always ran `npm install` locally, I never hit the mismatch myself. CI was the only place running `npm ci`, so it was the only place that caught it.

## How I Fixed It

### 1. Check whether the local lockfile is actually ahead of the committed one

```bash
git diff HEAD -- package-lock.json
```

```text
diff --git a/package-lock.json b/package-lock.json
index 3a1f9c2..8e7b410 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -12,6 +12,9 @@
     "dependencies": {
       "dayjs": "^1.11.11",
+      ...
```

Comparing my working tree against HEAD confirmed it: the `dayjs` entry only existed locally, never in the commit.

### 2. Stage and commit package-lock.json explicitly

```bash
git add package-lock.json
git commit -m "chore: commit package-lock.json for dayjs"
git push
```

Naming individual files with `git add` — like I did with `package.json` — makes it easy to forget a related file. That's exactly what happened here.

### 3. Reproduce the CI install locally with npm ci before pushing

```bash
rm -rf node_modules
npm ci
```

```text
added 412 packages, and audited 413 packages in 6s
```

I now run `npm ci` locally before pushing whenever I've touched dependencies, so I catch this kind of mismatch before CI does.

### 4. Confirm the CI run

Actions re-ran automatically on the new commit, and the `npm ci` step passed.

```text
added 412 packages, and audited 413 packages in 5s
npm notice
```

## Verify It Works

As a final check, I cloned into a clean directory and repeated the same steps to confirm it holds up from scratch.

```bash
git clone git@github.com:example-org/api-server.git api-server-check
cd api-server-check
npm ci
npm run build
```

```text
added 412 packages, and audited 413 packages in 7s

> api-server@1.0.0 build
> tsc -p tsconfig.json

```

Install and build both completed without errors.

## Takeaways

- `npm install` tolerates drift between `package.json` and `package-lock.json` and silently patches both files. `npm ci` treats the lockfile as authoritative and fails immediately (`EUSAGE`) on any mismatch.
- Whenever you add a dependency, commit `package-lock.json` alongside `package.json`. Staging files by name individually makes it easy to leave a related file behind.
- Running `npm ci` locally before you push reproduces CI's strict install and surfaces a lockfile mismatch before it ever reaches your pipeline.

## FAQ

**Q: Why did CI catch this but not my local `npm install`?**
`npm install` tolerates a mismatch between `package.json` and `package-lock.json` and patches both files to close the gap. `npm ci` trusts the lockfile as-is and fails the moment it doesn't match `package.json`. If your CI uses `npm ci` and your local workflow uses `npm install`, this kind of gap can go unnoticed until CI runs.

**Q: Would `git add .` have prevented this?**
Yes — `package-lock.json` would have been staged along with everything else. That said, `git add .` carries its own risk of staging things you didn't mean to commit, so checking `git status` before every commit is the more reliable habit either way.

**Q: Was clearing the Actions cache a waste of time?**
Not entirely. It was a reasonable way to rule out one cause quickly. Reproducing the same failure with a cold cache told me it wasn't a caching issue, which let me move on to checking the commit contents next.

## Related Articles

- [Fix ERESOLVE Errors in npm](/en/npm-eresolve-error)
- [How to Clear the npm Cache](/en/npm-cache-clear)
- [Fix Permission Denied During npm install](/en/npm-install-permission-denied)
- [Cache node_modules in GitHub Actions for Faster Builds](/en/github-actions-node-cache)
- [Manage Node.js Versions with nvm](/en/node-version-management-nvm)
