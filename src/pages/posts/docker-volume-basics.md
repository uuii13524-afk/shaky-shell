---
title: 'Dockerのボリュームでデータを永続化する方法'
date: '2026-05-16'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
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

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerfileの基本的な書き方](/posts/docker-dockerfile-basics)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
