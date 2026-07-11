---
title: 'docker run コマンドの使い方｜主要オプションとよくあるエラーまとめ'
date: '2026-07-11'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker run', 'トラブルシューティング']
description: 'docker runコマンドの基本構文と-d、-p、-v、--name、--rm等の主要オプションを解説。コンテナがすぐ終了する・ポート競合・イメージが見つからない等のよくあるエラーの対処法も紹介。'
---

## ひとことで言うと

```bash
# バックグラウンドで起動し、ポートとボリュームを指定する基本形
docker run -d --name my-container -p 8080:80 -v /host/path:/container/path nginx
```

---

## やりたかったこと / 現象

`docker pull` でイメージを取得したものの、実際にコンテナとして動かす方法がわからない。あるいは `docker run` を実行したらすぐにコンテナが終了してしまう、ポートが競合してエラーになる——そんな場面で `docker run` のオプションを一つずつ確認したくなった人向けの記事です。

`docker run` はイメージからコンテナを作成し起動するコマンドで、Dockerを使う上でもっとも基本かつ利用頻度の高いコマンドです。オプションの組み合わせ次第で挙動が大きく変わるため、代表的なパターンを押さえておくと迷いません。

---

## 環境

- Docker: 20.10以降で動作確認
- OS: Linux / macOS / Windows（WSL2）

---

## 解決策

### 1. 基本構文

```bash
docker run [オプション] <イメージ名> [コマンド]
```

イメージがローカルに存在しない場合は自動的に `docker pull` が実行されてから起動します。

### 2. バックグラウンドで起動する（-d）

```bash
docker run -d nginx
```

`-d`（`--detach`）を付けないとフォアグラウンドで実行され、ターミナルを占有してしまいます。

### 3. コンテナに名前を付ける（--name）

```bash
docker run -d --name my-nginx nginx
```

名前を指定しない場合はランダムな名前が自動で割り当てられます。`docker ps` や `docker logs` で扱いやすくするため、名前を付けておくのがおすすめです。

### 4. ポートを公開する（-p）

```bash
docker run -d -p 8080:80 nginx
```

`-p <ホスト側ポート>:<コンテナ側ポート>` の形式で指定します。ホスト側の `8080` にアクセスすると、コンテナ内の `80` 番ポートに転送されます。

### 5. ボリュームをマウントする（-v）

```bash
docker run -d -v /host/path:/container/path nginx
```

ホスト側のディレクトリをコンテナ内にマウントします。データの永続化や設定ファイルの共有によく使われます。名前付きボリュームを使う場合は以下のようにします。

```bash
docker run -d -v my-volume:/container/path nginx
```

### 6. 環境変数を渡す（-e）

```bash
docker run -d -e NODE_ENV=production -e PORT=3000 my-app
```

### 7. コンテナ終了時に自動削除する（--rm）

```bash
docker run --rm -it ubuntu bash
```

動作確認用の一時的なコンテナなど、終了後にコンテナを残したくない場合に使います。

### 8. 対話的にシェルへ入る（-it）

```bash
docker run -it ubuntu bash
```

`-i`（標準入力を維持）と `-t`（疑似端末を割り当て）を組み合わせることで、コンテナ内のシェルを対話的に操作できます。

### 9. よく使う組み合わせ

```bash
docker run -d --name my-app --restart unless-stopped -p 3000:3000 -v ./data:/app/data -e NODE_ENV=production my-app:latest
```

---

## よくあるエラーと対処

### コンテナがすぐに終了してしまう

```
$ docker ps
(何も表示されない)
```

`docker run` で起動したメインプロセスが終了すると、コンテナ自体も停止します。ベースイメージが `bash` や `sh` のみの場合、フォアグラウンドで動き続けるプロセスがないため即座に終了します。`docker logs <コンテナ名>` で終了直前の出力を確認しましょう。

```bash
docker logs my-container
docker ps -a
```

### `Error response from daemon: driver failed programming external connectivity`

指定したホスト側ポートがすでに他のプロセスで使用されている場合に発生します。

```bash
# 使用中のポートを確認
lsof -i :8080

# 別のポートを指定して再実行
docker run -d -p 8081:80 nginx
```

### `Unable to find image 'xxx:latest' locally`

イメージ名やタグのタイプミス、またはローカルにもレジストリにも存在しない場合に表示されます。エラー自体は問題なければ自動的にpullが続行されますが、存在しないイメージ名の場合は失敗します。

```bash
docker images
docker search <イメージ名>
```

### `docker: Error response from daemon: Conflict. The container name "/my-app" is already in use`

同じ名前のコンテナがすでに存在しています。既存のコンテナを削除するか、別の名前を指定してください。

```bash
docker rm my-app
# または
docker run -d --name my-app-2 nginx
```

### ボリュームマウントしたファイルが反映されない

パスの指定ミスや相対パスの解釈違いが原因であることが多いです。絶対パスで指定するか、`$(pwd)` を使うと確実です。

```bash
docker run -d -v $(pwd)/data:/app/data my-app
```

---

## よくある質問

**Q: `docker run` と `docker start` の違いは？**
`docker run` はイメージから新しいコンテナを作成して起動します。一方 `docker start` はすでに存在する（停止中の）コンテナを再起動するコマンドです。

**Q: `docker run` と `docker create` の違いは？**
`docker create` はコンテナを作成するだけで起動はしません。`docker run` は内部的に `docker create` と `docker start` を続けて実行しているのと同じです。

**Q: 同じイメージから複数のコンテナを起動できますか？**
できます。`--name` を省略するか毎回異なる名前を指定すれば、同じイメージから何個でもコンテナを起動できます。

**Q: `-p 8080:80` の代わりに `-P` と大文字にするとどうなりますか？**
`-P`（大文字）は、Dockerfileの `EXPOSE` で指定されたすべてのポートをランダムなホストポートに自動で割り当てます。

**Q: コンテナ起動後にオプションを変更できますか？**
できません。`-p` や `-v` などのオプションはコンテナ作成時にのみ指定可能です。変更したい場合はコンテナを削除して作り直す必要があります。

---

## 関連記事

- [docker exec でコンテナ内のbashに入る方法](/posts/docker-exec-bash)
- [docker ps コマンドの使い方](/posts/docker-ps-command)
- [docker inspect コマンドの使い方](/posts/docker-inspect-command)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
