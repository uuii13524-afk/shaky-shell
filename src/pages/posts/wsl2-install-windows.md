---
title: 'WindowsでWSL2をインストールする方法'
date: '2026-05-11'
category: 'Windows'
layout: '../../layouts/PostLayout.astro'
description: 'WindowsでWSL2をインストールしてLinux環境を構築する手順を解説。wsl --installコマンドの使い方・Ubuntuの初期設定方法を紹介します。'
---

## 手順

### 1. WSL2をインストール

PowerShellを管理者として起動。

```
wsl --install
```

再起動する。

### 2. Ubuntuの初期設定

再起動後にUbuntuが起動。ユーザー名とパスワードを設定する。

### 3. 動作確認

```
wsl
```

## よく使うWSLコマンド

```
wsl --shutdown         # WSLを停止
wsl --update           # WSLを更新
wsl --list --verbose   # インストール済み一覧
```

## ハマったポイント

- BIOSでIntel VT-x / AMD-Vを有効にする
- Windows Updateで最新版にしてから実行する

## XServer VPSで本番環境を用意する

ローカルでの動作確認ができたら、次は本番サーバーへの展開です。
XServer VPSなら高性能な環境を低コストで用意できます。

<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25ES2Q" rel="nofollow">エックスサーバーのVPSサーバー</a>
<img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25ES2Q" alt="">

## 関連記事

- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [Windows Terminalをインストールして使いやすくする方法](/posts/windows-terminal-setup)


## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">

## おすすめのプログラミングスクール

Windowsで開発環境を整えたら、次のステップとしてプログラミングスクールで体系的に学ぶのもおすすめです。

<a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+7N2A9E+529E+5YRHE" rel="nofollow">【Winスクール】</a>は講師が寄り添う個人レッスン形式のスクールで、未経験からでも即戦力のプログラマーを目指せます。無料カウンセリングも受付中です。
<img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=4B3VRB+7N2A9E+529E+5YRHE" alt="">
