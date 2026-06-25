---
title: 'DockerのイメージとコンテナをPruneで整理する方法（docker image prune・system prune）'
date: '2026-06-06'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'ディスク管理', 'docker system prune', 'イメージ削除', 'コンテナ削除']
en_tags: ['Docker', 'disk cleanup', 'docker system prune', 'image removal', 'container cleanup']
description: 'Dockerの不要なイメージ・コンテナ・ボリューム・ビルドキャッシュを削除する方法。docker image prune・system pruneのオプション・時間フィルター・cron自動化・FAQまとめ。'
---

## ひとことで言うと

```bash
# 未使用リソースをまとめて削除
docker system prune -a

# 未使用イメージだけ削除
docker image prune -a

# 特定のイメージを削除
docker rmi イメージID
```

削除前に `docker system df` で何が容量を使っているか確認する。

---

## やりたかったこと

VPSで長期間Dockerを使っていたら、ディスク使用量が急増してデプロイが失敗するようになった。`df -h` で確認したら `/var` がほぼ満杯で、原因は溜まりに溜まったDockerのイメージとビルドキャッシュだった。

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

---

## 一括削除する（docker system prune）

使っていないリソースをまとめて削除するのが一番手っ取り早い。

```bash
# 停止中コンテナ・未使用イメージ・未使用ネットワークを削除
docker system prune

# ボリュームも含めて削除（注意：データが消える）
docker system prune --volumes

# 確認プロンプトをスキップして全削除
docker system prune -a -f
```

`docker system prune -a` は起動中コンテナが使っていないイメージをすべて削除する（danglingのみではない）。`--volumes` は本当に使っていないか確認してから実行する。DBのデータが吹き飛ぶ。

---

## イメージだけ削除する

```bash
# タグなし（dangling）イメージだけ削除
docker image prune

# 使用中でないイメージをすべて削除
docker image prune -a

# 特定のイメージを削除（名前またはID）
docker rmi nginx:1.25
docker rmi イメージID

# 強制削除（コンテナが参照していても削除）
docker rmi -f イメージID
```

ビルドを繰り返すと `<none>` タグのイメージがどんどん溜まる。これが容量を食う主犯だった。

### 古いイメージだけを削除する（時間フィルター）

```bash
# 24時間以上使われていないイメージを削除
docker image prune -a --filter "until=24h"

# 7日以上使われていないイメージを削除
docker image prune -a --filter "until=168h"
```

---

## コンテナだけ削除する

```bash
# 停止中のコンテナをすべて削除
docker container prune

# 特定のコンテナを削除
docker rm コンテナID

# 強制削除（起動中でも削除）
docker rm -f コンテナID

# 停止中コンテナを一括削除
docker rm $(docker ps -a -q --filter status=exited)
```

---

## ボリュームだけ削除する

```bash
# 使用されていないボリュームをすべて削除
docker volume prune

# ボリューム一覧を確認してから削除
docker volume ls
docker volume rm ボリューム名
```

---

## ビルドキャッシュを削除する

CI/CD環境でビルドを繰り返すと、ビルドキャッシュが数GBになることがある。

```bash
# ビルドキャッシュをすべて削除
docker builder prune -f

# 48時間以上古いキャッシュだけ削除
docker builder prune --filter "until=48h"
```

---

## cronで定期的に自動削除する

```bash
# crontabを編集
crontab -e

# 毎週日曜2時にdocker image pruneを実行
0 2 * * 0 docker image prune -af >> /var/log/docker-cleanup.log 2>&1
```

---

## ハマったポイント

- `docker system prune` は起動中コンテナが使っているイメージは削除しないが、停止中コンテナのイメージは消える
- `docker-compose down` せずに `docker system prune --volumes` するとdocker-composeで管理しているボリュームが消えることがある
- `--volumes` フラグはデータベースのデータも消すので本番環境では慎重に
- `docker image prune -a` は未使用イメージをすべて削除するため、次回起動時に再ダウンロードが必要になる

---

## よくある質問

**Q: 未使用のDockerイメージを削除するコマンドは？**
`docker image prune -a` で未使用イメージをすべて削除できる。`-a` なしではdangling（`<none>`）イメージのみ削除される。

**Q: Dockerイメージをすべて削除したい**
`docker rmi $(docker images -q)` で全削除。起動中コンテナが使っているイメージはエラーになるので `-f` を追加して強制削除。

**Q: `docker image prune` と `docker image prune -a` の違いは？**
`-a` なしはdangling（タグなし`<none>`）イメージのみ削除。`-a` 付きは起動中コンテナが使っていないイメージをすべて削除。

**Q: `docker system prune` はボリュームも削除する？**
デフォルトでは削除しない。`--volumes` を明示的に追加した場合のみボリュームも削除される。

**Q: Dockerのディスク使用量を確認するには？**
`docker system df` でサマリー、`docker system df -v` でイメージ・コンテナごとの詳細が表示される。

---

## 関連記事

- [Dockerイメージとコンテナをdocker rmi・docker rmで削除する方法](/posts/docker-delete-image-container)
- [Dockerの基本コマンドまとめ（run/stop/rm/ps）](/posts/docker-basic-commands)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerfileの基本的な書き方](/posts/docker-dockerfile-basics)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
