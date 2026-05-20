---
title: 'Dockerのボリュームでデータを永続化する方法'
date: '2026-05-20'
category: 'Docker'
---

## やりたかったこと

Dockerコンテナを削除するとデータが消えてしまっていた。
ボリュームを使うとコンテナを削除してもデータを保持できる。

## 環境

- Docker Desktop（Windows / Mac）
- Docker（Linux）

## ボリュームとは

Dockerコンテナのデータをホストマシンに保存する仕組み。
コンテナを削除してもデータが残る。

## ボリュームの種類

### 1. 名前付きボリューム（推奨）

Dockerが管理するボリューム。

```bash
docker run -d \
  -v mydata:/var/lib/mysql \
  mysql:8
```

### 2. バインドマウント

ホストの特定フォルダをマウントする。

```bash
docker run -d \
  -v /home/user/data:/var/lib/mysql \
  mysql:8
```

開発時にソースコードをマウントするのに便利。

## ボリュームの操作

```bash
docker volume ls                  # ボリューム一覧
docker volume create mydata       # ボリュームを作成
docker volume inspect mydata      # ボリュームの詳細
docker volume rm mydata           # ボリュームを削除
docker volume prune               # 使われていないボリュームを削除
```

## docker-composeでの設定

```yaml
services:
  db:
    image: mysql:8
    volumes:
      - db_data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: password

volumes:
  db_data:
```

## ハマったポイント

- ボリュームなしでコンテナを削除するとデータが全部消える
- `docker compose down` はコンテナを削除するがボリュームは残る
- `docker compose down -v` はボリュームも削除する（注意）
- 開発環境ではバインドマウントが便利

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
