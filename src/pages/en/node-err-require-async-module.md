---
title: 'Fix: Node.js 22 require() Throws ERR_REQUIRE_ASYNC_MODULE'
date: '2026-09-09'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'On Node.js 22, a CommonJS require() call starts failing with Error [ERR_REQUIRE_ASYNC_MODULE] when loading an internal package. Here is the cause and how to fix it by switching to dynamic import().'
en_tags: ['Node.js', 'ERR_REQUIRE_ASYNC_MODULE', 'ESM']
---

## What I Was Trying to Do

Our internal batch script `report-batch` is plain old CommonJS (no `"type": "module"` in `package.json`) and loads a shared utility from our internal package `@internal/word-wrap` with `require()`.

```js
const { wrap } = require('word-wrap');
console.log(wrap('hello'));
```

This worked fine on Node.js 20. Right after we bumped the CI runner image to Node.js 22, the exact same code started throwing.

```text
node:internal/modules/esm/module_job:450
      throw new ERR_REQUIRE_ASYNC_MODULE(filename, parentFilename);
      ^

Error [ERR_REQUIRE_ASYNC_MODULE]: require() cannot be used on an ESM graph with top-level await. Use import() instead. To see where the top-level await comes from, use --experimental-print-required-tla.
  From /app/index.js
  Requiring /app/node_modules/word-wrap/index.js
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

The dependency itself hadn't changed in months, so the first clue was that only the Node.js version had moved. I'd seen `ERR_REQUIRE_ESM` before, but `ERR_REQUIRE_ASYNC_MODULE` was new to me, and my first guess was that the internal package itself was broken.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Package involved: `word-wrap` (an internal ESM-only package, `"type": "module"` in its `package.json`)
- Caller: a CommonJS batch script `index.js` (no `"type": "module"`, loaded via `require()`)

## What I Tried

First I checked whether the dependency itself was broken by looking at its `package.json`.

```json
{
  "name": "word-wrap",
  "version": "2.0.0",
  "type": "module",
  "main": "index.js"
}
```

Nothing unusual — just `"type": "module"`. Next I looked at the actual `index.js` inside the package.

```js
await Promise.resolve();
export function wrap(str) {
  return str;
}
```

There's a top-level `await` at the very top of the file. That's when the two clues — "Node 20 to 22" and "top-level await" — connected. Node.js 22 enables synchronous loading of ESM modules from `require()` (require(esm)) by default. Before this, requiring an ESM module immediately threw `ERR_REQUIRE_ESM`. On Node.js 22, an ESM module without top-level await can now be `require()`-d directly and just works. But this particular package does use top-level await, which a synchronous `require()` can never satisfy — hence the different error, `ERR_REQUIRE_ASYNC_MODULE`.

To confirm exactly where the top-level await was coming from, rather than guessing, I used the debug flag Node.js itself suggests in the error message.

```bash
node --experimental-print-required-tla index.js
```

```text
Error: unexpected top-level await at file:///app/node_modules/word-wrap/index.js:1
await Promise.resolve();
^
```

That confirmed the exact file and line, instead of relying on assumption.

## Root Cause

Node.js 22 enables "require(esm)" by default: `require()` can now load a target module as ESM synchronously. This means many cases that used to be immediately rejected with `ERR_REQUIRE_ESM` — requiring a plain ESM module — now just work.

But this synchronous load has a hard limit. `require()` is inherently synchronous, so it cannot `await` a Promise while evaluating the target module. If an ESM module has a top-level `await`, that module can only ever be evaluated asynchronously. When Node.js detects this, instead of forcing the require to succeed, it throws `ERR_REQUIRE_ASYNC_MODULE` and stops.

So in this case, neither the dependency nor the CI environment was actually broken. The real cause was a behavior change in Node.js itself: require(esm) being enabled on Node.js 22 turned a single, uniform `ERR_REQUIRE_ESM` failure mode into a split behavior that depends on whether the target module uses top-level await.

## How I Fixed It

### 1. Switch the caller to dynamic import

`require()` is synchronous and can never load an ESM module with top-level await, but `import()` (dynamic import) returns a Promise and handles it fine. I made the calling function `async` and replaced `require` with `await import()`.

```js
async function main() {
  const { wrap } = await import('word-wrap');
  console.log(wrap('hello'));
}
main();
```

### 2. Run it to confirm

```bash
node index.js
```

```text
hello
```

No exception, correct output.

### 3. Keep the debugging trick around for next time

I added `--experimental-print-required-tla` to our team runbook for future occurrences of this error.

```bash
node --experimental-print-required-tla <entry-file>
```

Running with this flag tells you exactly which file and line has the top-level await inside the ESM module being required. The `Requiring` line in the stack trace alone only points at the dependency's entry file, so this flag was what actually let us pinpoint the real await call.

## Verify It Works

I reconfirmed the failure reproduces with the original `require()` version, then confirmed the `import()`-based version runs cleanly.

```bash
node index.js
```

```text
hello
```

The same fix also ran cleanly on the CI runner's Node.js 22 image, and the pipeline was back to green.

## Takeaways

- Node.js 22 enables "require(esm)" by default, so `require()` can now synchronously load ESM modules — the failure mode is different from what you might remember from older Node.js versions.
- If the target ESM module has a top-level `await`, `require()` fundamentally cannot handle it and fails with `ERR_REQUIRE_ASYNC_MODULE`. This isn't a broken dependency or a broken upgrade — it's Node.js correctly refusing an impossible synchronous load.
- The most reliable fix is switching the caller to `await import()`. To find exactly where the top-level await lives, use `node --experimental-print-required-tla`.

## FAQ

**Q: What's the difference between `ERR_REQUIRE_ESM` and `ERR_REQUIRE_ASYNC_MODULE`?**
`ERR_REQUIRE_ESM` is thrown on older Node.js versions without require(esm), for any attempt to `require()` an ESM module at all. `ERR_REQUIRE_ASYNC_MODULE` is a narrower error on Node.js 22+ with require(esm): the ESM module itself can be loaded, but not synchronously, because it has a top-level await.

**Q: Would converting my own project to ESM avoid this entirely?**
Yes. If the calling `package.json` has `"type": "module"` and you use `import` instead of `require`, you never go through the synchronous require(esm) path, so `ERR_REQUIRE_ASYNC_MODULE` can't occur. We didn't do a full ESM migration here because it would touch other CommonJS-dependent code, so we scoped the fix to just the calling module.

**Q: Would downgrading back to Node.js 20 fix it?**
Yes, since require(esm)'s synchronous loading isn't enabled by default on Node.js 20, so the old behavior returns. But that's not a real fix — the same problem would resurface the next time we upgrade past 22, so we prioritized fixing the call site instead.

## Related Articles

- [Fix: ERESOLVE Error During npm install](/en/npm-eresolve-error)
- [Node.js JavaScript Heap Out of Memory: Cause and Fix](/en/node-heap-out-of-memory)
- [Switching Node.js Versions with nvm](/en/node-version-management-nvm)
- [Fix: git clone Leaves Submodule Directories Empty and Breaks the Build](/en/git-submodule-not-initialized)
