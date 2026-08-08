---
title: 'Fix: npm ci Fails With "package.json and package-lock.json ... in sync" Error'
date: '2026-08-08'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'npm ci fails in CI with an EUSAGE error saying package.json and package-lock.json are out of sync, even though npm install works fine locally. Here is the cause (a bad merge conflict resolution) and how to fix it.'
en_tags: ['Node.js', 'npm', 'GitHub Actions']
---

## What I Was Trying to Do

I added `axios` to a project for a small API client and opened a PR. Locally everything worked, so I expected CI to just pass.

```bash
npm install axios
git add package.json package-lock.json
git commit -m "feat: add axios for API client"
```

Right before pushing, another PR had just merged into `main`, so I pulled it in first.

```bash
git fetch origin main
git merge origin/main
```

That produced a conflict in `package-lock.json`. Rather than reading through the diff, I took the shortcut of just keeping my own side.

```bash
git checkout --ours package-lock.json
git add package-lock.json
git commit -m "merge: resolve lockfile conflict"
git push
```

`npm run build` and `npm test` both passed locally, so I pushed without worrying further. GitHub Actions came back red with this:

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: axios@1.7.7 from lock file
npm error
npm error Clean install a project
```

It didn't reproduce locally at all — only CI was failing.

## Environment

- OS: macOS Sonoma 14.5 (local) / Ubuntu 22.04 (GitHub Actions `ubuntu-latest`)
- Node.js: 20.11.1
- npm: 10.2.4
- CI: GitHub Actions, `actions/setup-node@v4` + `npm ci`
- Package in question: `axios@1.7.7`

## What I Tried

My first guess was a stale GitHub Actions cache, so I cleared it and reran the workflow.

```yaml
# .github/workflows/ci.yml (relevant part)
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: 'npm'
- run: npm ci
```

Same failure. Next I removed `node_modules` locally and ran `npm ci` there too, instead of my usual `npm install`.

```bash
rm -rf node_modules
npm ci
```

```text
npm error code EUSAGE
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error Missing: axios@1.7.7 from lock file
```

Same error, locally this time. I'd only ever used `npm install` day to day, never `npm ci` — so things "just worked" without me noticing the mismatch. `npm install` tolerates a gap between `package.json` and the lock file and quietly fills it in, which is exactly why I hadn't seen this before.

I checked the lock file directly:

```bash
grep -c '"axios"' package-lock.json
```

```text
0
```

`axios` was in `package.json` but absent from `package-lock.json`. That's when I remembered the `git checkout --ours package-lock.json` from the merge conflict.

## Root Cause

`git checkout --ours package-lock.json` takes "our" side of the conflict as-is — in this case, the feature branch's lock file from before `axios` was added. Resolving the conflict that way left `package.json` with `axios` added, but rolled `package-lock.json` back to a version that had never seen it.

`npm install` treats `package.json` as the source of truth and silently installs whatever the lock file is missing, so this kind of drift doesn't surface in normal local development. `npm ci`, by contrast, is built for reproducible installs: it requires the lock file to match `package.json` exactly, and refuses to install anything if it doesn't — that's the whole point of the EUSAGE error. Since the CI workflow used `npm ci` for speed and reproducibility, it was the only place the mismatch actually got caught.

## How I Fixed It

### 1. Regenerate the lock file locally

Treat `package.json` as correct and resync the lock file against it.

```bash
npm install
```

```text
added 1 package, and audited 842 packages in 3s
```

### 2. Check the diff

```bash
git diff package-lock.json | head -20
```

```diff
+    "node_modules/axios": {
+      "version": "1.7.7",
+      "resolved": "https://registry.npmjs.org/axios/-/axios-1.7.7.tgz",
+      "integrity": "sha512-S4kL7XrjYTOVwqZH2WVGGNcpaVMLtQmxWn0LN8m6dV0KKa3sB79pDNwbwSlmiVfmSaYbAX6P4x8bIReXQTLyxg==",
```

The `axios` entry was now present.

### 3. Verify with npm ci

```bash
rm -rf node_modules
npm ci
```

```text
added 843 packages, and audited 843 packages in 8s
found 0 vulnerabilities
```

Clean install, no errors.

### 4. Commit and push

```bash
git add package-lock.json
git commit -m "fix: resync package-lock.json with package.json"
git push
```

## Verify It Works

After pushing, GitHub Actions reran and the `npm ci` step succeeded:

```text
Run npm ci
added 843 packages, and audited 843 packages in 6s
found 0 vulnerabilities
```

The build and test steps completed as well, and all status checks on the PR turned green.

## What I'd Do Differently

The real gap was not understanding the difference between `npm install` and `npm ci`. Because I only ever used `npm install` locally, a mismatch between `package.json` and `package-lock.json` never threw an error — it just got silently patched over. `npm ci` in CI was the first thing that actually enforced consistency. Resolving a `package-lock.json` conflict with `--ours`/`--theirs` is risky whenever the conflicting commits touched dependencies; after resolving that way, always run `npm install` to regenerate the lock file properly.

I've since started running `npm ci` locally at least once before opening a PR that touches dependencies, instead of trusting `npm install` alone. It only takes a few extra seconds and it catches exactly this class of drift before it ever reaches a reviewer or a CI run. I also stopped resolving lock file conflicts with `--ours`/`--theirs` as a reflex — now I treat any conflict inside `package-lock.json` as a signal to stop, look at what actually changed in both `package.json` versions, and regenerate the lock file from a merged `package.json` rather than merging the lock file's contents by hand.

## FAQ

**Q: Should I use `npm install` or `npm ci`?**
Use `npm install` for local development, since it's meant to add and update dependencies. Use `npm ci` anywhere you want an exact, reproducible install — CI pipelines, deployments — since it wipes `node_modules` and installs strictly from the lock file, which also makes local/CI drift easier to catch.

**Q: What's the right way to resolve a `package-lock.json` merge conflict?**
Don't resolve it mechanically with `--ours` or `--theirs`. Check what each side's `package.json` actually changed, get `package.json` into the state you want first, then run `npm install` to regenerate the lock file. Avoid hand-editing the lock file directly.

**Q: Can I catch this before it ever reaches CI?**
Yes — add a pre-commit or pre-push hook that runs something equivalent to `npm ci --dry-run`, or move the `npm ci` step earlier in your CI workflow so PRs fail fast on a lock file mismatch before review.

## Related Articles

- [Fix npm ERR! ERESOLVE Dependency Conflicts](/en/npm-eresolve-error)
- [Fix npm install Failing With EACCES](/en/npm-install-permission-denied)
- [Resolving Merge Conflicts on git pull](/en/git-pull-merge-conflict)
- [Using Secrets in GitHub Actions](/en/github-actions-secrets)
- [Working With package.json Scripts](/en/npm-package-json-scripts)
