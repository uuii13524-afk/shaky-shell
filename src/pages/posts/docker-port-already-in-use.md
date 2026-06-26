---
title: 'Dockerでポートが既に使用中エラーが出た時の対処法'
date: '2026-05-14'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'Dockerでポートが既に使用中エラーが発生した時の原因調査と解決方法を解説。使用中のポートを確認してプロセスを終了する手順を紹介します。'
---

## やりたかったこと

いつも通り `docker compose up -d` でWebアプリを起動しようとしたら、こんなエラーが出て起動できなかった。

```
Error response from daemon: driver failed programming external connectivity on endpoint
myapp-web-1: Bind for 0.0.0.0:8080 failed: port is already allocated
```

昨日までは普通に動いていたのに、何も変えていないのになぜか急に起動しなくなった。

---

## 環境

- OS: Ubuntu 22.04 LTS
- Docker: 24.0.7
- docker compose: v2.21.0

---

## 試したこと・うまくいかなかったこと

まず `docker ps` でコンテナ一覧を見たが、起動中のコンテナは表示されなかった。「コンテナが動いていないならポートは空いているはずでは？」と思って再度 `docker compose up -d` したが同じエラーだった。

次に `docker compose down` で明示的に停止してから再度upしてみた。それでも同じエラーが出た。

「もしかしてDockerとは別のプロセスがポートを使ってる？」とやっと気づいた。

---

## 解決策

### ポートを使っているプロセスを特定する

**Linux / Mac の場合**

```bash
lsof -i :8080
```

```
COMMAND   PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
node     3142   user   22u  IPv4  85432      0t0  TCP *:8080 (LISTEN)
```

PIDを確認して kill する。

```bash
kill -9 3142
```

**Windows の場合**

```
netstat -ano | findstr :8080
```

```
  TCP    0.0.0.0:8080    0.0.0.0:0    LISTEN    4312
```

タスクマネージャーでPID 4312のプロセスを探して終了する。または:

```
taskkill /PID 4312 /F
```

### 停止中のDockerコンテナを確認・削除する

`docker ps` には停止中のコンテナが表示されない。`-a` フラグが必要。

```bash
docker ps -a
```

```
CONTAINER ID   IMAGE     COMMAND              STATUS    PORTS
a1b2c3d4e5f6   myapp     "node server.js"   Exited(1) 0.0.0.0:8080->8080/tcp
```

ポートを確保したまま Exited になっているコンテナがあった。これを削除する。

```bash
docker rm a1b2c3d4e5f6
```

または全停止コンテナをまとめて掃除する:

```bash
docker container prune
```

### どうしても特定できないときは別ポートを使う

```bash
docker run -d -p 8081:80 nginx
```

---

## ハマったポイント

- `docker ps` だけでは見つからない。`docker ps -a` で Exited のコンテナまで確認しないといけなかった。これに気づくまで30分以上かかった
- 前回 `docker compose up` が途中でエラー終了したとき、コンテナが中途半端な状態でポートを掴んだまま Exited になることがある
- PCを再起動すると治ることがあるが、毎回それをやるのは根本解決になっていなかった。`docker ps -a` で確認して `docker rm` するのが正解
- Mac上のDocker Desktopで `--network host` を使うとポートが見えなくて同様のエラーになることがある。Macでは host ネットワークが動作しない
- `docker compose down` はコンテナを削除するが、`docker compose stop` は停止するだけでコンテナが残る。stopで止めてからupすると同じエラーになる

---

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [Linuxでプロセスを確認・終了する方法（ps/kill）](/posts/linux-process-management)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
