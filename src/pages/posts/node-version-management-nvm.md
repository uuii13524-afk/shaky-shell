---
title: 'Node.jsのバージョンをnvmで管理する方法（Windows/Mac）'
date: '2026-05-07'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'nvmを使ってNode.jsの複数バージョンをインストール・切り替える方法をWindows・Macそれぞれ解説。プロジェクト別の.nvmrcファイル設定も紹介します。'
---

## やりたかったこと

プロジェクトによってNode.jsのバージョンを切り替えたかった。

## Windowsの場合（nvm-windows）

https://github.com/coreybutler/nvm-windows/releases から `nvm-setup.exe` をダウンロード。

```
nvm install 22
nvm use 22
```

## Macの場合

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 22
nvm use 22
```

## よく使うコマンド

```
nvm install 22
nvm use 22
nvm ls
nvm alias default 22
```

## ハマったポイント

- Windowsでは `nvm-windows` を使う
- インストール前に既存のNode.jsをアンインストール
- `nvm alias default` でデフォルトを設定しないとターミナルを開くたびに設定が必要

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
