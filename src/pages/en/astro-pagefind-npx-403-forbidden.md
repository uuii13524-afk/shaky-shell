---
title: 'Fix "403 Forbidden" from npx pagefind: it Was Never in package.json'
date: '2026-08-18'
category: 'Astro'
layout: '../../layouts/PostLayoutEn.astro'
description: 'The npx pagefind step in an Astro build fails with a 403 Forbidden once npm registry access is restricted. The cause: pagefind was never pinned in package.json, so npx silently re-fetches it on every build. Here is how to pin it as a devDependency and fix it for good.'
en_tags: ['Astro', 'npm', 'pagefind']
---

## What I Was Trying to Do

This blog is built with Astro, and the `build` script in `package.json` looked like this:

```json
"scripts": {
  "build": "astro build && npx pagefind --site dist"
}
```

`pagefind` builds the site's search index, and I was just running it through `npx` directly. This had worked fine on my dev machine for a long time. Then I ran the same build inside a sandboxed environment with restricted outbound network access (a test container that only allowed traffic to the npm registry's usual host, nothing else unusual). `astro build` itself succeeded, but the `pagefind` step right after it started failing.

```bash
npm run build
```

```text
npm error code E403
npm error 403 403 Forbidden - GET https://registry.invalid/pagefind
npm error 403 In most cases, you or one of your dependencies are requesting
npm error 403 a package version that is forbidden by your security policy, or
npm error 403 on a server you do not have access to.
npm error A complete log of this run can be found in: /root/.npm/_logs/2026-08-18T00_10_16_926Z-debug-0.log
```

All 265 pages from `astro build` were generated correctly, so the build itself wasn't broken. Only the `pagefind` step right after it was getting rejected trying to reach the registry — a confusing failure to pin down, since the two commands are chained with `&&` and look like one step in the logs.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Astro: ^6.3.5 (`astro build` succeeds on its own)
- pagefind: effectively 1.5.2, fetched fresh via `npx` each time
- `pagefind` was not listed under `dependencies` or `devDependencies` in `package.json`

## What I Tried

My first guess was a registry misconfiguration, so I checked `.npmrc` and the active registry.

```bash
cat .npmrc 2>/dev/null
npm config get registry
```

```text
https://registry.npmjs.org/
```

That was pointing at the correct official registry, nothing suspicious there. Next I wondered why `astro build` could complete entirely from `node_modules` while `pagefind` needed to reach out to the network at all.

```bash
grep -n pagefind package.json package-lock.json
```

```text
package.json:    "build": "astro build && npx pagefind --site dist",
```

`package-lock.json` had no entry for `pagefind` at all, and it wasn't declared in either `dependencies` or `devDependencies`. In other words, `pagefind` had never actually been installed as a project dependency — every single `npm run build` was having `npx` reach out to the registry and fetch it fresh. Running the same build on an unrestricted machine, I noticed a warning I had scrolled past before:

```text
npm warn exec The following package was not found and will be installed: pagefind@1.5.2
```

That `npm warn exec` line only gets skipped if npm's local cache already has the package. On a clean environment with no cache — a fresh CI runner, or this sandboxed container — a network fetch was mandatory every time. That's when it clicked: the network call itself wasn't misconfigured, the problem was that a binary that should have lived locally was being pulled from the outside world on every single build.

## Root Cause

`npx <package>` uses a locally installed copy from `node_modules` if one exists, and otherwise fetches it temporarily at run time before executing it. Because the build script called `npx pagefind` and `pagefind` was never pinned in `package.json`, every build silently depended on being able to reach the npm registry at build time.

That assumption held on my dev machine and on CI runners with unrestricted network, so it never surfaced. But on any environment with restricted or partially blocked registry access — a build pipeline behind a corporate proxy, a CI job with an allowlisted registry, or a near-offline sandbox — `astro build` succeeds because it's fully self-contained in `node_modules`, while `npx pagefind` fails on its own with a 403 or a timeout. On top of the network dependency, the version was never pinned either, which was its own reproducibility risk.

## The Fix

Pin `pagefind` as a real dependency instead of leaving it to `npx` to resolve on the fly.

```bash
npm install --save-dev pagefind@1.5.2
```

Confirm the entries landed in both `package.json` and `package-lock.json`.

```bash
grep -n pagefind package.json package-lock.json | head -5
```

```text
package.json:    "build": "astro build && npx pagefind --site dist",
package.json:    "pagefind": "^1.5.2"
package-lock.json:        "pagefind": "^1.5.2"
package-lock.json:    "node_modules/@pagefind/darwin-arm64": {
```

Once `pagefind` is installed locally, `npx` uses that local copy instead of hitting the registry, so the build script text technically didn't need to change. To make that explicit and remove the `npx` indirection entirely, I called the binary directly instead:

```json
"scripts": {
  "build": "astro build && pagefind --site dist"
}
```

npm scripts automatically add `node_modules/.bin` to `PATH`, so `pagefind` resolves to the local binary with no extra configuration.

## Verifying the Fix

I ran the same build again with registry access blocked, exactly as before.

```bash
npm_config_registry=https://registry.invalid/ npm run build
```

```text
[build] 265 page(s) built in 7.76s
[build] Complete!
Indexed 265 pages
Indexed 9567 words
Finished in 1.846 seconds
```

Both `astro build` and `pagefind` completed successfully even with the registry unreachable, and `npm error code E403` didn't come back. With the version now locked in `package-lock.json`, the build also stopped being able to silently pick up a different `pagefind` version over time.

## Things That Tripped Me Up

- `npx <package>` is convenient exactly because it fetches whatever isn't installed locally — but that convenience is really a hidden network dependency baked into the build script. Any `npx` call for a package that isn't declared in `package.json` carries the same risk of breaking the moment the CI environment changes.
- I almost missed this entirely because `astro build`'s log looked completely healthy — the failure was in the next command chained with `&&`, and multi-command scripts like that don't make it obvious which command actually produced an error.
- My dev machine's npm cache had been quietly masking this for a long time. This is the kind of bug that only shows up once you run a build on a genuinely clean environment with no cache.

## FAQ

**Q: Would installing pagefind normally from the start have avoided this?**
Yes. Pinning it as a real dependency in `package.json` means the network fetch happens once, during `npm install`, and the `build` script itself can then run fully offline.

**Q: Does this matter if I'm using `npm ci`?**
`npm ci` installs strictly what's listed in `package-lock.json`. Since `pagefind` wasn't listed there, it was never part of what `npm ci` installed — it was a separate fetch triggered later by `npx` at build time. After pinning it as a devDependency, `npm ci` alone is enough to have `pagefind` ready.

**Q: Are there other commands likely to have the same problem?**
Any tool invoked via `npx` from a CI or build script carries the same risk if it isn't declared as a project dependency. Running `grep -n "npx " package.json` is a quick way to audit for undeclared `npx` calls before they turn into a build failure somewhere else.

## Related Articles

- [Adding SEO Meta Tags to an Astro Post](/en/astro-seo-meta-tags)
- [Setting Up sitemap.xml and robots.txt in Astro](/en/astro-sitemap-robots)
- [Fixing npm's ERESOLVE Error](/en/npm-eresolve-error)
- [Caching Node.js Dependencies in GitHub Actions](/en/github-actions-node-cache)
- [Checking Cloudflare Pages Build Logs](/en/cloudflare-pages-build-log)
