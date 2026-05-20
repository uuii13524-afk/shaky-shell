---
title: 'Node.jsのバージョンをnvmで管理する方法（Windows/Mac）'
date: '2026-05-07'
category: 'Node.js'
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
