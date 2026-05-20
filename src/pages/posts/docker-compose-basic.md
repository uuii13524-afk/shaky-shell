---
title: 'docker-composeの基本的な使い方'
date: '2026-05-12'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
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

## ConoHa VPSでDockerを本番環境で使う

ローカルでDockerを動かせるようになったら、次は本番サーバーへの展開です。
ConoHa VPSならDockerがすぐに使える環境を低コストで用意できます。

<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4YQYYA" rel="nofollow">ConoHa VPSを見てみる →</a>
<img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4YQYYA" alt="">

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
