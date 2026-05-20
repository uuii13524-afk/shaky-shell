---
title: 'package.jsonのscriptsを活用して作業を効率化する方法'
date: '2026-05-20'
category: 'Node.js'
---

## やりたかったこと

毎回長いコマンドを打つのが面倒なので `package.json` のscriptsに登録して短縮したかった。

## 環境

- Node.js
- npm

## scriptsの基本

`package.json` の `scripts` に登録したコマンドは `npm run スクリプト名` で実行できる。

```json
{
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  }
}
```

```bash
npm run dev      # astro dev を実行
npm run build    # astro build を実行
```

## よく使うscriptsの例

```json
{
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "lint": "eslint src/",
    "format": "prettier --write src/",
    "clean": "rm -rf dist node_modules",
    "deploy": "npm run build && wrangler deploy"
  }
}
```

## 複数のコマンドを順番に実行

```json
{
  "scripts": {
    "build:prod": "npm run lint && npm run build"
  }
}
```

`&&` は前のコマンドが成功した場合のみ次を実行する。

## scriptsから別のscriptを呼び出す

```json
{
  "scripts": {
    "lint": "eslint src/",
    "build": "astro build",
    "build:check": "npm run lint && npm run build"
  }
}
```

## 特殊なスクリプト名

| スクリプト名 | 実行タイミング |
|-------------|--------------|
| `start` | `npm start` で実行（`run` 不要） |
| `test` | `npm test` で実行（`run` 不要） |
| `prebuild` | `build` の前に自動実行 |
| `postbuild` | `build` の後に自動実行 |

## ハマったポイント

- `npm start` と `npm test` は `run` が不要
- WindowsとMac/Linuxでコマンドが違う場合は `cross-env` を使う
- `&&` はシェルのコマンド結合なのでWindowsで動かない場合がある

## 関連記事

- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
