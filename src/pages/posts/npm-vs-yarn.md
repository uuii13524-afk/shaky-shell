---
title: 'npmとyarnの違いと使い分け'
date: '2026-05-11'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'npmとyarnのコマンド対応表・速度・lockファイルの違いを解説。インストール・アンインストール・スクリプト実行コマンドを比較して紹介します。'
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

GitHub Actionsのキャッシュはnpmかyarnかによって設定が変わる。[GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache)で `cache: 'npm'` か `cache: 'yarn'` を使い分けてほしい。

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [package.jsonのscriptsを活用して作業を効率化する方法](/posts/npm-package-json-scripts)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
