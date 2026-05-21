---
title: 'npmのキャッシュをクリアして問題を解決する方法'
date: '2026-05-09'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
---

## 症状

npmでパッケージをインストールしても動かない。インストールが途中で止まる。

## キャッシュのクリア

```
npm cache clean --force
```

## node_modulesを削除して再インストール（Windows）

```
rmdir /s /q node_modules
del package-lock.json
npm install
```

## ハマったポイント

- `--force` なしではキャッシュがクリアされない場合がある
- `node_modules` を削除して再インストールが最も確実

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
