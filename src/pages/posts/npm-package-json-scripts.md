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

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
