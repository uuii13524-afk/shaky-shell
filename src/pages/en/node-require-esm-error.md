---
title: 'Fix: Error [ERR_REQUIRE_ESM] When require()-ing node-fetch on Node.js 20'
date: '2026-08-26'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'On Node.js 20, require("node-fetch") throws "Error [ERR_REQUIRE_ESM]" and crashes the process immediately. Here is why the package became ESM-only and how to fix it with a dynamic import or by switching the project to ESM.'
en_tags: ['Node.js', 'ERR_REQUIRE_ESM', 'CommonJS']
---

## What I Was Trying to Do

I was adding a step to our internal batch job `report-fetcher` that writes data pulled from an external API into a cache file. The existing codebase is CommonJS (`require`-based), and I added `node-fetch` to implement the HTTP request.

```bash
npm install node-fetch
```

The install finished cleanly, but running `node index.js` crashed immediately with an exception.

```text
node:internal/modules/cjs/loader:1246
  throw err;
  ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/report-fetcher/node_modules/node-fetch/src/index.js from /home/user/report-fetcher/index.js not supported.
Instead change the require of index.js in /home/user/report-fetcher/index.js to a dynamic import() which is available in all CommonJS modules.
    at Object.<anonymous> (/home/user/report-fetcher/index.js:3:20) {
  code: 'ERR_REQUIRE_ESM'
}

Node.js v20.14.0
```

It was thrown by a single line, `require('node-fetch')`, so this didn't look like a typo in my code. My first guess was a bad version pin or a broken dependency tree, so I deleted `node_modules` and reinstalled — same error, reproduced exactly.

## Environment

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- Package in question: `node-fetch@3.3.2` (`npm install node-fetch` pulled the latest)
- Project setup: no `"type"` field in `package.json` (defaults to CommonJS)

## What I Tried

First I removed `node_modules` and `package-lock.json` and did a clean install.

```bash
rm -rf node_modules package-lock.json
npm install
node index.js
```

Same `ERR_REQUIRE_ESM` error, unchanged. Next I suspected a dependency resolution issue and checked what actually got installed.

```bash
npm ls node-fetch
```

```text
report-fetcher@1.0.0 /home/user/report-fetcher
└── node-fetch@3.3.2
```

`node-fetch` was installed as expected, and the version wasn't anything unusual. That's when I flipped my assumption — maybe the version was "too new" rather than broken — and went to check the release notes.

## Root Cause

Starting with v3, `node-fetch` is an **ESM-only package**. `package.json` didn't declare `"type": "module"`, and the code was loading it with `require()` — that combination is the direct cause.

Node's CommonJS loader treats a package as ESM when its `package.json` declares `"type": "module"`, or when the file extension is `.mjs`. ESM can't be loaded synchronously via `require()` by spec, so calling `require('node-fetch')` from CommonJS code throws `ERR_REQUIRE_ESM` partway through the load and kills the process.

`node-fetch@2.x` supported both CommonJS and ESM, so writing `require('node-fetch')` out of habit worked fine back then. What actually landed via `npm install` this time was the ESM-only v3 line. Since `npm install` grabs the latest major version unless you pin one explicitly, reusing old muscle memory (or code copied from another project) makes this easy to miss.

## How I Fixed It

There are two general approaches. Converting the whole project to ESM would have touched too much code for this change, so I went with a dynamic import scoped to the file that needed it.

### Option 1: Switch to dynamic import() (what I used)

Instead of a top-level, synchronous `require('node-fetch')`, load it with `await import()` inside the function that needs it.

```js
// Before
const fetch = require('node-fetch');

async function fetchReport(url) {
  const res = await fetch(url);
  return res.json();
}
```

```js
// After
async function fetchReport(url) {
  const { default: fetch } = await import('node-fetch');
  const res = await fetch(url);
  return res.json();
}
```

`import()` is an async function callable from inside CommonJS files, so it works even where `require` won't. Every caller further up the chain that expected a synchronous call had to become `async` too, which was the main cost of this fix.

```bash
node index.js
```

```text
[report-fetcher] fetch ok: status=200
[report-fetcher] cache written: ./cache/report.json
```

It started cleanly and wrote the cache file as expected.

### Option 2: Convert the project to ESM (not used here)

Add `"type": "module"` to `package.json` and rewrite every `require` as an `import` statement.

```json
{
  "type": "module"
}
```

This project still had several other CommonJS dependencies, so I picked the dynamic-import approach to keep the blast radius small. For a brand-new project, starting ESM-first avoids this class of error entirely.

### Option 3: Use a CommonJS-friendly alternative instead

If you're not tied to `node-fetch` specifically, Node.js 18+ ships a global `fetch` function. Skipping the extra dependency is often the simplest fix.

```js
async function fetchReport(url) {
  const res = await fetch(url); // global fetch, no require or import needed
  return res.json();
}
```

I stuck with dynamic import here to preserve compatibility with the existing code, but for new code, reaching for the built-in `fetch` first is worth considering.

## Verify It Works

I ran a quick standalone check to reconfirm `node-fetch` is indeed ESM-only.

```bash
node -e "require('node-fetch')"
```

```text
node:internal/modules/cjs/loader:1246
  throw err;
Error [ERR_REQUIRE_ESM]: require() of ES Module ... not supported.
```

With that confirmed, I ran the fixed `fetchReport` function as the real batch job five times in a row and all five completed cleanly.

```bash
for i in 1 2 3 4 5; do node index.js; done
```

```text
[report-fetcher] fetch ok: status=200
[report-fetcher] cache written: ./cache/report.json
(same output all 5 runs)
```

## Takeaways

- `Error [ERR_REQUIRE_ESM]` means Node tried to `require()` a package that's ESM-only — it's not a syntax mistake in your own code.
- `node-fetch` became ESM-only starting with v3. Since `npm install` pulls the latest major version unless you pin one, code written against v2's dual CJS/ESM support will hit this the moment the dependency gets reinstalled.
- Three fixes to pick from: switch the call site to dynamic `import()`, convert the whole project to ESM, or use Node's built-in `fetch` instead. Dynamic import is the lowest-blast-radius option inside an existing CommonJS codebase. The same `ERR_REQUIRE_ESM` shows up with other popular packages that went ESM-only too (`chalk`, `execa`, and others) — after a major version bump, checking the release notes for "now ESM-only" is worth doing before assuming your install is broken.

## Related Articles

- [Switch Between Node.js Versions with nvm](/en/node-version-management-nvm)
- [Fix the ERESOLVE Error from npm install](/en/npm-eresolve-error)
- [Fix EADDRINUSE Errors in Node.js: Finding and Freeing the Port](/en/node-eaddrinuse-port-fix)
- [npm vs yarn: Key Differences and When to Use Each](/en/npm-vs-yarn)
- [How to Write the scripts Field in package.json](/en/npm-package-json-scripts)
