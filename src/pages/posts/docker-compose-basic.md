---
title: 'docker-composeの基本的な使い方'
date: '2026-05-12'
category: 'Docker'
---

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
```

## 基本コマンド

```bash
docker compose up -d        # バックグラウンドで起動
docker compose down         # 停止・削除
docker compose ps           # 確認
docker compose logs -f      # リアルタイムログ
docker compose exec web bash  # コンテナに入る
```

## ハマったポイント

- `docker-compose`（ハイフンあり）は古い書き方
- `down` はコンテナを削除する。ボリュームも消す場合は `-v`

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
