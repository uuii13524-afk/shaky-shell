---
title: 'Fix: Error [ERR_REQUIRE_ESM] When Requiring chalk in Node.js'
date: '2026-09-21'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Requiring an ESM-only package like chalk in Node.js throws Error [ERR_REQUIRE_ESM]. Here is the cause and how to fix it with dynamic import or a version pin.'
en_tags: ['Node.js', 'ESM', 'CommonJS']
---

## What I Was Trying to Do

I wanted to update `chalk`, which our internal CLI tool `deploy-notify` had been using for a while to colorize log output.

```bash
npm install chalk@latest
node index.js
```

`npm install` finished without any error, but `node index.js` threw an exception immediately.

```text
node:internal/modules/cjs/loader:1105
  throw new ERR_REQUIRE_ESM(filename, true, hint);
  ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/deploy-notify/node_modules/chalk/source/index.js from /home/user/deploy-notify/index.js not supported.
Instead change the require of index.js in /home/user/deploy-notify/index.js to a dynamic import() which is available in all CommonJS modules.
    at Object.Module._extensions..js (node:internal/modules/cjs/loader:1105:13)
    at Module.load (node:internal/modules/cjs/loader:981:32)
    at Function.Module._load (node:internal/modules/cjs/loader:822:12)
    at Module.require (node:internal/modules/cjs/loader:1005:19)
    at require (node:internal/modules/helpers:102:18)
    at Object.<anonymous> (/home/user/deploy-notify/index.js:1:15) {
  code: 'ERR_REQUIRE_ESM'
}

Node.js v18.18.0
```

This code had been running fine with `chalk@4.1.2` until yesterday, and the only line I touched was `require('chalk')`. I didn't expect a version bump to break this much, so my first guess was a corrupted `node_modules`.

## Environment

- OS: Ubuntu 22.04 LTS
- Node.js: v18.18.0
- npm: 9.8.1
- Project's `package.json`: no `"type"` field (defaults to CommonJS)
- Package involved: `chalk` (upgraded from 4.1.2 to 5.3.0)

## What I Tried

I suspected `node_modules` corruption first, so I did a clean install.

```bash
rm -rf node_modules package-lock.json
npm install
node index.js
```

Same error. That's when I ruled out `node_modules` as the cause.

Next I checked `node_modules/chalk/package.json` directly.

```bash
cat node_modules/chalk/package.json
```

```json
{
  "name": "chalk",
  "version": "5.3.0",
  "type": "module",
  "exports": "./source/index.js"
}
```

The `"type": "module"` field stood out immediately — I had a feeling that was clashing with CommonJS's `require()`.

Just to check, I tried the naive fix of rewriting `require('chalk')` as `import chalk from 'chalk'`, but since the project's own `package.json` had no `"type": "module"`, that produced a different error.

```text
SyntaxError: Cannot use import statement outside a module
```

The direction felt right, but it didn't match the project's overall module setup.

## Root Cause

Starting with v5, `chalk` became a pure ESM (ECMAScript Modules) package and dropped CommonJS `require()` support. When a package's own `package.json` declares `"type": "module"`, Node.js treats every `.js` file inside that package as ESM.

`require()`, on the other hand, is a CommonJS mechanism that resolves modules synchronously. ESM is specified to load asynchronously, so synchronously `require()`-ing an ESM-only package from CommonJS is structurally impossible. Node.js detects this and throws `ERR_REQUIRE_ESM`, pointing you toward `import()` (dynamic import) instead.

This particular project had no `"type"` field in its own `package.json`, so it defaulted to CommonJS. Installing `chalk@latest` (the 5.x line) into that CommonJS codebase created the exact combination that triggers the error: CommonJS code requiring an ESM-only package. Up through `chalk@4`, the package shipped as a dual CommonJS/ESM package, so this never came up — the v5 upgrade was the actual trigger.

## How I Fixed It

There are two viable fixes depending on the situation. I went with option 1 for this CLI tool.

### Option 1: Pin chalk to the last CommonJS-compatible version

This is the pragmatic choice if you don't have the bandwidth to convert the whole project to ESM right now.

```bash
npm install chalk@4
```

```text
added 1 package, and audited 45 packages in 1s
```

```bash
node index.js
```

```text
[deploy-notify] Starting deployment
```

The error went away without touching the `require('chalk')` line at all. `chalk@4.1.2` is the last version in the 4.x line that works under CommonJS — its `package.json` has no `"type"` field at all.

```bash
cat node_modules/chalk/package.json | grep '"version"\|"type"'
```

```text
"version": "4.1.2",
```

### Option 2: Use dynamic import to load the ESM version (if you need the latest chalk)

If you actually need a feature from a newer chalk release, wrap the import in a top-level `async` function and use `import()`.

```js
async function main() {
  const chalk = (await import('chalk')).default;
  console.log(chalk.green('Starting deployment'));
}

main();
```

Writing `await import('chalk')` directly at the top level throws a `SyntaxError`. CommonJS modules don't support top-level await, so `await` only works inside an `async` function — dynamic import has to be wrapped accordingly.

```bash
node index.js
```

```text
[deploy-notify] Starting deployment
```

This also ran without errors.

## Verify It Works

Since I went with option 1 (pinning to `chalk@4`), I did a final check that the dependency actually resolved the way I intended.

```bash
npm ls chalk
```

```text
deploy-notify@1.0.0 /home/user/deploy-notify
└── chalk@4.1.2
```

It resolved to `^4.1.2` as expected. I also tightened the version range so a future `npm update` can't silently jump back to the 5.x line.

```json
{
  "dependencies": {
    "chalk": "^4.1.2"
  }
}
```

## Takeaways

- `ERR_REQUIRE_ESM` means "CommonJS `require()` tried to load an ESM-only package." Checking whether the package's own `package.json` has `"type": "module"` is the quickest way to confirm this.
- The root cause here wasn't a corrupted `node_modules` — it was a major-version upgrade of a dependency dropping CommonJS support. Before running `npm install <pkg>@latest`, it's worth checking whether the package's module format changed, not just its API.
- The fix comes down to two options: pin to the last CommonJS-compatible version if you want to keep the project as CommonJS, or convert the project to ESM (or wrap the import in an `async` function with dynamic `import()`) if you need the latest release. Pinning is the faster path when a full ESM migration isn't feasible right now.
- The same error shows up with other packages that have gone ESM-only, like `node-fetch`, `execa`, and `ora`. Whenever you see `ERR_REQUIRE_ESM`, check that package's `package.json` first.

## FAQ

**Q: Would converting the whole project to `"type": "module"` fix this for good?**
Yes, but it's a bigger change than it sounds — every `require`/`module.exports` needs to become `import`/`export`, and CommonJS-only globals like `__dirname` and `__filename` stop working. If the existing codebase is large, pinning the version (option 1) as a stopgap and planning the ESM migration separately is the safer path.

**Q: If I pin to `chalk@4`, do I lose security patches?**
No — the 4.x line still receives patch releases for security fixes. Pinning with a caret range like `^4.1.2` still lets you pick up patch updates within 4.x; it only blocks the jump to the 5.x major version.

**Q: Why can't I just write `await import()` directly inside `require()`'s call site?**
Because CommonJS modules don't support top-level `await`. ESM allows top-level await, but in CommonJS, `await` is only valid inside an `async` function — so any dynamic `import()` call needs to be wrapped in one.

## Related Articles

- [Switch Node.js Versions with nvm](/en/node-version-management-nvm)
- [Fix npm ERESOLVE Errors](/en/npm-eresolve-error)
- [Run a Node.js App as a Daemon with pm2](/en/node-pm2-setup)
- [npm vs yarn: Which One Should You Use?](/en/npm-vs-yarn)
- [Fix Node.js Heap Out of Memory Errors](/en/node-heap-out-of-memory)
