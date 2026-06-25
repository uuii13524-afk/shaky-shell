---
title: 'Dockerイメージとコンテナをdocker rmi・docker rmで削除する方法'
date: '2026-06-26'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker rmi', 'docker rm', 'イメージ削除', 'コンテナ削除']
en_tags: ['Docker', 'docker rmi', 'docker rm', 'delete image', 'remove container']
description: 'docker rmiとdocker rmを使ってDockerイメージとコンテナを削除する方法。個別削除・一括削除・強制削除のコマンドをまとめた。'
---

## ひとことで言うと

```bash
# 特定のイメージを削除
docker rmi IMAGE_NAME:TAG

# 特定のコンテナを削除
docker rm CONTAINER_ID

# 停止中のコンテナをすべて削除
docker container prune

# 未使用イメージをすべて削除
docker image prune -a
```

---

## Dockerイメージを削除する

### 名前とタグで削除

```bash
docker rmi nginx:1.25
docker rmi ubuntu:22.04
```

### イメージIDで削除

```bash
# IDを確認
docker images

# IDの先頭数文字でOK
docker rmi a1b2c3
```

### 強制削除（コンテナが参照していても削除）

```bash
docker rmi -f イメージID
```

### 複数イメージを一度に削除

```bash
docker rmi image1 image2 image3
```

### タグなし（dangling）イメージを削除

```bash
docker image prune
```

### 未使用イメージをすべて削除

```bash
docker image prune -a
```

---

## Dockerコンテナを削除する

### 停止中のコンテナを削除

```bash
# コンテナ一覧を確認
docker ps -a

# IDまたは名前で削除
docker rm コンテナID
docker rm my-container
```

### 起動中のコンテナを強制削除

```bash
docker rm -f コンテナID
```

### 停止中のコンテナをすべて削除

```bash
docker container prune
```

### 全コンテナを削除（起動中も含む）

```bash
docker rm -f $(docker ps -a -q)
```

---

## イメージとコンテナをまとめて削除

```bash
# 停止コンテナ・未使用イメージ・未使用ネットワークを削除
docker system prune

# ボリュームも含めて削除
docker system prune --volumes

# 確認なしで全削除
docker system prune -a -f
```

---

## よくあるエラー

### `unable to delete — image is being used by running container`

コンテナが起動中のためイメージを削除できない。先にコンテナを削除する：

```bash
docker rm -f コンテナID
docker rmi イメージID
```

または強制削除：

```bash
docker rmi -f イメージID
```

### `Error: No such image` / `Error: No such container`

名前またはIDが間違っている。一覧で確認する：

```bash
docker images    # イメージ一覧
docker ps -a     # コンテナ一覧
```

---

## よくある質問

**Q: Dockerイメージを削除するコマンドは？**
`docker rmi IMAGE_NAME:TAG`。名前が分からない場合は `docker images` で確認する。

**Q: Dockerコンテナを削除するコマンドは？**
停止中なら `docker rm コンテナID`。起動中は `docker rm -f コンテナID`。

**Q: Dockerイメージをすべて削除したい**
`docker image prune -a` で未使用イメージを一括削除。すべて強制削除するには `docker rmi -f $(docker images -q)`。

**Q: Dockerイメージが削除できない理由は？**
コンテナ（起動中・停止中問わず）がそのイメージを使っている。先に `docker rm -f コンテナID` でコンテナを削除してからイメージを削除する。

**Q: 停止中のコンテナをまとめて削除したい**
`docker container prune` で `exited` 状態のコンテナをすべて削除できる。

**Q: `docker rmi` と `docker image prune` の違いは？**
`docker rmi` は指定したイメージを削除。`docker image prune` はdangling（未使用）イメージをまとめて削除する。

---

## 関連記事

- [Dockerの不要なイメージ・コンテナ・ボリュームを削除する方法](/posts/docker-image-cleanup)
- [Dockerの基本コマンドまとめ（run/stop/rm/ps）](/posts/docker-basic-commands)
- [docker execでコンテナ内でコマンドを実行する方法](/posts/docker-exec-bash)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
