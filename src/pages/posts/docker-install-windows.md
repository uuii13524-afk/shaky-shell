---
title: 'WindowsにDockerをインストールして動かすまでの手順'
date: '2026-05-10'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'WindowsにDocker Desktopをインストールして動かすまでの手順を解説。WSL2の有効化・インストール・動作確認までステップごとに紹介します。'
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

## ConoHa VPSでDockerを本番環境で使う

ローカルでDockerを動かせるようになったら、次は本番サーバーへの展開です。
ConoHa VPSならDockerがすぐに使える環境を低コストで用意できます。

<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4YQYYA" rel="nofollow">ConoHa VPSを見てみる →</a>
<img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4YQYYA" alt="">

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)


## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
