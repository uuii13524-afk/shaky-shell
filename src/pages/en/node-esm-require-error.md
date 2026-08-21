---
title: 'Fix: ERR_REQUIRE_ESM When require()-ing chalk v5 on Node.js 20'
date: '2026-08-21'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Right after upgrading chalk to v5, existing code calling require("chalk") crashes with Error [ERR_REQUIRE_ESM]. Here is the cause and how to fix it, from checking package.json exports to pinning a CommonJS-compatible version.'
en_tags: ['Node.js', 'ESM', 'ERR_REQUIRE_ESM']
---

## What I Was Trying to Do

Our internal CLI tool `deploy-notifier` used `chalk` to color terminal output. While auditing dependencies with `npm outdated`, I saw `chalk` could jump from `4.1.2` to `5.3.0`, so I updated it along with a batch of other dependencies.

```bash
npm install chalk@latest
node bin/deploy-notifier.js --env staging
```

The script had been working fine before the update. Right after updating, it crashed immediately.

```text
node:internal/modules/cjs/loader:1105
  throw new ERR_REQUIRE_ESM(filename, parentPath, packageJsonPath);
  ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/deploy-notifier/node_modules/chalk/source/index.js from /home/user/deploy-notifier/bin/deploy-notifier.js not supported.
Instead change the require of index.js in /home/user/deploy-notifier/bin/deploy-notifier.js to a dynamic import() which is available in all CommonJS modules.
    at Object.<anonymous> (/home/user/deploy-notifier/bin/deploy-notifier.js:3:16) {
  code: 'ERR_REQUIRE_ESM'
}

Node.js v20.14.0
```

My first guess was that `npm install` had left `node_modules` in a half-finished state, so I deleted it and reinstalled.

## Environment

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- Package in question: `chalk` 4.1.2 → 5.3.0 (upgrade)
- Caller: a CommonJS script (`bin/deploy-notifier.js`, loading modules with `require()`)

## What I Tried

First I suspected `node_modules` itself and did a clean install.

```bash
rm -rf node_modules package-lock.json
npm install
node bin/deploy-notifier.js --env staging
```

```text
Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/deploy-notifier/node_modules/chalk/source/index.js from /home/user/deploy-notifier/bin/deploy-notifier.js not supported.
```

Same error. So it wasn't a broken `node_modules`. Next I suspected the `chalk` version and checked what `package.json` actually specified.

```bash
cat package.json | grep chalk
```

```text
    "chalk": "^5.3.0",
```

I realized `npm install chalk@latest` had silently bumped a major version. Checking chalk's release notes confirmed that v5 dropped CommonJS support entirely and became a pure ESM (ECMAScript Modules) package.

Just to be thorough, I also checked chalk's own `exports` field.

```bash
cat node_modules/chalk/package.json | grep -A3 '"exports"'
```

```text
  "exports": {
    "types": "./index.d.ts",
    "default": "./source/index.js"
  },
```

There was no `"require"` entry at all — only a `"default"` pointing at an ESM-only source file. That confirmed `require("chalk")` couldn't possibly work anymore.

## Root Cause

`chalk` moved to a pure ESM-only package starting with v5.0.0. Since CommonJS's `require()` has no way to synchronously load an ESM module, Node.js throws `ERR_REQUIRE_ESM` whenever `require()` is used to load an ESM-only package.

This project's `package.json` doesn't set `"type": "module"`, so `bin/deploy-notifier.js` itself is interpreted as CommonJS. When `require("chalk")` runs inside a CommonJS file, Node's module loader checks chalk's `exports` field, finds no CommonJS entry point, and immediately throws.

`npm install chalk@latest` installs whatever npm considers the latest version regardless of major-version boundaries, unless a range like `^4.1.2` is already pinned. In this case, updating manually while skimming the `npm outdated` list, I crossed that major-version boundary without noticing.

## How I Fixed It

### 1. Check the version boundary

```bash
npm view chalk versions --json | tail -20
```

```text
  "5.1.2",
  "5.2.0",
  "5.3.0"
]
```

I confirmed v5 was indeed the latest line, then decided whether to keep using CommonJS or migrate the whole tool to ESM. Since this CLI tool wasn't large enough to justify a full ESM migration, I chose to pin `chalk` to the last CommonJS-compatible major version instead.

### 2. Pin chalk to the v4 line, which still supports CommonJS

```bash
npm install chalk@^4.1.2
```

```text
added 1 package, and audited 154 packages in 2s
```

### 3. Confirm the pinned version in package.json

```bash
cat package.json | grep chalk
```

```text
    "chalk": "^4.1.2",
```

Confirmed the range no longer allows `^5`.

### 4. Re-run to verify

```bash
node bin/deploy-notifier.js --env staging
```

```text
[deploy-notifier] deployment notification sent for staging
```

It started without errors, and the colored output rendered correctly.

## Verify It Works

To double-check module resolution directly, I loaded it from the Node REPL.

```bash
node -e "console.log(require('chalk').green('OK'))"
```

```text
OK
```

(rendered in green in the terminal)

Confirmed that chalk's CommonJS entry point resolves without error.

## Takeaways

- Starting with v5.0.0, `chalk` has no CommonJS entry in its `exports` field and is pure ESM only. Projects that load it with `require()` need to pin a major version explicitly, such as `^4.1.2`.
- When you hit `ERR_REQUIRE_ESM`, the reliable first check is `node_modules/<package>/package.json`'s `exports` field — look for whether a `"require"` key exists.
- If you want to follow an ESM-only package long term, you need to either rename the caller file to `.mjs` or set `"type": "module"` in `package.json`, and rewrite `require()` calls to dynamic `import()`. In this case, ESM-migrating the whole CLI tool wasn't worth the cost, so I kept the dependency pinned to a CommonJS-compatible version instead.

## FAQ

**Q: If I run `npm install chalk@latest` again without specifying a version, will this happen again?**
Yes. `@latest` ignores major-version boundaries and installs whatever is newest, even if `package.json` already pins `^4.1.2` — an explicit `@latest` on the command line overrides that range. After pinning, it's worth checking `npm outdated` periodically to catch unintended major bumps.

**Q: Is there any way to keep using CommonJS besides rewriting `require()` to `import()`?**
Yes. Pinning the package to its last CommonJS-compatible major version, as done here, is the fastest fix. That pinned version won't receive further security updates though, so an eventual ESM migration is worth considering for the long term.

**Q: Does this happen with other packages too?**
Yes. Several widely used packages dropped CommonJS support and went ESM-only, including `node-fetch` v3 and `execa` v6. Before upgrading, it's worth checking the target package's changelog for phrases like "ESM only" or "Pure ESM package."

## Related Articles

- [Fix: Node.js Heap Out of Memory Errors](/en/node-heap-out-of-memory)
- [Switching Node.js Versions with nvm: The Basics](/en/node-version-management-nvm)
- [Fix: npm install ERESOLVE Error](/en/npm-eresolve-error)
- [When and How to Use npm cache clear](/en/npm-cache-clear)
- [A Guide to package.json Scripts](/en/npm-package-json-scripts)
