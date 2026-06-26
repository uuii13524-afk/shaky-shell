---
title: 'docker compose down の使い方｜コンテナ・ネットワーク・ボリュームを完全削除する方法'
date: '2026-06-26'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker-compose', 'コンテナ管理']
description: 'docker compose down の基本から --volumes・--rmi オプションまで解説。コンテナ・ネットワーク・ボリュームを一括削除する方法を手順付きで紹介します。'
---

## ひとことで言うと

```bash
# コンテナとネットワークを停止・削除
docker compose down

# ボリュームも一緒に削除（データも消える）
docker compose down --volumes

# イメージも削除
docker compose down --rmi all
```

---

## やりたかったこと / 現象

`docker compose up` で起動した複数コンテナを一括停止・削除したい。`docker stop` をコンテナごとに実行するのは手間なので、まとめて片付ける方法を知りたい。

---

## 環境

- Docker 24.x 以上
- Docker Compose V2（`docker compose` コマンド）
- OS: Ubuntu 22.04 / macOS

> **補足:** `docker-compose`（ハイフン付き）は Compose V1 です。現在は `docker compose`（スペース）の V2 が標準です。

---

## 解決策

### 基本: コンテナとネットワークを削除

```bash
docker compose down
```

`docker-compose.yml` があるディレクトリで実行します。

実行結果の例:

```
[+] Running 3/3
 ✔ Container myapp-web-1    Removed
 ✔ Container myapp-db-1     Removed
 ✔ Network myapp_default    Removed
```

`up` で作成したコンテナと自動生成ネットワークが削除されます。**名前付きボリュームは残ります。**

---

### ボリュームも削除する

```bash
docker compose down --volumes
# 短縮形
docker compose down -v
```

`volumes:` セクションで定義した名前付きボリュームも削除されます。**DBのデータ等が消えるので注意。**

---

### イメージも削除する

```bash
# compose で使ったイメージをすべて削除
docker compose down --rmi all

# ビルドしたイメージのみ削除（pullしたものは残す）
docker compose down --rmi local
```

---

### オプションの組み合わせ

```bash
# コンテナ・ネットワーク・ボリューム・イメージをすべて削除
docker compose down --volumes --rmi all
```

---

### 特定ファイルを指定して down する

```bash
docker compose -f docker-compose.prod.yml down
```

---

## よくあるエラーと対処

### `no configuration file provided: not found`

```
no configuration file provided: not found
```

**原因:** `docker-compose.yml` がないディレクトリで実行した。  
**対処:** `cd` で正しいディレクトリに移動してから再実行する。

```bash
ls docker-compose.yml  # ファイルが存在するか確認
```

---

### `volume is in use`

```
Error response from daemon: remove myapp_db_data: volume is in use
```

**原因:** 別のコンテナがボリュームを使用中。  
**対処:** 使用中のコンテナを先に停止する。

```bash
docker ps -a  # 全コンテナを確認
docker rm -f <コンテナID>
docker compose down --volumes
```

---

### `permission denied`

**原因:** Docker デーモンへのアクセス権限がない。  
**対処:** `sudo` を付けるか、ユーザーを `docker` グループに追加する。

```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## よくある質問

**Q: `docker compose stop` と `docker compose down` の違いは？**  
`stop` はコンテナを停止するだけでコンテナは残ります。`down` はコンテナを停止して削除します。再起動が必要なら `stop` → `start`、完全にリセットしたいなら `down` → `up` を使います。

**Q: `down` してもデータベースのデータは消えますか？**  
`--volumes` オプションを付けない限り、名前付きボリューム（`db_data` など）はそのまま残ります。`-v` を付けると削除されるので注意してください。

**Q: `docker compose down` 後に `docker compose up` すると元に戻りますか？**  
コンテナは再作成されますが、`--volumes` でボリュームを削除していた場合はデータは戻りません。イメージはローカルに残っているため再ダウンロードは不要です。

**Q: 特定のサービスだけ down できますか？**  
`down` はプロジェクト全体に作用します。特定サービスだけ止めたい場合は `docker compose stop <service>` を使ってください。

**Q: `docker compose down` と `docker system prune` はどう違いますか？**  
`down` は compose プロジェクトのリソースのみを対象にします。`system prune` はシステム全体の未使用リソースを削除します。意図しないリソース削除を避けるには `down` の方が安全です。

---

## 関連記事

- [docker compose up の基本的な使い方](/posts/docker-compose-basic)
- [Docker コンテナのログを確認する方法](/posts/docker-logs)
- [Docker ボリュームの基本と使い方](/posts/docker-volume-basics)
- [Docker イメージとコンテナの削除方法](/posts/docker-delete-image-container)
- [Docker イメージのクリーンアップ](/posts/docker-image-cleanup)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
