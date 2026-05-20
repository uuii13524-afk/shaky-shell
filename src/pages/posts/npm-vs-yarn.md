---
title: 'npmとyarnの違いと使い分け'
date: '2026-05-11'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
---

## コマンド比較

| 操作 | npm | yarn |
|------|-----|------|
| インストール | `npm install` | `yarn` |
| パッケージ追加 | `npm install パッケージ名` | `yarn add パッケージ名` |
| スクリプト実行 | `npm run スクリプト名` | `yarn スクリプト名` |

## どちらを使うべきか

- `package-lock.json` がある → npm
- `yarn.lock` がある → yarn
- 特にこだわりがなければ npm で十分

## ハマったポイント

- npmとyarnを同じプロジェクトで混在させない
- チームで開発する場合はどちらかに統一する

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [package.jsonのscriptsを活用して作業を効率化する方法](/posts/npm-package-json-scripts)
