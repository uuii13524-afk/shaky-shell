---
title: 'Dockerのネットワーク設定の基本（bridge/host/none）'
date: '2026-05-21'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'Dockerのbridge・host・noneネットワークの違いと使い方を解説。カスタムネットワークの作成やdocker-composeでのネットワーク設定方法も紹介します。'
---

## やりたかったこと

docker-composeでNginx + Node.js + MySQLの3コンテナ構成を動かそうとした。NginxからNode.jsにリクエストを転送したら `502 Bad Gateway` が出て、コンテナ名でアクセスしているのになぜ通らないのか全然わからなかった。調べているうちにDockerのネットワークの仕組みを理解していなかったのが原因だと気づいた。

---

## 環境

- OS: Ubuntu 22.04 LTS
- Docker: 24.0.5
- docker compose: v2.20.2

---

## 試したこと・うまくいかなかったこと

最初のdocker-compose.ymlはこんな感じだった。

```yaml
services:
  nginx:
    image: nginx:1.25
    ports:
      - "80:80"
  app:
    image: node:18-alpine
    command: node server.js
```

Nginxの設定ファイルに `proxy_pass http://app:3000;` と書いたが、502が出続けた。`docker exec` でNginxコンテナに入って `curl http://app:3000` を叩いたら `Could not resolve host: app` と出た。コンテナ名でDNSが解決できていなかった。

調べると、デフォルトのbridgeネットワークではコンテナ名でのDNS解決が使えないことがわかった。カスタムネットワークが必要だった。

---

## ネットワークの種類

### bridge（デフォルト）

`docker run` でネットワークを指定しないと自動で使われる。

```bash
docker run -d --network bridge nginx
```

- コンテナ同士はIPアドレスで通信できるが、コンテナ名では通信できない
- ホストとは別のネットワーク空間

### host

```bash
docker run -d --network host nginx
```

- ホストのネットワークをそのまま使う
- `-p` によるポートマッピング不要
- Linuxのみ対応。MacやWindowsのDocker Desktopでは動作しない

### none

```bash
docker run -d --network none nginx
```

- ネットワークなし。外部との通信が完全に遮断される
- セキュリティ要件で外部通信を禁止したいコンテナに使う

---

## カスタムネットワークでコンテナ名を使う

カスタムネットワークを作成すると、同一ネットワーク内のコンテナがコンテナ名でDNS解決できるようになる。

```bash
docker network create mynetwork
docker run -d --network mynetwork --name app1 nginx
docker run -d --network mynetwork --name app2 nginx

# app1のコンテナ内からapp2にアクセス
docker exec app1 curl http://app2
```

---

## docker-composeでのネットワーク設定

docker-composeは同一ファイル内のサービスを同じカスタムネットワークに自動で接続する。だからコンテナ名でのDNS解決が最初から使える。

```yaml
services:
  nginx:
    image: nginx:1.25
    ports:
      - "80:80"
    networks:
      - frontend

  app:
    image: node:18-alpine
    command: node server.js
    networks:
      - frontend
      - backend

  db:
    image: mysql:8.0
    networks:
      - backend

networks:
  frontend:
  backend:
```

この構成だと `app` からは `db` という名前でMySQLに接続でき、外部からはdbに直接アクセスできない。

---

## よく使うコマンド

```bash
docker network ls                              # ネットワーク一覧
docker network inspect mynetwork              # 詳細（どのコンテナが参加しているか）
docker network create mynetwork               # ネットワーク作成
docker network rm mynetwork                   # ネットワーク削除
docker network connect mynetwork コンテナ名    # 起動中のコンテナをネットワークに追加
docker network disconnect mynetwork コンテナ名 # ネットワークから切断
```

---

## ハマったポイント

- デフォルトbridgeネットワークではコンテナ名でDNSが引けない。`docker run` で繋いだコンテナ間で通信しようとすると詰まるのはこれが原因だった
- docker-composeはデフォルトでカスタムネットワーク（`プロジェクト名_default`）を自動作成するが、手動の `docker run` ではそのネットワークに参加しない。compose外からcomposeのコンテナに名前でアクセスしようとして通らなかった
- `--network host` はMac/WindowsのDocker Desktopでは動かない。Linuxのみ。これを知らずにローカル（Mac）で試して動いたスクリプトがVPS（Linux）で挙動が違ってしばらく混乱した
- `502 Bad Gateway` の原因がネットワーク設定だとわかるまで2時間かかった。`docker exec` でコンテナ内から `curl` を叩いて `Could not resolve host` を確認するのが最速の切り分け方法

---

## 関連記事

- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
