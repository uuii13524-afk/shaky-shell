---
title: 'docker-composeで.envファイルを使って環境変数を管理する方法'
date: '2026-06-03'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker-compose', '環境変数', '.env']
en_tags: ['Docker', 'docker-compose', 'environment variables', '.env file']
description: 'docker-composeで.envファイルを使って環境変数を管理する方法を解説。DBパスワードやAPIキーをコードに直書きせず安全に設定できる。'
---
## やりたかったこと

docker-compose.ymlにDBのパスワードやAPIキーをハードコードしていて、Gitにpushするのが怖かった。
.envファイルを使えばうまく管理できると聞いて試してみた。

## .envファイルの基本的な使い方

docker-compose.ymlと同じディレクトリに`.env`ファイルを置くと、自動で読み込まれる。

```
# .env
MYSQL_ROOT_PASSWORD=secret123
MYSQL_DATABASE=myapp
APP_PORT=3000
```

```yaml
# docker-compose.yml
version: '3'
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
    ports:
      - "3306:3306"
  app:
    build: .
    ports:
      - "${APP_PORT}:3000"
```

`.env`に書いた値が`${変数名}`の部分に展開される。`.env`はGitignoreに追加しておく。

## env_fileでコンテナ内部に渡す方法

`environment`キーとは別に、`env_file`キーを使うとファイルごとコンテナに渡せる。

```yaml
services:
  app:
    image: node:18
    env_file:
      - .env
      - .env.local
```

複数ファイルを読み込めるので、`.env`に共通設定・`.env.local`にローカル上書きを分けると便利だった。

## 設定値の確認方法

```bash
# 変数展開後のcompose設定を確認
docker compose config

# コンテナ内の環境変数を直接確認
docker exec -it <container_name> env
```

`docker compose config`を実行すると変数が実際の値に置き換わった状態のymlが表示される。デプロイ前に必ず確認するようにした。

## ハマったポイント

- `.env`は自動でyml内の`${変数名}`を展開するが、`env_file`指定ファイルはコンテナ内部に渡されるだけで展開には使えない
- 値にスペースが含まれる場合はクォートが必要：`MY_VAR="hello world"`
- `.env`を`.gitignore`に追加し忘れてDBパスワードをGitHubにpushしてしまった
- `docker-compose up`後に`.env`を書き換えても、`--env-file`なしだとコンテナを再起動するまで反映されない
- `docker compose config`でおかしな値が見えたらすぐ気づけた

## 関連記事

- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)
- [Dockerfileの基本的な書き方](/posts/docker-dockerfile-basics)
- [動いているDockerコンテナに入ってコマンドを実行する方法（docker exec）](/posts/docker-exec-bash)
- [Dockerのネットワーク設定の基本](/posts/docker-network-basics)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
