---
title: 'npmのキャッシュをクリアして問題を解決する方法'
date: '2026-05-09'
category: 'Node.js'
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
