---
title: '動いているDockerコンテナに入ってコマンドを実行する方法（docker exec）'
date: '2026-06-02'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker exec', 'コンテナ', 'bash', 'デバッグ']
en_tags: ['Docker', 'docker exec', 'container', 'bash', 'debugging']
description: 'docker execコマンドで起動中のコンテナ内にbashで入る方法を解説。デバッグ時のログ確認やファイル操作など実践的な使い方をまとめた。'
---
## やりたかったこと
起動中のDockerコンテナに直接入って、中のファイルを確認したりコマンドを実行したかった。
本番に近い環境でデバッグする時に毎回調べていたのでまとめてみた。

## docker exec の基本的な使い方

### コンテナに bash で入る

```bash
docker exec -it <コンテナ名またはID> bash
```

`-i`（インタラクティブ）と `-t`（疑似TTY割り当て）を組み合わせる。
コンテナ名は `docker ps` で確認できる。

```bash
docker ps
# CONTAINER ID   IMAGE     COMMAND   NAMES
# a1b2c3d4e5f6   nginx     ...       my-nginx
docker exec -it my-nginx bash
```

### bash が入っていない場合は sh を使う

Alpine Linuxベースのイメージには bash がないことが多い。

```bash
docker exec -it <コンテナ名> sh
```

### 1回だけコマンドを実行する

コンテナ内に入らずに単発でコマンドを実行したい場合。

```bash
docker exec <コンテナ名> cat /etc/nginx/nginx.conf
docker exec <コンテナ名> ls -la /var/log/nginx/
```

### 環境変数を確認する

```bash
docker exec <コンテナ名> env
```

## docker-compose 環境での使い方

docker-compose を使っている場合はサービス名で指定できる。

```bash
# docker-compose.yml の services 名で指定
docker-compose exec web bash
docker-compose exec db psql -U postgres
```

`docker exec` との違いは、`docker-compose exec` はコンテナ名ではなくサービス名を使う点。

### 特定のユーザーで実行する

```bash
# root で入る（パーミッション系の確認に便利）
docker exec -it -u root <コンテナ名> bash

# 別のユーザーで実行
docker exec -it -u www-data <コンテナ名> bash
```

## よく使うデバッグパターン

### ログファイルを直接確認する

```bash
docker exec <コンテナ名> tail -f /var/log/nginx/error.log
```

### プロセスを確認する

```bash
docker exec <コンテナ名> ps aux
```

### ネットワーク疎通を確認する

```bash
# curl が入っているか確認してから実行
docker exec <コンテナ名> curl -v http://other-container:3000
```

## ハマったポイント

- `bash: not found` が出たら `sh` に切り替える。Alpine系は bash が入っていない
- コンテナが停止中だと `docker exec` は使えない。`docker start` で起動してから実行する
- `-it` を忘れると入力を受け付けず即終了する。シェルに入る時は必ず付ける
- `docker-compose exec` でサービス名を間違えると `no such service` になる。`docker-compose ps` でサービス名を確認する
- rootで作ったファイルがホストからパーミッション不足で見えないことがある。ユーザー指定（`-u`）を使うと解決することが多い

## 関連記事

- [Dockerの基本コマンドまとめ（run/stop/rm/ps）](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerfileの基本的な書き方](/posts/docker-dockerfile-basics)
- [Dockerのネットワーク設定の基本（bridge/host/none）](/posts/docker-network-basics)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
