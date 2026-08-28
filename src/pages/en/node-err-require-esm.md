---
title: 'Fix: "Error [ERR_REQUIRE_ESM]: require() of ES Module ... not supported" in Node.js'
date: '2026-08-28'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'requiring chalk in a CommonJS Node.js project throws "Error [ERR_REQUIRE_ESM]" and the process fails to start. Here is how to confirm the package went ESM-only, and two ways to fix it: migrating to import or pinning an older version.'
en_tags: ['Node.js', 'ERR_REQUIRE_ESM', 'ESM', 'CommonJS', 'chalk']
---

## What I Was Trying to Do

I was writing an internal CLI for deploy notifications and wanted colored terminal output, so I reached for the usual `chalk`.

```bash
npm install chalk
```

The `package.json` had no `"type"` field, meaning it defaulted to CommonJS. I loaded it the same way I always had.

```js
// notify.js
const chalk = require('chalk');

console.log(chalk.green('Deploy finished'));
```

```bash
node notify.js
```

That should have been it. Instead it crashed immediately.

```text
node:internal/modules/cjs/loader:1105
    throw err;
    ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/deploy-cli/node_modules/chalk/source/index.js from /home/user/deploy-cli/notify.js not supported.
Instead change the require of index.js in /home/user/deploy-cli/notify.js to a dynamic import() which is available in all CommonJS modules.
    at Object.<anonymous> (/home/user/deploy-cli/notify.js:1:15) {
  code: 'ERR_REQUIRE_ESM'
}

Node.js v20.14.0
```

I've used `chalk` more times than I can count, so my first guess was a typo somewhere in my own code.

## Environment

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- Package added: `chalk` 5.3.0 (whatever `npm install chalk` pulls in right now)
- `package.json`: no `"type"` field (default CommonJS)

## What I Tried

First I checked whether `require('chalk')` was even resolving — whether `node_modules/chalk` existed at all.

```bash
ls node_modules/chalk
```

```text
license  package.json  readme.md  source
```

The directory was there, so it wasn't a path typo. Next I copied over code from an older project that I knew used `chalk` successfully, and it hit the exact same error. Since that code had worked before, I stopped suspecting my own code and started suspecting `chalk` itself.

```bash
npm ls chalk
```

```text
deploy-cli@1.0.0 /home/user/deploy-cli
└── chalk@5.3.0
```

Looking back at the `package-lock.json` from that older project, it had `chalk@4.1.2` pinned. That's when I noticed the major version had jumped from 4 to 5, so I checked `chalk`'s own `package.json`.

```bash
cat node_modules/chalk/package.json
```

```json
{
  "name": "chalk",
  "version": "5.3.0",
  "type": "module",
  "exports": "./source/index.js",
  "main": "./source/index.js"
}
```

`"type": "module"` was set, and the entry point referenced by `"main"` was itself an ESM file. There was no CommonJS branch in `"exports"`, no `.cjs` file anywhere. That confirmed it: `chalk` had become ESM-only starting at v5.

## Root Cause

Starting at v5, `chalk` stopped shipping a CommonJS build and became a pure ESM package. Node's `require()` can only load CommonJS modules. When a module's `package.json` declares `"type": "module"`, Node treats it as an ES Module — and ES Modules can't be loaded synchronously through `require()`, because resolving them can involve asynchronous top-level work. That's exactly what `ERR_REQUIRE_ESM` reports.

The error message itself points at the fix: it says to switch the `require` to a dynamic `import()`, which is accurate — a CommonJS file can still load an ESM-only package through `import()` (which returns a Promise), just not through a synchronous `require()`. Put differently, pinning `chalk` to any version 5 or later won't help as long as the call site stays a static `require('chalk')`.

## How I Fixed It

I compared two options and ended up moving the whole project to ESM.

### Option 1 (what I used): switch the project to ESM

I added `"type": "module"` to `package.json` and converted `require` calls to `import`.

```json
{
  "name": "deploy-cli",
  "version": "1.0.0",
  "type": "module"
}
```

```js
// notify.js
import chalk from 'chalk';

console.log(chalk.green('Deploy finished'));
```

```bash
node notify.js
```

```text
Deploy finished
```

(shown in green in an actual terminal)

There were three other homegrown modules still using `require()`, so I converted each one's `module.exports` to `export default` / `export const` and updated the corresponding `require` calls to `import`, then re-tested.

### Option 2 (not used here, noted for reference): pin chalk to v4

If migrating to ESM isn't practical for a project, pinning to the last CommonJS-compatible version is an alternative.

```bash
npm install chalk@4
```

```text
+ chalk@4.1.2
```

```js
const chalk = require('chalk'); // still works on chalk@4.x
console.log(chalk.green('Deploy finished'));
```

Worth noting: `chalk@4` hasn't received feature updates since 2021, so it may not get future security fixes either. Since this project was small and brand-new, I went with Option 1 instead.

## Verify It Works

After converting to ESM, I checked that no `require()` calls were left behind.

```bash
grep -rn "require(" *.js
```

```text
(no matches)
```

I also double-checked that `"type"` was actually being picked up.

```bash
node -e "console.log(require('./package.json').type)"
```

```text
module
```

I ran `node notify.js` a few more times and the colored log output came through consistently every time.

## Takeaways

- Node's `Error [ERR_REQUIRE_ESM]` fires when `require()` tries to load an ESM-only package. Check `cat node_modules/<pkg>/package.json` for `"type": "module"` to confirm that's the cause.
- `chalk` dropped CommonJS support starting at v5 and is now ESM-only. The same kind of change has hit other widely-used packages too (`node-fetch` from v3, `nanoid` from v4), so if code that used to work suddenly breaks after an update, checking the package's `"type"` field is a good first move.
- There are two real fixes. If the project can go ESM, add `"type": "module"` and switch to `import` for a permanent fix. If ESM migration isn't practical right now, pinning to the last CommonJS-compatible major version (`npm install <pkg>@<old-major>`) is a workable stopgap.

## FAQ

**Q: Can I keep some files as CommonJS and only convert others to ESM?**
Yes. Instead of setting `"type": "module"` project-wide, you can name the files you want as ESM with a `.mjs` extension. Files you want to keep as CommonJS can use `.cjs` — Node determines the module format from the file extension regardless of the `"type"` setting in that case.

**Q: Is there a way to use an ESM-only package while keeping `require()`?**
As the error message suggests, a dynamic `import()` works. But `import()` returns a Promise, so you can't assign it synchronously the way `require` does. You'd need something like `const chalk = (await import('chalk')).default;` inside an `async` function, which does require restructuring the CommonJS file somewhat.

**Q: Is there a way to check ahead of time which dependencies have gone ESM-only?**
Running `npm outdated` shows what's updatable, then checking each package's release notes or README for phrases like "ESM only" or "no longer supports require" before upgrading is the reliable way. For major version bumps specifically, checking the diff in `package.json` (a new `"type"` or `"exports"` field) via something like `npm view <pkg>@<new-version> type` ahead of time can catch this before it breaks anything.

## Related Articles

- [Fix "ERESOLVE" Dependency Resolution Errors in npm install](/en/npm-eresolve-error)
- [How to Manage a Node.js Process with pm2](/en/node-pm2-setup)
- [Switch and Manage Node.js Versions with nvm](/en/node-version-management-nvm)
- [npm vs yarn: Differences and When to Use Each](/en/npm-vs-yarn)
- [How to Write the scripts Field in package.json](/en/npm-package-json-scripts)
