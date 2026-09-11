---
title: 'Fix: Error [ERR_REQUIRE_ESM] require() of ES Module Not Supported in Node.js'
date: '2026-09-11'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Upgrading chalk to v5 broke a CommonJS CLI tool with Error [ERR_REQUIRE_ESM]. Here is why require() fails against ESM-only packages, and three fixes: pin the last CJS version, use dynamic import, or migrate to ESM.'
en_tags: ['Node.js', 'ESM', 'CommonJS', 'ERR_REQUIRE_ESM']
---

## What I Was Trying to Do

I maintain a small internal CLI tool (`my-cli-tool`) that uses `chalk` to color its terminal output. `package.json` had `"chalk": "^4.1.2"` pinned, and I noticed the README badge showing a v5 release, so I bumped it without thinking too hard about it.

```bash
npm install chalk@latest
```

```text
added 1 package, and audited 43 packages in 1s
```

The install finished without any warnings, so I went ahead and ran the CLI as usual.

```bash
node index.js
```

A script that had been working fine for months suddenly threw and crashed on startup.

```text
node:internal/modules/cjs/loader:1105
  throw new ERR_REQUIRE_ESM(filename, parentPath, packageJsonPath);
  ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/my-cli-tool/node_modules/chalk/source/index.js from /home/user/my-cli-tool/index.js not supported.
Instead change the require of index.js in /home/user/my-cli-tool/index.js to a dynamic import() which is available in all CommonJS modules.
    at Object.<anonymous> (/home/user/my-cli-tool/index.js:1:16) {
  code: 'ERR_REQUIRE_ESM'
}

Node.js v20.14.0
```

`index.js` still had `const chalk = require('chalk');` on line 1 — I hadn't touched any application code, so my first guess was that the install had somehow corrupted `node_modules`.

## Environment

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- Package in question: `chalk` (upgraded from `^4.1.2` to `5.3.0`)
- Project type: CommonJS (no `"type"` field in `package.json`)

## What I Tried

First I assumed a corrupted install and did a clean reinstall.

```bash
rm -rf node_modules package-lock.json
npm install
```

```text
added 43 packages in 2s
```

Running `node index.js` again produced the exact same `ERR_REQUIRE_ESM` error. At that point I realized the package's internals had genuinely changed, not just gotten corrupted, so I opened `node_modules/chalk/package.json` directly.

```bash
cat node_modules/chalk/package.json
```

```text
{
  "name": "chalk",
  "version": "5.3.0",
  "type": "module",
  "exports": "./source/index.js",
  ...
}
```

The `"type": "module"` field was the piece I hadn't noticed before. I went and checked what it actually means in Node's documentation.

## Root Cause

The `"type": "module"` field in `package.json` tells Node.js to interpret `.js` files inside that package as ECMAScript Modules (ESM) instead of CommonJS. `chalk` completed a full migration to ESM-only in v5.0.0 and dropped CommonJS support entirely, so it can no longer be loaded with `require()`.

`my-cli-tool`'s own `package.json` has no `"type"` field, which defaults it to CommonJS. When a CommonJS module calls `require()` on a package that is now pure ESM, Node.js throws `ERR_REQUIRE_ESM` during module resolution and refuses to continue. This is a hard constraint in Node's module system: `require()` has no synchronous way to load an ES Module, since ESM evaluation is inherently asynchronous.

What made this confusing was that `npm install` completed cleanly with no warning. npm resolves version ranges and dependency trees, but it does not check whether a package's module type (`"type": "module"` vs CommonJS) is compatible with how the consuming code will load it. The mismatch only surfaces at runtime, the moment `require()` actually executes.

## The Fix

I compared three options and picked the one with the smallest blast radius for this project.

### 1. Check whether dynamic import is a viable fix

Following the hint in the error message, I tried switching `require()` to `import()`.

```js
// index.js (test edit)
const chalk = await import('chalk');
console.log(chalk.default.green('OK'));
```

```bash
node index.js
```

```text
file:///home/user/my-cli-tool/index.js:1
const chalk = await import('chalk');
              ^^^^^

SyntaxError: await is only valid in async functions and the top level body of modules
```

Top-level `await` isn't valid in a CommonJS file, so I would have had to wrap the whole entry point in an `async function main() {}`. That's manageable for a single entry point, but this CLI called `chalk` from several files scattered across the codebase, so the rewrite cost wasn't worth it for what should have been a routine dependency bump.

### 2. Practical fix: pin chalk to the last CommonJS-compatible version

`chalk` v4.x is the last major version line that still ships as CommonJS. I pinned it there explicitly.

```bash
npm install chalk@4.1.2 --save-exact
```

```text
added 1 package, and audited 43 packages in 1s
```

```bash
grep '"chalk"' package.json
```

```text
"chalk": "4.1.2",
```

I used an exact pin instead of a caret range for two reasons: to avoid an accidental behavior change from a `4.x` minor bump, and to stop `npm update` from silently pulling v5 back in later.

### 3. Revert the test edit

I reverted `index.js` back to the original `require()` call before verifying.

```js
const chalk = require('chalk');
console.log(chalk.green('OK'));
```

## Verification

```bash
node index.js
```

```text
OK
```

Colored output came back exactly as it worked before the upgrade. I also confirmed the pinned version with `npm ls`.

```bash
npm ls chalk
```

```text
my-cli-tool@1.0.0 /home/user/my-cli-tool
└── chalk@4.1.2
```

## Preventing This Next Time

Since then, before bumping any dependency past a major version, I check its changelog for an ESM migration note, and I run `npm info <package> type` (if the field is missing, `npm info` just prints nothing, which itself is a hint) to see whether the currently published version already ships as `"type": "module"`. It's a five-second check that would have caught this before it ever hit `node_modules`. I also added `--save-exact` to how I upgrade single dependencies going forward, since a caret range on a package that ships frequent major bumps (as `chalk` does) makes it too easy for a future `npm update` to reintroduce the same break silently.

## Summary

- `Error [ERR_REQUIRE_ESM]` means Node.js tried to `require()` a package that is now pure ESM. Nothing about the install is broken; it's a module-format mismatch, not a corrupted dependency.
- You can confirm a package switched to ESM by opening `node_modules/<package>/package.json` and checking for `"type": "module"`. `npm install` won't warn you about this, since it doesn't validate module-format compatibility, only version ranges.
- There are three durable fixes: (1) convert the calling code to `async` and use dynamic `import()`, (2) pin the dependency to the last version that still supports CommonJS, or (3) migrate your own project to `"type": "module"` and go full ESM. For a small CLI with `require()` calls spread across multiple files, pinning the old version was the least disruptive option. For a larger codebase, migrating to ESM outright tends to pay off sooner.

## Related Articles

- [Fix: npm install ERESOLVE Dependency Resolution Error](/en/npm-eresolve-error)
- [Managing Node.js Versions with nvm](/en/node-version-management-nvm)
- [npm vs yarn: Key Differences and When to Use Each](/en/npm-vs-yarn)
- [Using package.json Scripts Effectively](/en/npm-package-json-scripts)
- [Fixing Node.js Heap Out of Memory Errors](/en/node-heap-out-of-memory)
