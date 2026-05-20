---
title: 'Node.jsのバージョンをnvmで管理する方法（Windows/Mac）'
date: '2026-05-20'
category: 'Node.js'
---

## やりたかったこと

プロジェクトによってNode.jsのバージョンを切り替えたかった。

## 環境

- Windows 10 / 11
- Mac

## Windowsの場合（nvm-windows）

### 1. インストール

https://github.com/coreybutler/nvm-windows/releases から `nvm-setup.exe` をダウンロード。

### 2. Node.jsをインストール

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
nvm install 22        # バージョン22をインストール
nvm use 22            # バージョン22に切り替え
nvm ls                # インストール済み一覧
nvm alias default 22  # デフォルトバージョンを設定
```

## ハマったポイント

- Windowsでは `nvm-windows` を使う。Mac用の `nvm` はWindowsでは動かない
- インストール前に既存のNode.jsをアンインストールしておく
- `nvm alias default` でデフォルトを設定しないとターミナルを開くたびに設定が必要

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)
