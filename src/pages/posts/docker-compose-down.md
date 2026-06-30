---
title: 'docker compose down の使い方｜コンテナ・ネットワーク・ボリュームを完全削除'
date: '2026-06-30'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker-compose', 'コンテナ削除']
description: 'docker compose down でコンテナを停止・削除する方法を解説。ボリュームやイメージも含めて完全削除するオプションも紹介します。'
---

## ひとことで言うと

```bash
# コンテナとネットワークを停止・削除
docker compose down

# ボリュームも一緒に削除
docker compose down -v

# イメージも含めて全削除
docker compose down --rmi all -v
```

---

## やりたかったこと / 現象

`docker compose up` で起動した環境を片付けたい。`docker compose stop` との違いがわからない。ボリュームも一緒に消したい。

---

## 環境

- Docker Engine 24.x 以降
- Docker Compose v2（`docker compose` コマンド）
- OS: Ubuntu 22.04 / macOS / WSL2

> **注意:** 旧来の `docker-compose`（v1）でも同じオプションが使えます。

---

## 解決策

### 基本の使い方

```bash
docker compose down
```

このコマンド1本で以下がまとめて実行されます:

1. 実行中のコンテナを**停止**
2. コンテナを**削除**
3. Compose が作成したネットワークを**削除**

ボリューム・イメージは**残ります**。

### ボリュームも削除したい場合

```bash
docker compose down -v
# または
docker compose down --volumes
```

`-v` を付けると、`docker-compose.yml` の `volumes:` セクションで定義した**名前付きボリューム**も削除されます。データベースのデータなど永続化データが消えるため注意してください。

### イメージも削除したい場合

```bash
# Compose で使用したイメージをすべて削除
docker compose down --rmi all

# ローカルビルドしたイメージのみ削除
docker compose down --rmi local
```

### 全部まとめて削除（開発環境リセット）

```bash
docker compose down --rmi all -v
```

これで「コンテナ + ネットワーク + ボリューム + イメージ」をすべて削除できます。

### 特定のサービスだけ停止・削除

```bash
# web サービスのコンテナだけ削除
docker compose down web
```

### タイムアウトを指定する

```bash
# 停止まで最大60秒待つ（デフォルト10秒）
docker compose down -t 60
```

---

## docker compose stop との違い

| コマンド | コンテナ停止 | コンテナ削除 | ネットワーク削除 |
|---------|------------|------------|----------------|
| `docker compose stop` | ✅ | ❌ | ❌ |
| `docker compose down` | ✅ | ✅ | ✅ |

`stop` は「一時停止」、`down` は「後片付けまで含めた終了」です。  
再開するなら `stop` → `start`、環境を消すなら `down` を使います。

---

## よくあるエラーと対処

### `Error response from daemon: removal of container ... is already in progress`

別のプロセスが同じコンテナを操作中です。少し待ってから再実行してください。

```bash
# 強制削除が必要な場合
docker rm -f $(docker ps -aq)
```

### `network ... has active endpoints`

ネットワークに他のコンテナが接続されています。

```bash
# 接続中のコンテナを確認
docker network inspect <network_name>

# 全コンテナを停止してから再実行
docker compose down
```

### `volume is in use`

ボリュームが別のコンテナに使われています。

```bash
# ボリュームを使用中のコンテナを確認
docker ps -a --filter volume=<volume_name>

# コンテナを削除してからボリュームを削除
docker compose down -v
```

### Permission denied（ソケットエラー）

```bash
sudo docker compose down
# または docker グループに自分を追加
sudo usermod -aG docker $USER
```

---

## よくある質問

**Q: `docker compose down` と `docker compose rm` の違いは何ですか？**  
`down` はコンテナの停止→削除→ネットワーク削除まで一括で行います。`rm` は**停止済みコンテナのみ**を削除する（停止はしない）コマンドです。

**Q: ボリュームを削除し忘れました。後から消せますか？**  
はい。`docker volume ls` で名前を確認して `docker volume rm <名前>` で削除できます。使われていないボリュームをまとめて消す場合は `docker volume prune` も使えます。

**Q: `down` 後にデータが消えていました。なぜですか？**  
`-v` オプションを付けていた場合、名前付きボリュームも削除されます。また、`docker-compose.yml` でボリュームを定義せずにコンテナ内にデータを書いていた場合も、コンテナ削除とともにデータは消えます。

**Q: `docker compose down` してもイメージは残りますか？**  
デフォルトではイメージは残ります。イメージも削除したい場合は `--rmi all` オプションを追加してください。

**Q: `docker-compose.yml` が複数ある場合はどうしますか？**  
`-f` オプションでファイルを指定できます。

```bash
docker compose -f docker-compose.prod.yml down
```

**Q: 停止せずにコンテナだけ削除できますか？**  
`docker compose down` は内部で自動的に停止してから削除するので、実行中のコンテナがあっても安全に使えます。

---

## 関連記事

- [docker compose up の使い方](/posts/docker-compose-basic)
- [docker system prune で不要なリソースを一掃する](/posts/docker-system-prune)
- [docker volume の基本](/posts/docker-volume-basics)
- [docker logs でコンテナのログを確認する](/posts/docker-logs)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
