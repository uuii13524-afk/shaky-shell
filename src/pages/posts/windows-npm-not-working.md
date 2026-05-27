---
title: 'Windowsでnpmコマンドが動かない時の対処法'
date: '2026-05-06'
category: 'Windows'
layout: '../../layouts/PostLayout.astro'
description: 'Windowsでnpmコマンドが認識されない・動かない時の原因と解決方法を解説。PATHの確認・Node.jsの再インストール手順を紹介します。'
---

## 症状

```
'npm' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

## 環境

- Windows 10 / 11
- Node.js

## 原因と解決方法

### 原因1：Node.jsがインストールされていない

https://nodejs.org からLTS版をインストール。

### 原因2：環境変数のPATHが通っていない

1. 「環境変数」を検索→「Path」を編集
2. Node.jsのインストールパスを追加（例：C:\Program Files\nodejs\）
3. ターミナルを再起動

### 原因3：PowerShellのスクリプト実行ポリシーが制限されている

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 原因4：ターミナルを再起動していない

インストール後にターミナルを再起動する。

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
