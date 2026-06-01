---
title: 'How to Use package.json Scripts to Automate Tasks'
date: '2026-05-17'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Node.js', 'npm', 'package.json', 'scripts']
en_tags: ['Node.js', 'npm', 'package.json', 'scripts']
description: 'How to define custom commands in the scripts field of package.json and run them with npm run. Includes pre/post hooks and special script names.'
---
## Basic Scripts

```json
{
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "lint": "eslint src/",
    "deploy": "npm run build && wrangler deploy"
  }
}
```

```bash
npm run dev
npm run build
```

## Special Script Names

| Script name | How to run |
|-------------|-----------|
| `start` | `npm start` (no `run` needed) |
| `test` | `npm test` (no `run` needed) |
| `prebuild` | Runs automatically before `build` |

## Common Pitfalls

- `&&` may not work on Windows — use `cross-env` or separate scripts
- `npm start` and `npm test` don't need the `run` keyword

To run these scripts automatically in CI, combine with [GitHub Actions: Basic Auto-Deploy Setup](/en/github-actions-basic).

## Related Posts

- [npm vs yarn: Differences and When to Use Each](/en/npm-vs-yarn)
- [Fix npm Cache Problems](/en/npm-cache-clear)
- [Manage Node.js Versions with nvm](/en/node-version-management-nvm)
- [How to Deploy an Astro Site to Cloudflare Pages](/en/astro-cloudflare-deploy)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
