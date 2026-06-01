---
title: 'Dockerのボリュームでデータを永続化する方法'
date: '2026-05-16'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'Dockerのボリュームを使ってコンテナのデータを永続化する方法を解説。ボリュームの作成・マウント・バックアップの基本的な使い方を紹介します。'
---

## ボリュームとは

Dockerコンテナのデータをホストマシンに保存する仕組み。コンテナを削除してもデータが残る。

## 名前付きボリューム（推奨）

```bash
docker run -d -v mydata:/var/lib/mysql mysql:8
```

## docker-composeでの設定

```yaml
services:
  db:
    image: mysql:8
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

## ボリュームの操作

```bash
docker volume ls
docker volume create mydata
docker volume rm mydata
docker volume prune
```

## ハマったポイント

- `docker compose down -v` はボリュームも削除する（注意）
- ボリュームなしでコンテナを削除するとデータが全部消える

ボリュームを使ったdocker-composeの構成については[docker-composeの基本的な使い方](/posts/docker-compose-basic)でまとめて確認できる。

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerfileの基本的な書き方](/posts/docker-dockerfile-basics)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
