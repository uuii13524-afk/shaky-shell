---
title: 'WindowsにDockerをインストールして動かすまでの手順'
date: '2026-05-10'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'WindowsにDocker Desktopをインストールして動かすまでの手順を解説。WSL2の有効化・インストール・動作確認までステップごとに紹介します。'
---

## やりたかったこと

Windowsのラップトップ（Windows 11 Home）でDockerを動かしたかった。チームのMacメンバーはすんなり動いているのに、自分だけ `docker run hello-world` を実行しても何も起きなくて、インストール手順を調べながら3時間格闘した。

---

## 環境

- OS: Windows 11 Home 23H2
- CPU: Intel Core i7（VT-x対応）
- Docker Desktop: 4.30.0
- WSL2: Ubuntu 22.04

---

## 試したこと・うまくいかなかったこと

最初、Docker Desktopのインストーラーをそのまま実行した。インストール自体は完了したが、Docker Desktopを開いたらこんなエラーが出た。

```
WSL 2 installation is incomplete.
The WSL 2 Linux kernel is not installed.
```

「WSL 2」の意味もわからず、とりあえず画面の「Restart」を押したが何も変わらなかった。

次に公式ドキュメントを読んで `wsl --install` を実行しようとしたら、管理者権限なしのPowerShellで叩いたせいで権限エラーになった。

```
Error: 0x8007019e
The Windows Subsystem for Linux optional component is not enabled.
```

BIOSの仮想化設定もデフォルトでOFFになっていたので、そこから直す必要があった。

---

## 解決策

### 1. BIOSで仮想化を有効にする

PCを再起動してBIOS画面に入る（Dellなら起動時にF2、HPならF10）。「Intel Virtualization Technology」または「AMD-V」をEnabledに変更して保存・再起動。

### 2. 管理者権限のPowerShellでWSL2をインストール

スタートメニューでPowerShellを右クリック→「管理者として実行」で開く。

```powershell
wsl --install
```

インストールが完了したら再起動する。再起動後にUbuntuのユーザー名とパスワードの設定画面が自動で開くので設定する。

### 3. Docker Desktopをダウンロード・インストール

https://www.docker.com/products/docker-desktop から「Download for Windows」をクリック。

インストーラーを実行して、「Use WSL 2 instead of Hyper-V」にチェックが入っていることを確認してインストール。完了後に再起動。

### 4. 動作確認

PowerShellまたはコマンドプロンプトで実行する。

```bash
docker --version
docker run hello-world
```

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

このメッセージが出たら成功した。

---

## ハマったポイント

- BIOSの仮想化設定がデフォルトでOFFになっていた。`wsl --install` をどれだけ実行してもここが原因でずっと失敗し続けた
- `wsl --install` は管理者権限のPowerShellで実行しないとエラーになる。普通に開いたPowerShellでは権限不足だった
- WSL2のインストール後に再起動しないとDockerが起動しない。再起動を省略して詰まった
- Docker DesktopのインストールでHyper-Vを有効にする選択肢があったが、Windows HomeはHyper-V非対応なのでWSL2の選択肢を選ぶ必要があった
- インストール直後にDocker Desktopを開いたらまたエラーが出て焦ったが、「Start」ボタンを押してデーモンが起動するまで待つだけだった

---

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
