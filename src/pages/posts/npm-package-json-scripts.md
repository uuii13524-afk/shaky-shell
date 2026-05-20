---
title: 'package.jsonのscriptsを活用して作業を効率化する方法'
date: '2026-05-17'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
---

## scriptsの基本

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

## 特殊なスクリプト名

| スクリプト名 | 実行 |
|-------------|------|
| `start` | `npm start`（runなし） |
| `test` | `npm test`（runなし） |
| `prebuild` | `build` の前に自動実行 |

## ハマったポイント

- `&&` はWindowsで動かない場合がある
- `npm start` と `npm test` は `run` が不要

## 関連記事

- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
