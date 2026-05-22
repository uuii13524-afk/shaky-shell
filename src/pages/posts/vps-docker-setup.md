---
title: 'VPSにDockerをインストールして本番環境を構築する方法'
date: '2026-05-21'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

VPS（ConoHa・XServer等）を契約してDockerで本番環境を構築したかった。
ローカルと同じ手順でDockerを使える環境を作る。

## 環境

- Ubuntu 22.04 LTS（VPS）
- Docker
- ConoHa VPS / XServer VPS

## 手順

### 1. VPSにSSHで接続

```bash
ssh root@VPSのIPアドレス
```

### 2. システムを更新

```bash
apt update && apt upgrade -y
```

### 3. Dockerをインストール

```bash
curl -fsSL https://get.docker.com | sh
```

### 4. 動作確認

```bash
docker --version
docker run hello-world
```

### 5. Docker Composeをインストール

```bash
apt install docker-compose-plugin -y
docker compose version
```

### 6. 一般ユーザーでDockerを使えるようにする

```bash
usermod -aG docker ユーザー名
```

ログアウトして再ログインすると反映される。

## セキュリティ設定

### SSHのrootログインを無効にする

```bash
nano /etc/ssh/sshd_config
# PermitRootLogin no に変更
systemctl restart sshd
```

### ファイアウォールの設定

```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

## ハマったポイント

- `curl | sh` でインストールすると最新版が入る
- rootでDockerを使うのはセキュリティリスクがある
- UFWとDockerの相性に注意が必要

## VPSを選ぶなら

<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4YQYYA" rel="nofollow">ConoHa VPSを見てみる →</a>
<img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4YQYYA" alt="">

## 関連記事

- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)


## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
