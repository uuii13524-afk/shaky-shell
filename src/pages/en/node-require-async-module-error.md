---
title: 'Fix: ERR_REQUIRE_ASYNC_MODULE When require()-ing an ESM Package (Node.js 22)'
date: '2026-09-05'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'On Node.js 22, require()-ing an ESM package can suddenly fail with "require() cannot be used on an ESM graph with top-level await." Here is the cause and how to fix it with dynamic import().'
en_tags: ['Node.js', 'ESM', 'require']
---

## What I Was Trying to Do

Our internal build script, `build.js`, has been plain CommonJS (`require()`) for years. I upgraded an internal helper package it depends on, `async-esm-utils`, so it could load its config asynchronously, and converted it to an ESM package (`"type": "module"` in its `package.json`).

```bash
node build.js
```

The `require()` call that had worked fine for years suddenly started throwing.

```text
node:internal/modules/esm/module_job:450
      throw new ERR_REQUIRE_ASYNC_MODULE(filename, parentFilename);
      ^

Error [ERR_REQUIRE_ASYNC_MODULE]: require() cannot be used on an ESM graph with top-level await. Use import() instead. To see where the top-level await comes from, use --experimental-print-required-tla.
  From /work/esm-repro2/build.js
  Requiring /work/esm-repro2/node_modules/async-esm-utils/index.js
    at ModuleJobSync.runSync (node:internal/modules/esm/module_job:450:13)
    at ModuleLoader.importSyncForRequire (node:internal/modules/esm/loader:435:47)
    at loadESMFromCJS (node:internal/modules/cjs/loader:1536:24)
    at Module._compile (node:internal/modules/cjs/loader:1687:5)
    at Object..js (node:internal/modules/cjs/loader:1838:10)
    at Module.load (node:internal/modules/cjs/loader:1441:32)
    at Function._load (node:internal/modules/cjs/loader:1263:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:237:24)
    at Module.require (node:internal/modules/cjs/loader:1463:12) {
  code: 'ERR_REQUIRE_ASYNC_MODULE'
}
```

What made this confusing is that the exact same `require('async-esm-utils')` line had worked without any error on the previous version of the package (before it had top-level await). This happened right around the same time we upgraded Node.js from 18 to 22, so my first guess was that the Node upgrade itself was the cause.

## Environment

- OS: Ubuntu 22.04.4 (a build container)
- Node.js: v22.22.2
- npm: 10.9.7
- Caller: `build.js` (CommonJS, uses `require()`)
- Dependency: `async-esm-utils` (internal package, `"type": "module"` in `package.json`, top-level await at the top of `index.js`)

## What I Tried

My first move was to check whether rolling Node.js back to 18 would fix it, so I switched with `nvm` and ran the same code.

```bash
nvm use 18
node build.js
```

```text
Error [ERR_REQUIRE_ESM]: require() of ES Module /work/esm-repro2/node_modules/async-esm-utils/index.js from /work/esm-repro2/build.js not supported.
Instead change the require of index.js in /work/esm-repro2/build.js to a dynamic import() which is available in all CommonJS modules.
```

On Node 18 it failed with a *different* error, `ERR_REQUIRE_ESM`. In other words: on Node 18, `require()`-ing an ESM module was never possible at all, while on Node 22, `require()` actually succeeds in some cases (as long as there's no top-level await). That's when I realized Node 22 had partially added support for `require()`-ing ESM from CommonJS, but async ESM (with top-level await) is still off-limits for `require()`.

To be sure, I also confirmed the same failure with a minimal version of `async-esm-utils` stripped down to just the top-level await.

```bash
node -e "console.log(process.version, process.features.require_module)"
```

```text
v22.22.2 [Getter]
```

The mere presence of a `process.features.require_module` getter was a clue that Node 22 has the `require(esm)` feature enabled at all.

I also re-ran with the `--experimental-print-required-tla` flag mentioned in the error message, to see exactly which line was flagged as top-level await.

```bash
node --experimental-print-required-tla build.js
```

```text
Error: unexpected top-level await at file:///work/esm-repro2/node_modules/async-esm-utils/index.js:1
const config = await Promise.resolve({ env: 'production' });
               ^
```

That confirmed it: line 1 of `index.js`, `await Promise.resolve(...)`, was being detected as the top-level await.

## Root Cause

Starting in Node.js 22.12, `require()` can load ESM modules from CommonJS synchronously (the `require(esm)` feature). But this only works when the module's evaluation can complete synchronously. If the ESM module contains top-level await, its evaluation becomes asynchronous (it goes through a Promise), which is incompatible with the synchronous semantics `require()` requires. So Node 22 explicitly rejects `require()`-ing an ESM module that has top-level await, and tells you to use `import()` instead, via `ERR_REQUIRE_ASYNC_MODULE`.

In this case, the direct cause was the version bump to `async-esm-utils`, which added top-level await to its config-loading code. The Node 18 → 22 upgrade wasn't entirely unrelated — it's what made `require()` succeed at all for non-async ESM — but the actual root cause wasn't the Node version, it was that the required ESM module had gained top-level await.

## How I Fixed It

### 1. Switch the caller from require() to dynamic import()

I turned the top of `build.js` into an async function and replaced `require()` with `await import()`.

```javascript
// Before
const { getEnv } = require('async-esm-utils');
console.log(getEnv());
```

```javascript
// After
async function main() {
  const { getEnv } = await import('async-esm-utils');
  console.log(getEnv());
}

main();
```

### 2. Verify it works

```bash
node build.js
```

```text
production
```

No error, and the config value `production`, loaded via the top-level await inside `async-esm-utils`, printed correctly.

### 3. An alternative if you must stay CommonJS

If `build.js` genuinely cannot become async, another option is asking the dependency to drop the top-level await (e.g. moving initialization into a synchronous function, or an explicit async `init()` function you call separately). In our case switching the caller to `import()` had no downside, so that's what we went with.

## Verify It Works

Just to be thorough, I checked that the same `import()`-based `build.js` also runs correctly on Node 18.

```bash
nvm use 18
node build.js
```

```text
production
```

Same result on both Node 18 and Node 22. Dynamic `import()` is always available from CommonJS modules regardless of Node version or how `require()` happens to behave, so it isn't affected by this difference at all.

## Takeaways

- Since Node.js 22.12, `require()` can load ESM modules, but only ones that evaluate synchronously.
- If the ESM module has top-level await, `require()` explicitly rejects it with `ERR_REQUIRE_ASYNC_MODULE`. Following the error message's advice and switching to `import()` fixes it.
- If something that used to `require()` fine suddenly breaks, don't assume it's purely a Node version difference — check whether the required dependency itself gained top-level await. The `--experimental-print-required-tla` flag pinpoints exactly which line triggered it.

## FAQ

**Q: What's the difference between `ERR_REQUIRE_ESM` and `ERR_REQUIRE_ASYNC_MODULE`?**
`ERR_REQUIRE_ESM` is thrown on Node versions before 20.19/22.12, whenever CommonJS tries to `require()` any ESM module at all. `ERR_REQUIRE_ASYNC_MODULE` only shows up on Node 22.12+, after `require(esm)` support exists, and only when the specific ESM module being required contains top-level await and can't be evaluated synchronously.

**Q: Can I disable the `require(esm)` feature?**
Yes, with the `--no-experimental-require-module` flag. But disabling it reverts *all* ESM requires — including ones without top-level await — back to `ERR_REQUIRE_ESM`, so it isn't a real fix, just a rollback.

**Q: Does this happen with TypeScript builds too?**
Yes. If your compiler config still emits `require()` calls (e.g. `module: "commonjs"`), the same `ERR_REQUIRE_ASYNC_MODULE` shows up the moment a dependency you `require()` becomes an ESM module with top-level await. You'll need to revisit the `module` target in your build config too.

## Related Articles

- [Fix EADDRINUSE: Port Already in Use in Node.js](/en/node-eaddrinuse-port-fix)
- [Fix npm install ERESOLVE Errors](/en/npm-eresolve-error)
- [Switching Node.js Versions with nvm](/en/node-version-management-nvm)
- [Fix Node.js Heap Out of Memory Errors](/en/node-heap-out-of-memory)
- [Keeping a Node.js App Running with pm2](/en/node-pm2-setup)
