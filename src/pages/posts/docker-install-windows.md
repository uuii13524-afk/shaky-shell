---
title: 'WindowsにDockerをインストールして動かすまでの手順'
date: '2026-05-10'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
---

## 手順

### 1. WSL2をインストール

```
wsl --install
```

再起動する。

### 2. Docker Desktopをダウンロード

https://www.docker.com/products/docker-desktop から「Download for Windows」。

### 3. インストール

「Use WSL 2 instead of Hyper-V」にチェックが入っていることを確認。再起動する。

### 4. 動作確認

```
docker --version
docker run hello-world
```

## ハマったポイント

- BIOSで仮想化（Intel VT-x / AMD-V）を有効にする
- WSL2のインストールが必要：`wsl --install`

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
