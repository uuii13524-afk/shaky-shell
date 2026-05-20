---
title: 'npmのキャッシュをクリアして問題を解決する方法'
date: '2026-05-20'
category: 'Node.js'
---

## 症状

npmでパッケージをインストールしても動かない。
インストールが途中で止まる。
以前のバージョンが残っておかしな動作をしている。

## 環境

- Node.js
- npm

## キャッシュのクリア方法

```
npm cache clean --force
```

## パッケージ関連の問題をリセット

### node_modulesを削除して再インストール（Windows）

```
rmdir /s /q node_modules
del package-lock.json
npm install
```

### node_modulesを削除して再インストール（Mac/Linux）

```
rm -rf node_modules
rm package-lock.json
npm install
```

## ハマったポイント

- `--force` なしではキャッシュがクリアされない場合がある
- `node_modules` を削除して再インストールが最も確実
- キャッシュクリア後はインストールに時間がかかる

## いつキャッシュクリアするか

- パッケージのインストールが失敗する
- バージョンを変えても古い動作をしている
- 原因不明のエラーが出る

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
