---
title: 'Fix: Node.js require() Throws Error [ERR_REQUIRE_ESM]'
date: '2026-09-24'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'require() of node-fetch throws Error [ERR_REQUIRE_ESM] in a CommonJS project because the package went ESM-only. Here is how to spot ESM-only packages and fix it with a version pin or dynamic import.'
en_tags: ['Node.js', 'ERR_REQUIRE_ESM', 'node-fetch']
---

## What I Was Trying to Do

I was adding an outbound API call to an internal Express batch script. I had never used `node-fetch` before, so I installed the latest version without thinking twice about it.

```bash
npm install node-fetch
```

The install finished cleanly and `node-fetch` showed up in `package.json` as a dependency. I loaded it the same way I always load packages, with `require`.

```js
// fetch-users.js
const fetch = require('node-fetch');

async function main() {
  const res = await fetch('https://api.example.com/users');
  const data = await res.json();
  console.log(data);
}

main();
```

Running it with `node fetch-users.js` immediately threw an exception and the script stopped.

```text
node:internal/modules/cjs/loader:1105
    throw new ERR_REQUIRE_ESM(filename, parentPath, packageJsonPath);
    ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/batch/node_modules/node-fetch/src/index.js from /home/user/batch/fetch-users.js not supported.
Instead change the require of index.js in /home/user/batch/fetch-users.js to a dynamic import() which is available in all CommonJS modules.
    at Object.<anonymous> (/home/user/batch/fetch-users.js:1:15) {
  code: 'ERR_REQUIRE_ESM'
}
```

Since `npm install` hadn't complained about anything, my first assumption was a typo somewhere in my own code.

## Environment

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- Package in question: node-fetch 3.3.2
- Project setup: no `"type"` field in `package.json` (defaults to CommonJS)

## What I Tried

My first guess was the `require` syntax itself. I rewrote it with destructuring, thinking a default export might need to be pulled out explicitly.

```js
const { default: fetch } = require('node-fetch');
```

Same error, word for word. That ruled out the destructuring theory — it wasn't about how I wrote the `require` call, it was that `require()` itself was being rejected for this module.

Next I opened the installed package's own `package.json` directly.

```bash
cat node_modules/node-fetch/package.json | grep -E '"type"|"exports"|"main"'
```

```text
  "type": "module",
  "exports": "./src/index.js",
  "main": "./src/index.js",
```

There it was: `"type": "module"`. I knew that field tells Node.js how to interpret a package, but until this point I had only ever thought about it in terms of my own project's `package.json`, never a dependency's. This was the first time it clicked that a dependency itself can be ESM-only, independent of how my own project is configured.

Checking node-fetch's release history confirmed it: starting with v3.0.0, CommonJS support was dropped entirely and the package became ESM-only. My `package.json` had no version constraint on `node-fetch`, so `npm install` had silently pulled the latest v3 release.

## Root Cause

What I confirmed:

- `node-fetch` has been ESM-only since v3.0.0 and can no longer be loaded with CommonJS `require()`.
- My project has no `"type": "module"` in `package.json`, so it runs as CommonJS.
- When a CommonJS file `require()`s an ESM-only package, Node.js throws at module-resolution time and halts execution. This is expected behavior that pushes you toward `import` or a dynamic `import()`, not a bug.

## How I Fixed It

Migrating the whole project to ESM wasn't practical for a single batch script, so I pinned `node-fetch` to the last major version that still supports CommonJS: v2.

First, remove the current v3 install.

```bash
npm uninstall node-fetch
```

Install v2 explicitly.

```bash
npm install node-fetch@2
```

Confirm the pinned version landed in `package.json`.

```bash
grep node-fetch package.json
```

```text
    "node-fetch": "^2.7.0",
```

No code changes needed — `require('node-fetch')` works as-is.

```js
const fetch = require('node-fetch');
```

If a full ESM migration is the better long-term move for a project, the alternative is adding `"type": "module"` to `package.json` and converting every `require` to `import`. For a single script, I didn't want to change the whole project's module system, so pinning the dependency version was the faster, lower-risk fix.

There's a third option worth knowing about even if I didn't use it here: a dynamic `import()` inside an otherwise-CommonJS file. Node's own error message actually points at this.

```js
async function getFetch() {
  const { default: fetch } = await import('node-fetch');
  return fetch;
}

async function main() {
  const fetch = await getFetch();
  const res = await fetch('https://api.example.com/users');
  const data = await res.json();
  console.log(data);
}

main();
```

`import()` is a function, not a static keyword, so it's legal inside CommonJS and returns a promise instead of throwing synchronously. This is handy when only one or two call sites in a large CommonJS codebase need an ESM-only package and a full migration isn't worth it. I ended up not needing it here because pinning to v2 kept the code identical to what it already was, but it's the right tool when the CJS-compatible version of a package is outdated or missing a feature you actually need.

It's also worth understanding why this keeps happening: a growing number of popular npm packages are dropping CommonJS support entirely and shipping ESM-only releases, often as part of a major version bump. `node-fetch` did it at v3, `chalk` did it at v5, and `inquirer` did it at v9. None of these are bugs in the packages — they're intentional decisions by maintainers to simplify their own build tooling now that Node.js has had stable ESM support for several years. The practical impact for consumers is the same every time: an existing CommonJS project that upgrades one of these dependencies without a version constraint will suddenly hit `ERR_REQUIRE_ESM` on the next `npm install`, even though nothing in the project's own code changed.

## Verifying the Fix

With `node-fetch@2` installed, I ran the script again.

```bash
node fetch-users.js
```

```text
[
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' }
]
```

The API response came back with no errors. I also checked the resolved version directly.

```bash
npm ls node-fetch
```

```text
batch@1.0.0 /home/user/batch
└── node-fetch@2.7.0
```

## Summary

- `Error [ERR_REQUIRE_ESM]` isn't a bug in your own code — it means the package you're `require()`ing is ESM-only.
- Check `node_modules/<package>/package.json` for `"type": "module"` or the `"exports"` field to tell whether a dependency has gone ESM-only.
- If you need to stay on CommonJS, pin the dependency to its last CJS-compatible version; if you're ready to modernize the whole project, switch to `"type": "module"` and rewrite `require` calls as `import`. The same error shows up with other popular packages that went ESM-only, like `chalk` or `inquirer`.

## Related Posts

- [Switch Node.js Versions with nvm](/en/node-version-management-nvm/)
- [Fix ERESOLVE Errors During npm install](/en/npm-eresolve-error/)
- [Understanding the scripts Field in package.json](/en/npm-package-json-scripts/)
- [Fix Node.js Crashing with JavaScript Heap Out of Memory](/en/node-heap-out-of-memory/)
- [Cache Node.js Dependencies in GitHub Actions](/en/github-actions-node-cache/)
