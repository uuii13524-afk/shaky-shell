---
title: 'LinuxのUFWファイアウォール設定の基本'
date: '2026-05-22'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'UFW', 'ファイアウォール', 'セキュリティ', 'VPS']
en_tags: ['Linux', 'UFW', 'Firewall', 'Security', 'VPS']
description: 'LinuxのUFWファイアウォールの基本設定を解説。UFWの有効化・ポート許可・SSH接続の設定・ステータス確認など、VPS構築時の必須手順を紹介します。'
---

## やりたかったこと

VPSを立ち上げた後、不要なポートを閉じてセキュリティを強化したかった。
UFW（Uncomplicated Firewall）はコマンドが直感的で使いやすかった。

## UFWのインストールと有効化

```bash
# Ubuntuはデフォルトで入っている場合が多い
sudo apt install ufw

# 状態確認
sudo ufw status
```

有効化する前に必ずSSHを許可しておく。これをやらないとVPSにログインできなくなる。

```bash
sudo ufw allow ssh      # ポート22を許可
sudo ufw enable         # UFWを有効化
```

## ポートの許可と拒否

```bash
# ポート番号で指定
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8080

# サービス名で指定
sudo ufw allow http
sudo ufw allow https

# 特定のIPアドレスからのみ許可
sudo ufw allow from 192.168.1.100 to any port 22
```

## ルールの確認と削除

```bash
# 番号付きで一覧表示
sudo ufw status numbered

# 番号指定で削除
sudo ufw delete 3

# ルールを直接指定して削除
sudo ufw delete allow 8080
```

## UFWのリセット

設定をやり直したい時。

```bash
sudo ufw reset
```

リセット後はSSHの許可から再設定する必要がある。

## よく使うポートをまとめて設定する

```bash
# Webサーバー
sudo ufw allow 80
sudo ufw allow 443

# SSH（デフォルトポートを変えた場合）
sudo ufw allow 2222

# nginx + Node.jsの場合（3000はローカルのみ）
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 3000
```

## 現在の設定を確認する

```bash
sudo ufw status verbose
```

```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
```

## ハマったポイント

- `ufw enable` する前に必ず `ufw allow ssh` を実行する（忘れるとSSH接続できなくなる）
- ポート番号とサービス名は同じ意味（`allow 22` と `allow ssh` は同じ）
- `ufw reset` するとSSHの設定も消えるので要注意
- Dockerを使っている場合、UFWのルールをDockerが迂回することがある（`DOCKER-USER` チェーンの設定が必要）
- デフォルトで incoming は deny になっているので、必要なポートだけ明示的に許可する

UFWを設定する前に、[LinuxのSSH接続の基本（VPSに接続する方法）](/posts/linux-ssh-basics)でSSHポートの設定を確認しておくと、誤ってSSH接続を遮断するリスクを減らせる。

## 関連記事

- [LinuxのSSH基本操作まとめ](/posts/linux-ssh-basics)
- [Linuxの基本コマンドまとめ](/posts/linux-basic-commands)
- [VPSにDockerをセットアップする方法](/posts/vps-docker-setup)
- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [Linuxのファイルパーミッションの基本](/posts/linux-file-permissions)

## おすすめのVPS／ドメイン

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
