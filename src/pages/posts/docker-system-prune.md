---
title: 'docker system pruneで不要リソースを一括削除する方法'
date: '2026-06-29'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker system prune', 'ディスク容量', 'クリーンアップ', 'コンテナ削除']
description: 'docker system pruneで停止中コンテナ・未使用イメージ・ボリュームをまとめて削除する方法を解説。オプション別の挙動と注意点も紹介。'
---

## ひとことで言うと

```bash
# 停止コンテナ・未使用ネットワーク・dangling imageを一括削除
docker system prune

# ボリュームも含めてすべて削除（要注意）
docker system prune -a --volumes
```

---

## やりたかったこと / 現象

Dockerを使い続けていると、停止したコンテナや使われていないイメージが蓄積し、ディスクが圧迫されていきます。`df -h` でディスク残量を確認したら残りわずかだった、というケースでよく使われるコマンドが `docker system prune` です。

---

## 環境

- OS: Ubuntu 22.04 / macOS Ventura
- Docker: 24.x 以降

---

## 解決策

### 基本的な使い方

```bash
docker system prune
```

実行すると以下が削除されます：

- 停止中のコンテナ（`Exited` 状態）
- どのコンテナからも参照されていないネットワーク
- dangling イメージ（タグなし・未参照）
- ビルドキャッシュ

確認プロンプトをスキップしたい場合：

```bash
docker system prune -f
```

### すべての未使用イメージも削除する

```bash
docker system prune -a
```

`-a` / `--all` を付けると、dangling だけでなく「どのコンテナからも使われていないイメージ」もすべて削除されます。開発環境でディスクをまとめて解放したいときに便利です。

### ボリュームも含めて削除する

```bash
docker system prune -a --volumes
```

**注意:** `--volumes` を付けると名前付きボリューム（DBデータなど）も削除されます。本番データが消えるリスクがあるため、十分に確認してから実行してください。

### 削除前に何が消えるか確認する

```bash
# 停止中コンテナの一覧
docker ps -a --filter "status=exited"

# 未使用イメージの一覧
docker images -f "dangling=true"

# ボリューム一覧
docker volume ls
```

### 削除後のディスク使用量を確認する

```bash
docker system df
```

| 種別 | SIZE | RECLAIMABLE |
|------|------|-------------|
| Images | 3.2GB | 1.1GB |
| Containers | 0B | 0B |
| Volumes | 500MB | 200MB |
| Build Cache | 800MB | 800MB |

`RECLAIMABLE` 列が実際に回収できる容量です。

---

## よくあるエラーと対処

### `Error response from daemon: conflict`

実行中のコンテナが使っているリソースは削除されません。エラーではなくスキップされるため、正常な動作です。

### `permission denied`

```bash
sudo docker system prune
```

Linuxで `docker` グループに所属していない場合は `sudo` が必要です。

### ボリュームを消してしまった

`--volumes` 付きで削除してしまった場合、バックアップがなければ復元は困難です。事前に `docker volume inspect <name>` でマウントパスを確認し、重要なデータはホスト側にバックアップを取る習慣をつけましょう。

---

## よくある質問

**Q: 実行中のコンテナのデータは消えますか？**
いいえ。`docker system prune` は停止中のリソースのみを対象にします。実行中のコンテナ・それが使うイメージ・ボリュームは削除されません。

**Q: `docker image prune` との違いは？**
`docker image prune` はイメージのみを削除します。`docker system prune` はコンテナ・ネットワーク・ビルドキャッシュもまとめて削除するため、より広い範囲をクリーンアップできます。

**Q: 定期的に自動実行したい場合は？**
`cron` に登録することで自動化できます。

```bash
# 毎週日曜日の深夜1時に実行（確認なし）
0 1 * * 0 docker system prune -f >> /var/log/docker-prune.log 2>&1
```

**Q: ビルドキャッシュだけ削除したい場合は？**

```bash
docker builder prune
```

`docker system prune` を使わずにビルドキャッシュだけ削除できます。

**Q: `-a` なしと `-a` ありで何が変わりますか？**
`-a` なしは dangling イメージ（タグなし）のみ削除。`-a` ありは「コンテナから参照されていないすべてのイメージ」を削除します。`-a` は pull したがまだ使っていないイメージも消えるため注意が必要です。

**Q: Windows（Docker Desktop）でも使えますか？**
はい。PowerShell や WSL2 のターミナルから同じコマンドで実行できます。

---

## 関連記事

- [docker image cleanupで不要イメージを削除する](/posts/docker-image-cleanup)
- [docker logsでコンテナのログを確認する](/posts/docker-logs)
- [docker volume basicsでデータ永続化を理解する](/posts/docker-volume-basics)
- [docker network basicsでネットワークを理解する](/posts/docker-network-basics)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
