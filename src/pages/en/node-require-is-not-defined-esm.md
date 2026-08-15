---
title: 'Fixing "require is not defined in ES module scope" in Node.js'
date: '2026-08-15'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'After adding "type": "module" to package.json, an existing .js file calling require() suddenly throws ReferenceError: require is not defined in ES module scope. Covers why it happens and three fixes: converting to import syntax, using the .cjs extension, and createRequire.'
ja_tags: ['Node.js', 'ESM', 'CommonJS', 'require', 'type module']
en_tags: ['Node.js', 'ESM', 'CommonJS', 'require', 'type module']
---

## What I Was Trying to Do

I wanted top-level await in one of my build scripts, so I added `"type": "module"` to that script's `package.json`. I didn't touch the script file itself. Running it the same way I always had, `node index.js`, immediately blew up:

```text
file:///home/deploy/scripts/index.js:1
const path = require('path');
             ^

ReferenceError: require is not defined in ES module scope, you can use import instead
This file is being treated as an ES module because it has a '.js' file extension and '/home/deploy/scripts/package.json' contains "type": "module". To treat it as a CommonJS script, rename it to use the '.cjs' file extension.
    at file:///home/deploy/scripts/index.js:1:14
    at ModuleJob.run (node:internal/modules/esm/module_job:343:25)
    at async onImport.tracePromise.__proto__ (node:internal/modules/esm/loader:665:26)
    at async asyncRunEntryPointWithESMLoader (node:internal/modules/run_main:117:5)

Node.js v22.22.2
```

Since I hadn't changed a single line of `index.js`, it took me a moment to connect the error to the `package.json` edit I'd just made.

## Environment

- OS: Ubuntu 22.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Target file: a `.js` script written in CommonJS style (using `require`)

## What I Tried

My first thought, following the error message, was to just rewrite `require` as `import`. But the script used `require` in several places, and rewriting all of them right away felt like more work than I wanted to do at that moment. So instead I removed `"type": "module"` from `package.json` again to see what happened.

```bash
node index.js
```

```text
a/b
```

That got the script working again, but it defeated the whole point — I'd added the setting specifically to get top-level await. Then I remembered the same file also used `__dirname`, so I put `"type": "module"` back and tried running that part too.

```bash
node dirname-test.js
```

```text
file:///home/deploy/scripts/dirname-test.js:1
console.log(__dirname);
            ^

ReferenceError: __dirname is not defined in ES module scope
This file is being treated as an ES module because it has a '.js' file extension and '/home/deploy/scripts/package.json' contains "type": "module".
    at file:///home/deploy/scripts/dirname-test.js:1:13
    at ModuleJob.run (node:internal/modules/esm/module_job:343:25)
    at async onImport.tracePromise.__proto__ (node:internal/modules/esm/loader:665:26)
    at async asyncRunEntryPointWithESMLoader (node:internal/modules/run_main:117:5)

Node.js v22.22.2
```

So it wasn't just `require` — `__dirname` and `__filename` are unavailable in ES modules too, and a one-line fix wasn't going to be enough.

## Why This Happens

Setting `"type": "module"` in `package.json` changes how every `.js` file in that directory (and below) is interpreted — from CommonJS to ES Modules. CommonJS modules get `require`, `__dirname`, `__filename`, `module`, and `exports` implicitly provided by Node.js, but none of these exist in ES Modules; it's a genuinely different module system. Because the interpretation is controlled entirely by the `type` field in `package.json`, changing that one setting flips how every `.js` file is parsed without touching a single line inside those files — which is why existing CommonJS syntax starts failing everywhere at once.

## Solution

Pick whichever of these three fits the situation.

### Option 1: Rewrite to import syntax (best for new code or small scripts)

```js
import path from 'path';
console.log(path.join('a', 'b'));
```

```bash
node index2.js
```

```text
a/b
```

Replacing `require('path')` with `import path from 'path'` is enough to make it work while keeping `"type": "module"`. If you're planning to write ESM going forward anyway, this is the simplest option.

### Option 2: Rename just that file to `.cjs` (when you don't want to touch existing code)

```bash
mv index.js index.cjs
node index.cjs
```

```text
a/b
```

A `.cjs` extension is always treated as CommonJS, regardless of the `type` setting in `package.json`. You can keep using `require` and `__dirname` as-is, which is useful when you don't want to rewrite a large number of scripts all at once.

### Option 3: Bring back require selectively with createRequire (when you need a CJS-only package)

```js
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const path = require('path');
console.log(path.join('a', 'b'));
```

```bash
node index3.js
```

```text
a/b
```

This works well if you've moved to ESM but still need to `require` a CommonJS-only package that doesn't support `import`. The same idea applies to `__dirname`/`__filename` — rebuild them from `import.meta.url` using `fileURLToPath` and `path.dirname`.

```js
import { fileURLToPath } from 'url';
import path from 'path';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
console.log(__dirname);
```

```bash
node dirname-fix.js
```

```text
/home/deploy/scripts
```

## Gotchas

- I hadn't changed `index.js` at all, so at first I wasted time looking for the wrong cause. I didn't realize that how a `.js` file gets parsed is entirely controlled by the `type` field in `package.json`.
- I thought fixing the `require` error was the end of it, but the same file also used `__dirname`, so a second ReferenceError showed up right after the first fix. CommonJS provides more than one implicit global, so don't assume one fix covers everything.
- When I tried converting the whole project to ESM at once, I ran into npm packages that were CommonJS-only and didn't support being `import`-ed from ESM. Rather than forcing every file to `import`, it was less work to leave those specific packages on `createRequire`.

## FAQ

**Q: Would this error not happen at all if I skip `"type": "module"`?**
Correct. If `package.json` has no `type` field, or explicitly sets `"commonjs"`, `.js` files are treated as CommonJS as before and `require` works normally. You only need `"type": "module"` if you specifically need top-level await or an ESM-only package.

**Q: Is it fine to mix `.js` and `.cjs` files in the same project?**
Yes. Node.js determines the module system per file extension, so `.mjs` (always ESM), `.cjs` (always CommonJS), and `.js` (follows `package.json`'s `type`) can all coexist in the same project. That makes it a reasonable way to migrate incrementally.

**Q: Do I need to do the same thing if I'm using TypeScript?**
Yes — the `module` option in `tsconfig.json` (or your `ts-node` config) determines what kind of `.js` the compiler emits, so the `package.json` next to that compiled output needs a matching `type` field. If your transpiler settings and Node.js's own `package.json` setting disagree, you'll hit the same class of error.

## Related Articles

- [How to Fix "Heap Out of Memory" in Node.js](/en/node-heap-out-of-memory)
- [How to Fix EADDRINUSE Errors in Node.js](/en/node-eaddrinuse-port-fix)
- [Fixing npm install ERESOLVE Errors](/en/npm-eresolve-error)
- [Switching Node.js Versions with nvm](/en/node-version-management-nvm)
- [npm vs yarn: Key Differences](/en/npm-vs-yarn)
