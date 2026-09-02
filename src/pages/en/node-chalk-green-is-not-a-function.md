---
title: 'Fix: "chalk.green is not a function" When require()-ing chalk on Node.js 22'
date: '2026-09-02'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'On Node.js 22, require("chalk") from CommonJS throws TypeError: chalk.green is not a function. Node''s native require(esm) interop returns the raw ESM namespace object instead of the default export, and here is how to fix it with .default.'
en_tags: ['Node.js', 'CommonJS', 'ESM', 'chalk']
---

## What I Was Trying to Do

I wanted to add `chalk` to an existing CommonJS script to colorize terminal output.

```bash
npm install chalk
```

The project's `package.json` had no `"type": "module"` field — just an ordinary CommonJS setup, same as always.

```js
// index.js
const chalk = require('chalk');
console.log(chalk.green('Hello, world!'));
```

```bash
node index.js
```

That tiny script threw a `TypeError` immediately.

```text
/tmp/esm-repro/index.js:2
console.log(chalk.green('Hello, world!'));
                  ^

TypeError: chalk.green is not a function
    at Object.<anonymous> (/tmp/esm-repro/index.js:2:19)
    at Module._compile (node:internal/modules/cjs/loader:1705:14)
    at Object..js (node:internal/modules/cjs/loader:1838:10)
    at Module.load (node:internal/modules/cjs/loader:1441:32)
    at Function._load (node:internal/modules/cjs/loader:1263:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:237:24)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:171:5)
    at node:internal/main/run_main_module:36:49

Node.js v22.22.2
```

I remembered that requiring an ESM-only package from CommonJS used to crash with `ERR_REQUIRE_ESM`, so I assumed that was the same class of problem. But this error was different: `require()` itself succeeded — the crash only happened once I tried to call `chalk.green`, which made the connection to an ESM/CJS mismatch far less obvious at first.

## Environment

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Package in question: chalk v6.0.0 (`"type": "module"` in its `package.json`, ESM-only, no CommonJS export condition)
- The consuming project itself has no `"type"` field — plain CommonJS

## What I Tried

Still assuming I was hitting `ERR_REQUIRE_ESM`, I checked chalk's own `package.json` first.

```bash
cat node_modules/chalk/package.json
```

```json
{
  "name": "chalk",
  "version": "6.0.0",
  "type": "module",
  "exports": {
    "types": "./source/index.d.ts",
    "default": "./source/index.js"
  },
  "engines": {
    "node": ">=22"
  }
}
```

It was indeed ESM-only (`"type": "module"`, no CommonJS export condition). But looking back at the actual crash output, there's no `ERR_REQUIRE_ESM` code anywhere — `require('chalk')` completed without error, and the `TypeError` only fired on the line that called `chalk.green`. That's when it clicked that `require` was succeeding, but returning something unexpected.

I checked exactly what `require('chalk')` was returning:

```bash
node -e "const chalk = require('chalk'); console.log(chalk); console.log(Object.keys(chalk));"
```

```text
[Module: null prototype] {
  Chalk: [class Chalk],
  __esModule: true,
  backgroundColorNames: [ 'bgBlack', 'bgRed', ... ],
  chalkStderr: [Function: chalk] createChalk { [Symbol(LEVEL)]: 0 },
  default: [Function: chalk] createChalk { [Symbol(LEVEL)]: 0 },
  foregroundColorNames: [ 'black', 'red', ... ],
  modifierNames: [ 'reset', 'bold', ... ],
  supportsColor: false,
  ...
}
[
  'Chalk',           '__esModule',
  'backgroundColorNames', 'backgroundColors',
  'chalkStderr',      'colorNames',
  'colors',           'default',
  'foregroundColorNames', 'foregroundColors',
  'modifierNames',    'modifiers',
  'supportsColor',    'supportsColorStderr',
  'underlineColorNames'
]
```

The `[Module: null prototype]` label and the `__esModule: true` property stood out. The actual callable `chalk` function wasn't at the top level — it was under `chalk.default`. In other words, `require('chalk')` was returning the raw ESM module namespace object, not the unwrapped default export you'd get from `import chalk from 'chalk'`.

## Root Cause

Node.js 22 ships a native interop that lets a CommonJS file `require()` an ESM-only package directly and by default (this is the big difference from earlier Node.js versions, which hard-failed with `ERR_REQUIRE_ESM`). That interop worked here, so `require('chalk')` completed without error.

But what it returns is the ESM namespace object itself. It does not perform the convenience transform that bundlers like webpack, ts-node, or Babel have long provided — hoisting the `default` export up to the top level for CommonJS callers. For a package like `chalk` that exposes only a default export, the actually-callable function stays nested under the namespace object's `default` property.

So `require('chalk')` wasn't returning "the chalk function" — it was returning `{ default: <chalk function>, __esModule: true, ...other named exports }`. There is no top-level `chalk.green`, hence `chalk.green('Hello, world!')` throws `TypeError: chalk.green is not a function`.

Because I was anchored on the old `ERR_REQUIRE_ESM` behavior, I initially assumed "require succeeded, so the ESM issue must be resolved" and wasted time checking `node_modules` and the Node.js version before looking at what `require` actually returned.

## How I Fixed It

### 1. Pull the default export off the require() result

```js
// index.js
const chalk = require('chalk').default;
console.log(chalk.green('Hello, world!'));
```

The callable `chalk` function lives on the `default` property of the namespace object that `require('chalk')` returns, so pull it out explicitly.

### 2. Run it again

```bash
node index.js
```

```text
Hello, world!
```

(shown in green in an actual terminal)

The `TypeError` was gone and the colored output worked as expected.

### 3. In TypeScript, also check `esModuleInterop`

If you're writing TypeScript, enabling `esModuleInterop: true` and `allowSyntheticDefaultImports: true` in `tsconfig.json` lets `import chalk from 'chalk'` compile down to code that handles `.default` for you automatically. If you're calling `require()` directly, you don't get that help and need to add `.default` by hand.

## Verify It Works

I compared both forms side by side to double-check the behavior.

```bash
node -e "const chalk = require('chalk'); console.log(typeof chalk.green);"
```

```text
undefined
```

```bash
node -e "const chalk = require('chalk').default; console.log(typeof chalk.green);"
```

```text
function
```

`require('chalk')` alone leaves `chalk.green` as `undefined`, while adding `.default` makes it a `function`. That confirmed the diagnosis.

## Takeaways

- Node.js 22 lets CommonJS `require()` an ESM-only package directly, but that's a different behavior from the older `ERR_REQUIRE_ESM` crash and easy to conflate with it.
- This native interop returns the raw ESM namespace object rather than mimicking a bundler's CommonJS interop. The default export isn't hoisted automatically — pull it out yourself with `require('pkg').default`.
- If you see `require()` succeed but a property comes back `undefined` or "is not a function", check `console.log(Object.keys(require('pkg')))` first and look for `__esModule` / `default` keys — it's the fastest way to confirm this pattern.

## FAQ

**Q: Does this happen with every ESM-only package?**
It's most noticeable with packages that expose only a default export, like `chalk`. Packages you consume via named exports (`const { someFunction } = require('pkg')`) work fine as-is, since those show up directly as properties on the namespace object.

**Q: Is switching the whole project to `"type": "module"` and `import` a better fix?**
Yes, where practical. `import chalk from 'chalk'` correctly unwraps the default export, so you never have to think about `.default`. But migrating an entire existing CommonJS project to ESM is a bigger change, so patching the specific call sites with `.default` is often the pragmatic option.

**Q: How is this different from the `ERR_REQUIRE_ESM` error?**
`ERR_REQUIRE_ESM` happens when the native require-ESM interop isn't available (older Node.js versions or environments where it's disabled) and `require()` itself hard-fails. Here, Node.js 22 had that interop enabled, so `require()` succeeded — the problem showed up one step later, in the shape of the value it returned.

## Related Articles

- [Fix ERESOLVE Errors When Running npm install](/en/npm-eresolve-error)
- [Managing Node.js Versions with nvm](/en/node-version-management-nvm)
- [Fix EADDRINUSE: Port Already in Use in Node.js](/en/node-eaddrinuse-port-fix)
- [Fix JavaScript Heap Out of Memory in Node.js](/en/node-heap-out-of-memory)

## Recommended VPS / Cloud Hosting
Looking for developer-friendly infrastructure to deploy what you just fixed? These providers are solid choices for production workloads.
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - managed cloud hosting with one-click stacks.
- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - bare-metal and VPS optimized for demanding workloads.

## Recommended VPS / Cloud Hosting
Looking for developer-friendly infrastructure to deploy what you just fixed? These providers are solid choices for production workloads.
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - managed cloud hosting with one-click stacks.
- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - bare-metal and VPS optimized for demanding workloads.
