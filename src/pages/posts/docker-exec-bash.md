---
title: 'docker execでコンテナ内にbashで入る・コマンドを実行する方法'
date: '2026-06-02'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker exec', 'コンテナ', 'bash', 'デバッグ']
en_tags: ['Docker', 'docker exec', 'container', 'bash', 'debugging']
description: 'docker execで起動中コンテナに入る方法を解説。bash/sh切り替え・オプション一覧・環境変数設定・よくあるエラーの対処をまとめた。'
---

## ひとことで言うと

```bash
# コンテナにbashで入る
docker exec -it コンテナ名 bash

# bashがない場合（Alpineイメージ）
docker exec -it コンテナ名 sh

# コンテナ内で1回だけコマンドを実行
docker exec コンテナ名 cat /etc/nginx/nginx.conf
```

コンテナ名は `docker ps` で確認できる。

---

## docker exec の構文とオプション

```
docker exec [オプション] コンテナ名 コマンド [引数...]
```

| オプション | 説明 |
|---|---|
| `-i` | 標準入力を開いたまま（インタラクティブ） |
| `-t` | 疑似TTYを割り当て（ターミナル表示） |
| `-u` | 実行ユーザーを指定 |
| `-e` | 環境変数を設定 |
| `-w` | 作業ディレクトリを指定 |

シェルに入る時は `-i` と `-t` を必ず両方付ける（`-it`）。`-t` がないとプロンプトが出ない。`-i` がないと入力が即座に閉じられる。

---

## コンテナのシェルに入る

### bash（ほとんどのイメージ）

```bash
docker exec -it my-nginx bash
```

### sh（Alpineベースのイメージはbashがないのでshを使う）

```bash
docker exec -it my-alpine sh
```

### rootで入る（パーミッション調査に便利）

```bash
docker exec -it -u root コンテナ名 bash
```

### 特定ユーザーで入る

```bash
docker exec -it -u www-data コンテナ名 bash
```

---

## コンテナ内に入らずに1回だけコマンドを実行

```bash
# 設定ファイルを確認
docker exec my-nginx cat /etc/nginx/nginx.conf

# ファイル一覧
docker exec my-app ls -la /var/log/

# 環境変数を確認
docker exec my-app env

# プロセスを確認
docker exec my-app ps aux
```

---

## 環境変数を渡す

```bash
# 1つ渡す
docker exec -e DEBUG=true my-app node debug.js

# 複数渡す
docker exec -e NODE_ENV=production -e PORT=8080 my-app node app.js
```

---

## 作業ディレクトリを指定して実行

```bash
docker exec -w /app コンテナ名 ls
```

---

## docker-compose 環境での使い方

docker-compose ではコンテナ名ではなく **サービス名**（`docker-compose.yml` の `services` キー）を使う。

```bash
docker-compose exec web bash
docker-compose exec db psql -U postgres
docker-compose exec web rails db:migrate
```

サービス名は `docker-compose ps` で確認できる。

---

## よく使うデバッグパターン

### ログをリアルタイムで確認

```bash
docker exec コンテナ名 tail -f /var/log/nginx/error.log
```

### コンテナ間のネットワーク疎通を確認

```bash
docker exec my-app curl -v http://db:5432
docker exec my-app ping redis
```

### コンテナ内の開放ポートを確認

```bash
docker exec コンテナ名 ss -tlnp
```

---

## よくあるエラーと対処

### `bash: not found`

Alpine系イメージには bash が入っていない。`sh` を使う：

```bash
docker exec -it コンテナ名 sh
```

### `the input device is not a TTY`

`-t` が抜けている。シェルに入る時は必ず `-it` を付ける。

### `cannot exec in a stopped container`

コンテナが停止中。先に起動する：

```bash
docker start コンテナ名
docker exec -it コンテナ名 bash
```

---

## docker exec vs docker run

| | `docker exec` | `docker run` |
|---|---|---|
| 対象 | 起動中のコンテナ | 新しいコンテナを作成して起動 |
| 用途 | 起動中コンテナのデバッグ | フレッシュな環境で実行 |
| 状態 | 既存のコンテナ状態を使う | クリーンな状態から始まる |

---

## よくある質問

**Q: `docker exec -it` の意味は？**
`-i` が標準入力を開いたまま、`-t` が疑似ターミナルを割り当てる。組み合わせることでインタラクティブなシェル操作が可能になる。

**Q: コンテナ内でコマンドを実行するには？**
`docker exec コンテナ名 コマンド`。例: `docker exec my-app ls /var/log`。

**Q: 起動中のコンテナに入るには？**
`docker exec -it コンテナ名 bash`（Alpineは `sh`）。

**Q: なぜ `bash: not found` になるのか？**
Alpine Linuxベースのイメージはbashを含まない。`sh` を使うと入れる。

**Q: 停止中のコンテナに docker exec できる？**
できない。`docker start コンテナ名` で起動してから実行する。

**Q: docker exec と docker attach の違いは？**
`docker exec` はコンテナ内に新しいプロセスを起動する。`docker attach` はメインプロセス（PID 1）に接続する。デバッグには `exec` を使う。

---

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
