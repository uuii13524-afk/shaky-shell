---
title: 'Dockerのボリュームでデータを永続化する方法'
date: '2026-05-16'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'Dockerのボリュームを使ってコンテナのデータを永続化する方法を解説。ボリュームの作成・マウント・バックアップの基本的な使い方を紹介します。'
---

## やりたかったこと

MySQLコンテナを立ち上げてデータを入れていたが、`docker compose down` したらデータが全部消えてしまった。「コンテナを落とすたびにDBが初期化されては困る」と気づいてボリュームを調べ始めた。

---

## 環境

- OS: Ubuntu 22.04 LTS
- Docker: 24.0.5
- docker compose: v2.20.2
- MySQL: 8.0.33

---

## 試したこと・うまくいかなかったこと

最初はホストのディレクトリをバインドマウントしてみた。

```yaml
services:
  db:
    image: mysql:8.0
    volumes:
      - ./mysql-data:/var/lib/mysql
```

これで `docker compose down` してもデータが残るようになった。ただし、ホスト側の `./mysql-data` ディレクトリのパーミッションがrootになってしまって、ホストから中身を確認したり操作しようとすると `Permission denied` が出た。

```
ls: cannot open directory './mysql-data': Permission denied
```

次に、バインドマウントをそのままVPSに持っていったら、MySQLの起動時にこんなエラーが出て動かなくなった。

```
[ERROR] InnoDB: Operating system error number 13 in a file operation.
```

OS側のパーミッションとMySQLの期待するディレクトリ権限がズレていた。

---

## 解決策

Dockerが管理する名前付きボリュームを使うと、こうしたパーミッション問題が起きない。

### 名前付きボリュームで起動する

```bash
docker run -d \
  -e MYSQL_ROOT_PASSWORD=secret123 \
  -v mydata:/var/lib/mysql \
  mysql:8.0
```

### docker-composeで設定する

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secret123
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

`volumes:` セクションを書かないとエラーになるので注意。

### ボリュームの操作コマンド

```bash
docker volume ls                  # ボリューム一覧
docker volume create mydata       # 手動作成
docker volume inspect mydata      # 詳細確認（保存先パスも分かる）
docker volume rm mydata           # 削除
docker volume prune               # 使われていないボリュームを全削除
```

### バックアップとリストア

```bash
# バックアップ（ボリュームの中身をtarで固める）
docker run --rm \
  -v mydata:/source \
  -v $(pwd):/backup \
  alpine tar czf /backup/mydata-backup.tar.gz -C /source .

# リストア
docker run --rm \
  -v mydata:/target \
  -v $(pwd):/backup \
  alpine tar xzf /backup/mydata-backup.tar.gz -C /target
```

---

## ハマったポイント

- `docker compose down` は停止のみ、ボリュームは残る。`docker compose down -v` はボリュームも一緒に削除する。うっかり `-v` をつけてDBのデータを全部吹き飛ばしたことがある
- バインドマウント（`./ホストパス:/コンテナパス`）とボリューム（`名前:/コンテナパス`）は別物。バインドマウントはホストのパスを直接使うのでパーミッション問題が起きやすい
- `docker volume inspect` で実際の保存先（`/var/lib/docker/volumes/mydata/_data`）が確認できる。ボリュームがどこにあるか分からなくて焦ったがこれで解決した
- `docker compose up` で再起動してもボリュームのデータはそのまま引き継がれる。MySQLの初期化スクリプト（`/docker-entrypoint-initdb.d/`）はボリュームが空のときだけ実行される仕様で、データが残っていると実行されない

---

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerfileの基本的な書き方](/posts/docker-dockerfile-basics)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
