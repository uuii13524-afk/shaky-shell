---
title: 'Node.jsのバージョンをnvmで管理する方法（Windows/Mac）'
date: '2026-05-20'
category: 'Node.js'
---

## やりたかったこと

プロジェクトによってNode.jsのバージョンを切り替えたかった。
nvmを使うとバージョン管理が簡単にできる。

## 環境

- Windows 10 / 11
- Mac

## Windowsの場合（nvm-windows）

### 1. インストール

https://github.com/coreybutler/nvm-windows/releases にアクセス。
`nvm-setup.exe` をダウンロードしてインストール。

### 2. インストール確認

```
nvm version
```

### 3. Node.jsをインストール

```
nvm install 22
nvm use 22
```

### 4. 確認

```
node -v
npm -v
```

## Macの場合（nvm）

### 1. インストール

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

ターミナルを再起動する。

### 2. Node.jsをインストール

```
nvm install 22
nvm use 22
```

## よく使うコマンド

```
nvm install 22        # バージョン22をインストール
nvm use 22            # バージョン22に切り替え
nvm ls                # インストール済みのバージョン一覧
nvm ls-remote         # インストール可能なバージョン一覧
nvm alias default 22  # デフォルトバージョンを設定
```

## ハマったポイント

- Windowsでは `nvm-windows` を使う。Mac用の `nvm` はWindowsでは動かない
- インストール前に既存のNode.jsをアンインストールしておく
- `nvm use` はターミナルを開くたびに必要な場合がある。`nvm alias default` でデフォルトを設定する
- プロジェクトルートに `.nvmrc` ファイルを置くとバージョンを自動で切り替えられる

## .nvmrcの使い方

プロジェクトルートに `.nvmrc` を作成して使いたいバージョンを書く。

```
22
```

以降は `nvm use` だけで自動的に対応バージョンに切り替わる。
