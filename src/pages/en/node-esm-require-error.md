---
title: 'Fix: require() of ES Module Not Supported (ERR_REQUIRE_ESM) in Node.js'
date: '2026-08-22'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
description: 'require() on an ESM-only package like chalk v5 throws Error [ERR_REQUIRE_ESM] in a CommonJS Node.js project. Here is how to spot ESM-only packages and fix it with dynamic import().'
en_tags: ['Node.js', 'ESM', 'require']
---

## What I Was Trying to Do

I added `chalk` to an existing CLI tool, `report-cli`, to colorize terminal output. The project is CommonJS (no `"type"` field in `package.json`, so it defaults to CommonJS).

```bash
npm install chalk
```

The install itself succeeded. But when I loaded it with `require`, matching the style of the rest of the codebase, it crashed at runtime.

```js
// src/logger.js
const chalk = require('chalk');

console.log(chalk.green('done'));
```

```bash
node src/logger.js
```

```text
node:internal/modules/cjs/loader:1157
  throw err;
  ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/report-cli/node_modules/chalk/source/index.js from /home/user/report-cli/src/logger.js not supported.
Instead change the require of index.js in /home/user/report-cli/src/logger.js to a dynamic import() which is available in all CommonJS modules.
    at Module._extensions..js (node:internal/modules/cjs/loader:1157:19)
    at Module.load (node:internal/modules/cjs/loader:981:32)
    at Module._load (node:internal/modules/cjs/loader:822:12)
    at Module.require (node:internal/modules/cjs/loader:1005:19)
    at require (node:internal/modules/helpers:102:18)
    at Object.<anonymous> (/home/user/report-cli/src/logger.js:1:15) {
  code: 'ERR_REQUIRE_ESM'
}
```

`npm install` had finished cleanly, so the crash only showing up at runtime was confusing. I assumed the package itself was broken, removed it, and reinstalled — same error.

## Environment

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- Package in question: chalk 5.3.0
- Project type: CommonJS (no `"type"` field in `package.json`, which defaults to CommonJS)

## What I Tried

First I checked whether `node_modules/chalk` itself was corrupted by looking directly at its `package.json`.

```bash
cat node_modules/chalk/package.json
```

```text
{
  "name": "chalk",
  "version": "5.3.0",
  "type": "module",
  "exports": "./source/index.js",
  ...
}
```

The `"type": "module"` line caught my eye, but I didn't think much of it yet. My next guess was that downgrading a version would fix it, so I tried `chalk@4`.

```bash
npm uninstall chalk
npm install chalk@4
node src/logger.js
```

```text
done
```

`chalk@4` worked without any changes. So the package wasn't broken — something specific to `chalk@5` was the actual cause. Comparing the two `package.json` files side by side, `chalk@4` had no `"type"` field at all, while `chalk@5` had `"type": "module"`.

## Root Cause

Node.js uses the `"type"` field in a package's `package.json` to decide whether to treat that package as CommonJS or as an ES module (ESM). A package with `"type": "module"` is published as a pure ES module and cannot be loaded directly with CommonJS `require()`.

`chalk` moved to being fully ESM-only starting with v5.0.0 (versions up to `chalk@4` still supported CommonJS). Since `npm install chalk` pulled the latest version (5.3.0) with no version pin, the existing CommonJS `require('chalk')` call in this project stopped being valid at a structural level.

The `Error [ERR_REQUIRE_ESM]` error code is what Node.js throws specifically when it detects that a module being `require()`'d is an ES module. As the message itself suggests, the officially recommended fix is to replace `require()` with a dynamic `import()`.

## How I Fixed It

### 1. Check whether the package is ESM-only

```bash
cat node_modules/chalk/package.json | grep '"type"'
```

```text
"type": "module",
```

A package with `"type": "module"` and no CommonJS `require` condition in its `"exports"` field cannot be loaded with `require()`.

### 2. Replace `require` with a dynamic `import()`

I made the calling function `async` and swapped `require` for `await import()`.

```js
// src/logger.js
async function main() {
  const { default: chalk } = await import('chalk');
  console.log(chalk.green('done'));
}

main();
```

`import()` is a dynamic import expression that's available even inside CommonJS files, and it returns a Promise. One thing that tripped me up: since the package uses a default export rather than named exports, you have to destructure `{ default: chalk }`. I initially wrote `const chalk = await import('chalk')`, which left `chalk.green` as `undefined`.

### 3. Verify it works

```bash
node src/logger.js
```

```text
done
```

The terminal printed `done` in green, confirming it worked.

### 4. Centralize the import when multiple files call it

`logger.js` was required from several other files, so writing `import()` in each of them separately would mean loading the module redundantly. I pulled it into a small helper that caches the result of a single top-level `import()`.

```js
// src/chalkLoader.js
let chalkPromise;
function getChalk() {
  if (!chalkPromise) {
    chalkPromise = import('chalk').then((m) => m.default);
  }
  return chalkPromise;
}
module.exports = { getChalk };
```

```js
// src/logger.js
const { getChalk } = require('./chalkLoader');

async function main() {
  const chalk = await getChalk();
  console.log(chalk.green('done'));
}

main();
```

## Verify It Works

I confirmed all three call sites could produce colored output through `getChalk()`.

```bash
node src/logger.js
node src/reporter.js
node src/cli.js --check
```

```text
done
report: 12 passed, 0 failed
check: ok
```

`ERR_REQUIRE_ESM` did not reoccur, and colored output rendered correctly in all three.

## Takeaways

- `Error [ERR_REQUIRE_ESM]` is the specific error Node.js throws when a CommonJS `require()` call tries to load an ESM-only package. It's not a sign the package is broken.
- Checking whether the package's `package.json` has `"type": "module"` is a quick way to confirm an ESM-only migration is the cause.
- If you want to stay on CommonJS, replace `require` with `await import()`. If a package is called from several places, centralize the import behind a helper that caches the result so you're not re-importing it repeatedly.
- Migrating the entire project to `"type": "module"` is another option, but it's a bigger change. Switching just the affected import to dynamic `import()`, as done here, keeps the change local.

## FAQ

**Q: Would pinning `chalk` to v4 avoid this entirely?**
Yes — `chalk@4` still supports CommonJS, so `require('chalk')` keeps working as-is. That said, future fixes and features only land in v5 and later, so migrating to dynamic import is the better long-term fix.

**Q: Would switching the whole project to `"type": "module"` also fix this?**
It would, but it's a much bigger change — every `require`/`module.exports` in the codebase would need to become `import`/`export`, and any CommonJS-only dependencies could break in the process. Switching just the affected import to dynamic `import()`, as shown here, keeps the blast radius small.

**Q: Why can't I just write a top-level `await import()`?**
CommonJS modules can't use top-level `await` — that's an ES-module-only feature. That's why the `import()` call needs to sit inside an `async` function like `main()` above.

## Related Articles

- [Fix: git clone Leaves Submodule Directories Empty and Breaks the Build](/en/git-submodule-not-initialized/)
- [Fix: npm ERESOLVE Dependency Resolution Error](/en/npm-eresolve-error/)
- [Managing Node.js Versions with nvm](/en/node-version-management-nvm/)
- [Fixing Node.js "heap out of memory" Errors](/en/node-heap-out-of-memory/)
- [Fix: npm install Permission Denied](/en/npm-install-permission-denied/)
