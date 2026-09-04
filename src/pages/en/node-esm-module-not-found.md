---
title: 'Fix: ERR_MODULE_NOT_FOUND After Adding "type": "module" to package.json (Node.js 22)'
date: '2026-09-04'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'After adding "type": "module" to package.json and switching to import, an extension-less relative import throws Error [ERR_MODULE_NOT_FOUND]. Here is why Node.js 22 ESM resolution does not auto-append extensions the way require() does, and how to fix it.'
en_tags: ['Node.js', 'ESM', 'ERR_MODULE_NOT_FOUND']
---

## What I Was Trying to Do

I was migrating a small personal CLI tool from CommonJS (`require`/`exports`) to ESM (`import`/`export`). As a first step I added `"type": "module"` to `package.json` and replaced the `require` call in the entry point with `import`.

```json
{
  "name": "esm-ext-repro",
  "version": "1.0.0",
  "type": "module",
  "main": "index.js"
}
```

```js
import { formatDate } from './lib';

console.log(formatDate(new Date('2026-09-04')));
```

`lib.js` sat right next to `index.js` in the same directory. Back in the CommonJS days, `require('./lib')` had worked fine without an extension. I kept the same style and ran `node index.js`, expecting the same result. Instead it crashed immediately.

```text
node:internal/modules/run_main:123
    triggerUncaughtException(
    ^

Error [ERR_MODULE_NOT_FOUND]: Cannot find module '/path/to/esm-ext/lib' imported from /path/to/esm-ext/index.js
Did you mean to import "./lib.js"?
    at finalizeResolution (node:internal/modules/esm/resolve:275:11)
    at moduleResolve (node:internal/modules/esm/resolve:861:10)
    at defaultResolve (node:internal/modules/esm/resolve:985:11)
    at #cachedDefaultResolve (node:internal/modules/esm/loader:731:20)
    at ModuleLoader.resolve (node:internal/modules/esm/loader:708:38)
    at ModuleLoader.getModuleJobForImport (node:internal/modules/esm/loader:310:38)
    at ModuleJob._link (node:internal/modules/esm/module_job:182:49) {
  code: 'ERR_MODULE_NOT_FOUND',
  url: 'file:///path/to/esm-ext/lib'
}

Node.js v22.22.2
```

`lib.js` definitely existed at that path, and I couldn't find a typo in the import specifier. I didn't understand why simply switching `require` to `import` had made the module unresolvable.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Files involved: `package.json` (with `"type": "module"`), `index.js`, `lib.js` (all in the same directory)

## What I Tried

First I re-checked that the file existed and was named correctly.

```bash
ls -la
```

```text
-rw-r--r-- 1 user user  76 Sep  4 09:00 index.js
-rw-r--r-- 1 user user  98 Sep  4 09:00 lib.js
-rw-r--r-- 1 user user 108 Sep  4 09:00 package.json
```

`lib.js` was right there, and the import path (`./lib`) had no typo. Next, to isolate the variable, I reproduced the same extension-less `require('./lib')` in a plain CommonJS project (no `"type": "module"`) and confirmed it still worked.

```bash
# In a separate directory without "type": "module" in package.json
node index.js
```

```text
2026-09-04
```

The CommonJS version ran fine with the extension omitted. That ruled out "the file doesn't exist" and pointed instead at "`import` and `require` resolve relative paths differently." Reading the error message again, one line stood out: `Did you mean to import "./lib.js"?` — Node itself was suggesting the fix.

## Root Cause

Node's CommonJS loader (`require()`) has its own resolution algorithm for extension-less relative paths: it tries `.js`, then `.json`, then `.node` in order until it finds a match. That's a long-standing CommonJS convention, and it's the only reason `require('./lib')` was ever able to find `lib.js` without being told the extension.

`"type": "module"` in `package.json`, on the other hand, switches Node to its ESM (ECMAScript Modules) loader, which resolves relative specifiers according to the web-standard URL resolution algorithm instead. That algorithm does not auto-append extensions. So `import './lib'` is resolved literally as a file named `./lib`, which doesn't exist, and Node throws `ERR_MODULE_NOT_FOUND`. Switching to ESM isn't just a syntax change from `require` to `import` — it changes how module specifiers get resolved in the first place.

In this project several extension-less relative imports had accumulated over time, so adding `"type": "module"` broke all of them at once.

## How I Fixed It

### 1. Read the extension Node suggests in the error

```text
Did you mean to import "./lib.js"?
```

When the ESM loader fails to resolve an extension-less specifier, it checks whether a same-named file with a different extension exists and suggests it. In this case the suggestion was exactly the fix I needed.

### 2. Add the extension to the relative import

```js
import { formatDate } from './lib.js';

console.log(formatDate(new Date('2026-09-04')));
```

I changed `./lib` to `./lib.js`. Because ESM doesn't allow extension-less relative specifiers, every relative import and re-export in the codebase needs to follow this pattern.

### 3. Re-run to confirm the fix

```bash
node index.js
```

```text
2026-09-04
```

It ran without error, and `formatDate` returned the expected output.

### 4. Search for other extension-less imports

```bash
grep -rn "from '\./" --include="*.js" . | grep -v "\.js'"
```

This particular project had no other extension-less imports left, but in a larger project split across many files this pattern tends to hide in more than one place. Grepping for lines that start with `from './` and don't end in `.js'` is a reliable way to catch the rest mechanically.

## Verify It Works

As a final check, I ran the extension-less version and the extension-included version side by side — one under CommonJS, one under ESM — to confirm the difference in behavior.

```bash
# CommonJS (no "type" field): works without the extension
node cjs-check/index.js
```

```text
2026-09-04
```

```bash
# ESM ("type": "module"): fails without the extension, works with it
node esm-ext/index.js
```

```text
2026-09-04
```

The CommonJS version kept working with the extension omitted, and the ESM version only succeeded once the extension was explicit — confirming the two loaders really do resolve relative paths differently.

## Takeaways

- CommonJS `require()` auto-appends extensions, but Node's ESM loader (triggered by `"type": "module"`) does not. Relative imports need an explicit extension like `.js`.
- The `ERR_MODULE_NOT_FOUND` error usually suggests the correct path, e.g. `Did you mean to import "./lib.js"?` — check that first.
- Migrating an existing CommonJS project to ESM is more than swapping `require` for `import`. Grep for extension-less relative imports and fix them all up front to avoid hitting this error file by file.

## FAQ

**Q: Would using a `.mjs` extension let me skip the extension in imports?**
No. `.mjs` just tells Node to treat that specific file as ESM, the same way `"type": "module"` does for a whole directory. Either way, you're using the ESM loader, and the ESM loader never auto-appends extensions to relative imports.

**Q: Does this also happen when importing `.ts` files in a TypeScript project?**
If you're running through a loader like `ts-node` or `tsx`, that tool often has its own resolution logic and may not hit this error. But once you compile with `tsc` and run the resulting `.js` directly with plain Node, the same ESM resolution rules in this article apply — so make sure your `tsconfig.json` (`moduleResolution` and related settings) produces import paths with extensions in the compiled output.

**Q: If I remove `"type": "module"` from package.json, does extension-less resolution come back?**
Yes. Removing it, or setting `"type": "commonjs"`, switches `.js` files in that directory back to the CommonJS loader, restoring `require()`'s automatic extension resolution. But `import`/`export` syntax isn't valid under CommonJS, so you can't keep ESM syntax while reverting only the resolution rules.

## Related Articles

- [Manage Node.js Versions with nvm (Windows and Mac)](/en/node-version-management-nvm)
- [How to Fix npm ERESOLVE Dependency Tree Error](/en/npm-eresolve-error)
- [How to Fix "JavaScript Heap Out of Memory" in Node.js](/en/node-heap-out-of-memory)
- [How to Use package.json Scripts to Automate Tasks](/en/npm-package-json-scripts)
- [How to Keep Node.js Apps Running in Production with PM2](/en/node-pm2-setup)
