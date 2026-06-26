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

docker-compose.ymlにMySQLのパスワードをそのまま書いていた。チームメンバーに「それGitHubに上がってるよ」と指摘されて血の気が引いた。`.env`ファイルで環境変数を管理する方法に切り替えることにした。

---

## 環境

- OS: Ubuntu 22.04 LTS / macOS 13.4
- Docker: 24.0.5
- docker compose: v2.20.2

---

## 試したこと・うまくいかなかったこと

最初はdocker-compose.ymlの中に直接 `environment` キーで書いていた。

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: mysecretpassword123
```

これをそのまま `git add` して `git commit` してしまった。GitHubのリポジトリ（パブリック）にパスワードが丸見えで上がっていた。`git log` を見たら過去のコミットにも残っていた。

次に、シェルの環境変数としてexportしてcompose.ymlから参照しようとした。

```bash
export MYSQL_ROOT_PASSWORD=secret
```

```yaml
environment:
  MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
```

動いたが、ターミナルを閉じるたびに毎回exportし直す必要があって面倒だった。チームで共有する方法もなかった。

---

## 解決策

### .envファイルをdocker-compose.ymlと同じディレクトリに置く

```
# .env
MYSQL_ROOT_PASSWORD=secret123
MYSQL_DATABASE=myapp
APP_PORT=3000
```

docker-composeは自動でこの `.env` を読み込んで、yml内の `${変数名}` に展開する。

```yaml
# docker-compose.yml
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

### .gitignoreに追加する

```bash
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

`.env.example`（ダミー値を入れたサンプル）はコミットして、実際の値が入った `.env` はGit管理外にする。

### env_fileでコンテナ内部にも渡す

`environment`キーに変数名を列挙する方法とは別に、ファイルごとコンテナに渡す方法もある。

```yaml
services:
  app:
    image: node:18
    env_file:
      - .env
      - .env.local
```

`env_file` に指定したファイルの変数はそのままコンテナ内の環境変数になる。複数ファイルを重ねて読めるので、`.env` に共通設定・`.env.local` にローカル上書き用の値を書くと便利だった。

### 設定値が正しく展開されているか確認する

```bash
# 変数展開後のcompose設定を表示する
docker compose config

# コンテナ内の環境変数を直接確認
docker exec -it <container_name> env
```

`docker compose config` を実行すると変数が実際の値に置き換わった状態のymlが表示される。デプロイ前にこれで確認するようにした。

---

## ハマったポイント

- `.env` はyml内の `${変数名}` を展開するが、`env_file` で指定したファイルは展開に使えない。コンテナ内部に渡されるだけ。この2つの役割を混同して1時間ハマった
- 値にスペースや特殊文字が含まれるときはクォートが必要：`MY_VAR="hello world"` / `SECRET="p@ss!word"`
- `.gitignore` に追加し忘れてパスワードを含む `.env` をGitHubにpushしてしまった。GitHubにpushした秘密情報は「削除してpushし直す」だけでは履歴に残るので、パスワードを変更するのが正しい対処
- `docker compose up` 後に `.env` を書き換えても、コンテナを再起動しないと反映されない。`docker compose up --force-recreate` が必要
- `docker compose config` でおかしな値が見えたら `.env` の書き方を確認する。`=` の前後にスペースを入れると読み込まれない

---

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
