---
title: 'docker-composeの基本的な使い方'
date: '2026-05-20'
category: 'Docker'
---

## やりたかったこと

複数のDockerコンテナをまとめて管理したかった。
docker-composeを使うと複数コンテナの起動・停止を1コマンドでできる。

## 環境

- Docker Desktop（Windows / Mac）
- Docker + Docker Compose（Linux）

## docker-compose.ymlの基本構成

```yaml
version: '3'
services:
  web:
    image: nginx
    ports:
      - "8080:80"
  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: mydb
```

## 基本コマンド

```bash
docker compose up           # コンテナを起動
docker compose up -d        # バックグラウンドで起動
docker compose down         # コンテナを停止・削除
docker compose ps           # 起動中のコンテナ確認
docker compose logs         # ログを表示
docker compose logs -f      # リアルタイムでログを表示
docker compose exec web bash  # コンテナに入る
docker compose build        # イメージをビルド
docker compose restart      # コンテナを再起動
```

## よく使うdocker-compose.ymlの設定

### ボリューム（データを永続化する）

```yaml
services:
  db:
    image: mysql:8
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

### 環境変数を.envファイルから読み込む

```yaml
services:
  web:
    image: nginx
    env_file:
      - .env
```

### 依存関係を設定する

```yaml
services:
  web:
    image: nginx
    depends_on:
      - db
  db:
    image: mysql:8
```

## ハマったポイント

- `docker-compose` （ハイフンあり）は古い書き方。新しくは `docker compose`（スペース）
- `down` はコンテナを削除する。データも消えることがあるので注意
- ボリュームを使わないとコンテナ削除時にデータが消える
- `depends_on` は起動順序を制御するが、サービスの準備完了を保証しない

## 関連記事

- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
