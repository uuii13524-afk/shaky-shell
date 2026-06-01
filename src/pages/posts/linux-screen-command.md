---
title: 'screenコマンドでSSHセッションを永続化する方法'
date: '2026-06-01'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'screen', 'SSH', 'VPS', 'サーバー管理']
en_tags: ['Linux', 'screen', 'SSH', 'VPS', 'server management']
description: 'Linuxのscreenコマンドを使ってSSH切断後もプロセスを継続実行する方法。基本操作・セッション管理・よく使うキーバインドをまとめた。'
---
## やりたかったこと

VPSで長時間かかる処理を走らせたまま、ターミナルを閉じたかった。
SSH接続が切れるとプロセスも死ぬので、screenを使ってセッションを永続化することにした。

## screenのインストール

```bash
# Ubuntu/Debian
sudo apt install screen

# CentOS/RHEL
sudo yum install screen
```

インストール済みかどうかは `screen --version` で確認できる。

## 基本的な使い方

### 新しいセッションを作成する

```bash
screen
```

そのままセッションが始まる。名前をつけておくと後で分かりやすい。

```bash
screen -S mysession
```

### セッションをデタッチする（バックグラウンドに回す）

`Ctrl + A` を押してから `D` を押す。

```
[detached from 12345.mysession]
```

このメッセージが出たらデタッチ成功。SSH接続を切断しても、セッション内のプロセスは動き続ける。

### 既存セッションに再接続する

```bash
# セッション一覧を確認
screen -ls
```

```
There is a screen on:
        12345.mysession (Detached)
1 Socket in /run/screen/S-user.
```

```bash
# セッション名を指定して再接続
screen -r mysession

# IDを指定する場合
screen -r 12345
```

### セッションを終了する

セッション内で `exit` を実行するか、`Ctrl + D` で終了できる。

## よく使うキーバインド

| 操作 | キー |
|------|------|
| デタッチ | `Ctrl + A` → `D` |
| 新しいウィンドウを作成 | `Ctrl + A` → `C` |
| ウィンドウ一覧を表示 | `Ctrl + A` → `"` |
| 次のウィンドウへ移動 | `Ctrl + A` → `N` |
| 前のウィンドウへ移動 | `Ctrl + A` → `P` |
| セッションを強制終了 | `Ctrl + A` → `K` |

## 複数セッションの管理

```bash
# セッション一覧
screen -ls

# 特定のセッションを強制終了（セッション内に入れない時）
screen -S mysession -X quit
```

デタッチ済みセッションへの再接続時にエラーが出る場合は `-d -r` を使う。

```bash
# 接続中の別クライアントを切り離して再接続
screen -d -r mysession
```

## ハマったポイント

- `screen -r` でセッションが見つからない時はセッション名ではなくIDで指定すると解決することがある
- SSH接続が切れた後に再接続すると `(Attached)` 状態になっている場合がある。その場合は `screen -d -r` を使う
- 複数ユーザーが同じVPSを使う場合、`screen -ls` には自分のセッションしか見えない
- screenセッション内でさらにscreenを起動するとキーバインドが衝突するので注意
- 長期運用なら screen より tmux のほうが機能が豊富なことも覚えておく

## 関連記事

- [LinuxのSSH接続の基本（VPSに接続する方法）](/posts/linux-ssh-basics)
- [~/.ssh/configでSSH接続を効率化する方法](/posts/ssh-config-file)
- [Node.jsアプリをPM2で本番環境に常駐させる方法](/posts/node-pm2-setup)
- [systemdでサービスを管理する方法（start/stop/enable/status）](/posts/linux-systemd-service)
- [Linuxでプロセスを確認・終了する方法（ps/kill）](/posts/linux-process-management)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
