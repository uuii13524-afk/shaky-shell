---
title: 'Dockerの不要なイメージ・コンテナ・ボリュームを削除してディスクを解放する方法'
date: '2026-06-06'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'ディスク管理', 'docker system prune', 'イメージ削除', 'コンテナ削除']
en_tags: ['Docker', 'disk cleanup', 'docker system prune', 'image removal', 'container cleanup']
description: 'Dockerの不要なイメージ・コンテナ・ボリュームを削除してディスク容量を確保する方法。docker system pruneの使い方と注意点をまとめた。'
---
## やりたかったこと
VPSで長期間Dockerを使っていたら、ディスク使用量が急増してデプロイが失敗するようになった。
`df -h` で確認したら `/var` がほぼ満杯で、原因は溜まりに溜まったDockerのイメージとビルドキャッシュだった。

## 現状を確認する

まず何がどれだけ使っているかを確認する。

```bash
docker system df
```

出力例：

```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          23        5         8.2GB     6.1GB (74%)
Containers      12        3         142MB     98MB (69%)
Local Volumes   8         4         2.3GB     1.1GB (47%)
Build Cache     0         0         0B        0B
```

`RECLAIMABLE` が解放できるサイズ。これを見てから削除を判断した。

## 一括削除する（docker system prune）

使っていないリソースをまとめて削除するのが一番手っ取り早い。

```bash
# 停止中コンテナ・未使用イメージ・未使用ネットワークを削除
docker system prune

# ボリュームも含めて削除（注意：データが消える）
docker system prune --volumes

# 確認プロンプトをスキップ
docker system prune -f
```

`--volumes` は本当に使っていないか確認してから実行する。DBのデータが吹き飛ぶ。

## イメージだけ削除する

```bash
# タグなし（dangling）イメージだけ削除
docker image prune

# 使用中でないイメージをすべて削除
docker image prune -a

# 特定のイメージを削除
docker rmi イメージID

# 停止中コンテナで使われているイメージも含めて強制削除
docker rmi -f イメージID
```

ビルドを繰り返すと `<none>` タグのイメージがどんどん溜まる。これが容量を食う主犯だった。

## コンテナだけ削除する

```bash
# 停止中のコンテナをすべて削除
docker container prune

# 特定のコンテナを削除
docker rm コンテナID

# 強制削除（起動中でも削除）
docker rm -f コンテナID

# 停止中コンテナのIDを一覧表示して確認
docker ps -a --filter status=exited
```

## ボリュームだけ削除する

```bash
# 使用されていないボリュームをすべて削除
docker volume prune

# ボリューム一覧を確認してから削除
docker volume ls
docker volume rm ボリューム名
```

## ビルドキャッシュを削除する

CI/CD環境でビルドを繰り返すと、ビルドキャッシュが数GBになることがある。

```bash
# ビルドキャッシュをすべて削除
docker builder prune

# 確認なしで削除
docker builder prune -f
```

## ハマったポイント
- `docker system prune` は起動中コンテナが使っているイメージは削除しないが、停止中コンテナのイメージは消える
- `docker-compose down` せずに `docker system prune` するとdocker-composeで管理しているボリュームが消えることがある
- `--volumes` フラグはデータベースのデータも消すので本番環境では慎重に
- `docker image prune -a` は未使用イメージをすべて削除するため、次回起動時に再ダウンロードが必要になる
- cron で定期的に `docker image prune -f` を実行するとディスク逼迫を防げた

## 関連記事
- [Dockerの基本コマンドまとめ（run/stop/rm/ps）](/posts/docker-basic-commands)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [VPSにDockerをインストールして本番環境を構築する方法](/posts/vps-docker-setup)
- [Dockerfileの基本的な書き方](/posts/docker-dockerfile-basics)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
