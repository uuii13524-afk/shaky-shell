---
title: 'Dockerのネットワーク設定の基本（bridge/host/none）'
date: '2026-05-21'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

Dockerコンテナ間の通信設定を理解したかった。
docker-composeで複数コンテナを動かす時にネットワーク設定が重要になる。

## ネットワークの種類

### bridge（デフォルト）

```bash
docker run -d --network bridge nginx
```

- デフォルトのネットワーク
- コンテナ間はIPアドレスで通信できる
- ホストとは別のネットワーク空間

### host

```bash
docker run -d --network host nginx
```

- ホストのネットワークをそのまま使う
- ポートマッピング不要
- Linuxのみ対応（MacやWindowsでは動作が異なる）

### none

```bash
docker run -d --network none nginx
```

- ネットワークなし
- 外部との通信が完全に遮断される

## カスタムネットワークを作成する

```bash
docker network create mynetwork
docker run -d --network mynetwork --name app1 nginx
docker run -d --network mynetwork --name app2 nginx
```

同じネットワーク内のコンテナはコンテナ名で通信できる。

```bash
# app1からapp2に接続
curl http://app2
```

## docker-composeでのネットワーク設定

```yaml
services:
  web:
    image: nginx
    networks:
      - frontend
  db:
    image: mysql:8
    networks:
      - backend
  app:
    image: myapp
    networks:
      - frontend
      - backend

networks:
  frontend:
  backend:
```

## よく使うコマンド

```bash
docker network ls                    # ネットワーク一覧
docker network inspect mynetwork     # ネットワーク詳細
docker network create mynetwork      # ネットワーク作成
docker network rm mynetwork          # ネットワーク削除
docker network connect mynetwork コンテナ名  # コンテナをネットワークに追加
```

## ハマったポイント

- docker-composeは自動でカスタムネットワークを作成する
- 同じネットワーク内でないとコンテナ名で通信できない
- nginx 502エラーはネットワーク設定が原因のことが多い

## 関連記事

- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)
