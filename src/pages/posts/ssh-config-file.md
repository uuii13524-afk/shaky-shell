---
title: '~/.ssh/configでSSH接続を効率化する方法'
date: '2026-05-27'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['ssh', 'linux', 'サーバー', '設定ファイル', 'VPS']
en_tags: ['ssh', 'linux', 'server', 'config', 'VPS']
description: '~/.ssh/configファイルにホストエイリアスやIdentityFileを設定して、複数サーバーへのSSH接続を効率化する方法を解説。'
---
## やりたかったこと
VPSや踏み台サーバーなど複数のサーバーを管理していて、毎回 `ssh -i ~/.ssh/id_rsa ubuntu@203.0.113.10` みたいな長いコマンドを打つのが面倒だった。
`~/.ssh/config` に設定を書いておけば `ssh myserver` だけで接続できると知ったので試してみた。

## ~/.ssh/configの基本的な書き方

### ファイルを作成する

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/config
chmod 600 ~/.ssh/config
```

configファイルのパーミッションは `600` にしないとSSHが無視するので注意。

### Hostエイリアスを設定する

`~/.ssh/config` に以下を書く。

```
Host myserver
    HostName 203.0.113.10
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

設定後は短いコマンドで接続できる。

```bash
ssh myserver
```

## 複数サーバーをまとめて管理する

```
Host web
    HostName 203.0.113.10
    User ubuntu
    IdentityFile ~/.ssh/id_rsa

Host db
    HostName 203.0.113.20
    User ubuntu
    Port 2222
    IdentityFile ~/.ssh/id_db_rsa

Host github
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_github_rsa
```

これで `ssh web`、`ssh db` と打つだけで接続できるようになった。

## 共通設定をまとめる

`Host *` を使うとすべてのホストに共通設定を適用できる。

```
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    AddKeysToAgent yes
```

- `ServerAliveInterval` : 一定秒ごとに生存確認パケットを送る（接続が切れにくくなる）
- `AddKeysToAgent` : SSH Agentに鍵を自動追加する

## 踏み台サーバー経由の接続（ProxyJump）

踏み台（bastion）を経由して内部サーバーに接続する場合も設定できる。

```
Host bastion
    HostName 203.0.113.1
    User ubuntu
    IdentityFile ~/.ssh/id_rsa

Host internal
    HostName 10.0.0.10
    User ubuntu
    IdentityFile ~/.ssh/id_rsa
    ProxyJump bastion
```

```bash
ssh internal
# bastionを経由してinternalに接続される
```

## ハマったポイント

- configファイルのパーミッションが `644` だとSSHに無視される（必ず `600` にする）
- `IdentityFile` はチルダ始まり（`~/.ssh/id_rsa`）か絶対パスで書く
- `Host` のエイリアス名は大文字小文字を区別しない
- `Port` を省略すると22番ポートになる
- SCPやrsyncでもconfigのエイリアスが使える（`scp myserver:/path/to/file .`）

## 関連記事

- [LinuxのSSH接続の基本（VPSに接続する方法）](/posts/linux-ssh-basics)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
- [Linuxのファイルパーミッション（chmod/chown）完全ガイド](/posts/linux-file-permissions)
- [rsyncでファイルを同期・バックアップする方法](/posts/linux-rsync)
- [VPSにDockerをインストールして本番環境を構築する方法](/posts/vps-docker-setup)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
