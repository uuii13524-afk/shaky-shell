---
title: 'Fix: ERR_PACKAGE_PATH_NOT_EXPORTED After Adding "exports" to package.json'
date: '2026-09-13'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Adding an "exports" field to a shared internal package suddenly breaks existing deep imports with Error [ERR_PACKAGE_PATH_NOT_EXPORTED]. Here is why it happens and how to fix it by re-exporting from the entry point.'
en_tags: ['Node.js', 'npm', 'exports', 'module resolution']
---

## What I Was Trying to Do

We have an internal shared utility package, `@internal/date-utils`, used across several repos. As prep for ESM support, I added an `exports` field to its `package.json` to make the public API explicit. I assumed the entry point import (`require("@internal/date-utils")`) would keep working exactly as before.

Instead, CI in a completely different project, `batch-report`, which depends on this package, started failing right after the change shipped.

```bash
npm run build
```

```text
node:internal/modules/cjs/loader:657
      throw e;
      ^

Error [ERR_PACKAGE_PATH_NOT_EXPORTED]: Package subpath './lib/format.js' is not defined by "exports" in /workspace/batch-report/node_modules/@internal/date-utils/package.json
    at exportsNotFound (node:internal/modules/esm/resolve:314:10)
    at packageExportsResolve (node:internal/modules/esm/resolve:661:9)
    at resolveExports (node:internal/modules/cjs/loader:650:36)
    at Function._findPath (node:internal/modules/cjs/loader:717:31)
    at Function._resolveFilename (node:internal/modules/cjs/loader:1369:27)
    at defaultResolveImpl (node:internal/modules/cjs/loader:1025:19)
    at resolveForCJSWithHooks (node:internal/modules/cjs/loader:1030:22)
    at Function._load (node:internal/modules/cjs/loader:1192:37)
    code: 'ERR_PACKAGE_PATH_NOT_EXPORTED'
}
```

I hadn't touched the package's actual code, only added `exports`, and the entry point import still worked fine locally. So my first instinct was that `batch-report`'s `node_modules` was somehow corrupted, not that adding `exports` was the actual cause.

## Environment

- OS: Ubuntu 24.04 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Internal package: `@internal/date-utils` (a local monorepo package, consumed via a `file:` reference from other projects)
- Consuming project: `batch-report` (CommonJS, loads modules with `require`)

## What I Tried

First I suspected a stale `node_modules` cache and tried a clean install.

```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

Same `ERR_PACKAGE_PATH_NOT_EXPORTED` error. That ruled out a caching or dependency-resolution issue.

Next I grepped for every place that imports `./lib/format.js` directly instead of the package's entry point.

```bash
grep -rn "date-utils/lib/format" src/
```

```text
src/reports/monthly.js:3:const { formatJst } = require("@internal/date-utils/lib/format.js");
src/reports/weekly.js:5:const { formatJst } = require("@internal/date-utils/lib/format.js");
```

Two files were requiring the package's internal `lib/format.js` file directly instead of going through the public entry point (`require("@internal/date-utils")`). This dated back to an earlier version of the package that didn't expose `formatJst` from its public API, so someone had reached into the internal file as a workaround.

Checking `@internal/date-utils`'s own `package.json` confirmed it:

```json
{
  "name": "@internal/date-utils",
  "version": "2.0.0",
  "main": "index.js",
  "exports": {
    ".": "./index.js"
  }
}
```

`exports` only defined the entry point (`.`) — no subpath like `./lib/format.js` was allowed at all.

## Root Cause

Once a `package.json` has an `exports` field, Node's module resolution blocks direct access to anything not explicitly listed there. Before I added `exports`, any file inside the package could be reached with `require("pkg/any/internal/file.js")` — not because it was an intended public API, but simply because Node's resolution rules happened to allow it when no `exports` map existed.

Adding the `exports` field closed off that accidental path entirely. Since I had only listed `"."` in `exports`, any direct access to an internal path like `./lib/format.js` now gets rejected with `ERR_PACKAGE_PATH_NOT_EXPORTED`.

I thought I hadn't changed the package's public surface, but adding `exports` was itself a breaking change — it closed off a previously-working, unofficial internal path that other code depended on.

## How I Fixed It

### 1. Find every place reaching into the internal path

```bash
grep -rn "date-utils/lib/" --include="*.js" .
```

```text
src/reports/monthly.js:3:const { formatJst } = require("@internal/date-utils/lib/format.js");
src/reports/weekly.js:5:const { formatJst } = require("@internal/date-utils/lib/format.js");
```

Confirmed only two files were affected.

### 2. Proper fix: re-export from the entry point

The real issue was that `@internal/date-utils`'s public API never included `formatJst`. I fixed that by re-exporting it from the entry point.

```js
// @internal/date-utils/index.js
const { formatJst } = require("./lib/format.js");

module.exports = {
  // ...existing exports
  formatJst,
};
```

### 3. Update the consuming code to import from the entry point

```js
// Before
const { formatJst } = require("@internal/date-utils/lib/format.js");

// After
const { formatJst } = require("@internal/date-utils");
```

Updated both `monthly.js` and `weekly.js`.

### 4. A stopgap: adding the subpath to exports directly

If the consuming code can't be updated right away, another option is to explicitly list the subpath in `exports`.

```json
{
  "name": "@internal/date-utils",
  "version": "2.0.1",
  "main": "index.js",
  "exports": {
    ".": "./index.js",
    "./lib/format.js": "./lib/format.js"
  }
}
```

This locks an internal implementation file into the public API, though, so I went with the proper fix (steps 2 and 3) instead and didn't use this.

### 5. Reinstall and rebuild

```bash
npm install
npm run build
```

```text
> batch-report@1.0.0 build
> node scripts/build.js

Build completed successfully.
```

The build completed without errors.

## Verify It Works

I loaded the module directly with `node -e` to confirm the error was gone.

```bash
node -e "const { formatJst } = require('@internal/date-utils'); console.log(formatJst(new Date('2026-09-13T00:00:00Z')))"
```

```text
2026-09-13 09:00:00
```

`formatJst` resolved correctly through the intended public API. I also grepped the other consuming projects to make sure no other internal-path imports were left.

```bash
grep -rn "date-utils/lib" --include="*.js" ../*/src 2>/dev/null || echo "no direct internal-path imports remain"
```

```text
no direct internal-path imports remain
```

## Takeaways

- Once a `package.json` defines `exports`, any path not listed there is rejected with `ERR_PACKAGE_PATH_NOT_EXPORTED`. Direct access to internal files that weren't part of `main` used to work purely as an accident of Node's resolution rules — adding `exports` closes that gap.
- If code elsewhere is reaching into internal paths because the public API was missing something, adding `exports` will break all of that at once. Grep for direct internal-path imports first, then re-export the needed functions from the entry point as the proper fix.
- If you can't update the consuming code immediately, listing the subpath explicitly in `exports` keeps things working temporarily — but it locks in an internal file as part of the public API, so treat it as a stopgap on the way to the real fix.

## FAQ

**Q: Does this happen to packages that only have `main`, with no `exports` field?**
No. Without an `exports` field, Node still allows requiring any file path inside the package, exactly as before. The restriction only kicks in once `exports` is defined.

**Q: Could I just use a wildcard like `"./*": "./*.js"` in exports to avoid this?**
Technically yes, but that defeats most of the point of adding `exports` in the first place — making the public API explicit and preventing consumers from depending on internal implementation details. Finding the call sites and switching them to the real entry point keeps more freedom to refactor internals later.

**Q: Is this specific to CommonJS (`require`), or does it also happen with ESM (`import`)?**
It happens the same way with `import`. The `exports` field governs module resolution itself, regardless of whether the consumer uses `require` or `import` — any subpath not listed is rejected either way.

## Related Articles

- [Fix the npm ERESOLVE Error](/en/npm-eresolve-error)
- [Switch Node.js Versions with nvm](/en/node-version-management-nvm)
- [How to Write package.json Scripts](/en/npm-package-json-scripts)
- [Cache node_modules in GitHub Actions](/en/github-actions-node-cache)
- [Fix Node.js "JavaScript heap out of memory"](/en/node-heap-out-of-memory)
