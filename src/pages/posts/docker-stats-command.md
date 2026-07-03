---
title: 'docker stats コマンドの使い方｜コンテナのCPU・メモリ使用量をリアルタイム監視'
date: '2026-07-03'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker stats', 'コンテナ', 'リソース監視', 'パフォーマンス']
description: 'docker statsコマンドでコンテナのCPU・メモリ・ネットワーク使用量をリアルタイム監視する方法を解説。フォーマット指定、特定コンテナの絞り込み、ログ保存の方法も紹介。'
---

## ひとことで言うと

```bash
# 全コンテナのリソース使用量をリアルタイム表示
docker stats

# 特定のコンテナだけを表示
docker stats my-container

# 1回だけ取得してすぐ終了(監視ではなく単発取得)
docker stats --no-stream
```

---

## やりたかったこと / 現象

コンテナの動作が重い、ホストのCPUやメモリを圧迫している気がする、といったときに「どのコンテナがどれだけリソースを使っているか」を確認したい。

`docker stats` はコンテナごとのCPU使用率・メモリ使用量・ネットワークI/O・ディスクI/Oをリアルタイムで表示するコマンドで、`top` や `htop` のDocker版として使えます。

---

## 環境

- Docker Engine 24.x 以上（Docker Desktop でも同様）
- OS: Linux / macOS / Windows（WSL2）

---

## 解決策

### 基本: 全コンテナの使用量を表示する

```bash
docker stats
```

出力例:
```
CONTAINER ID   NAME           CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O
a1b2c3d4e5f6   web-app        2.34%     120.5MiB / 1.944GiB   6.05%     1.2MB / 850kB     0B / 0B
b2c3d4e5f6a1   db             15.67%    512.3MiB / 1.944GiB   25.72%    3.4MB / 2.1MB     45MB / 12MB
```

`Ctrl + C` で表示を終了します。デフォルトでは1〜2秒ごとに自動更新されます。

### 特定のコンテナだけを表示する

```bash
docker stats web-app db
```

複数のコンテナ名・IDをスペース区切りで指定できます。

### 1回だけ取得する（--no-stream）

継続監視ではなく、スクリプトなどで1回だけ値を取得したい場合。

```bash
docker stats --no-stream
```

### 表示項目をカスタマイズする（--format）

Go テンプレート形式で出力項目を指定できます。

```bash
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

出力例:
```
NAME       CPU %     MEM USAGE / LIMIT
web-app    2.34%     120.5MiB / 1.944GiB
db         15.67%    512.3MiB / 1.944GiB
```

### JSON形式で出力する（スクリプト連携向け）

```bash
docker stats --no-stream --format "{{json .}}"
```

`jq` と組み合わせて特定の値だけ抽出できます。

```bash
docker stats --no-stream --format "{{json .}}" | jq -r '.Name + ": " + .CPUPerc'
```

### 一定間隔でログに保存する

```bash
while true; do
  docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}}" >> stats.csv
  sleep 60
done
```

---

## よくあるエラーと対処

### 数値がずっと `0.00%` のまま変化しない

コンテナがほぼアイドル状態か、`--no-stream` を付けずに一瞬しか表示を見ていない可能性があります。負荷をかけた状態で確認しましょう。

```bash
# コンテナ内で負荷テストを実行してから確認
docker exec my-container stress --cpu 2 --timeout 30s
docker stats my-container
```

### `MEM LIMIT` が想定より大きい/小さい

コンテナのメモリ上限は `docker run --memory` で明示的に指定しない限り、ホストの全メモリが上限として表示されます。

```bash
# メモリ上限を指定して起動
docker run --memory="512m" --name my-container my-image
```

### `docker stats` の実行が重い・遅い

大量のコンテナを起動している環境では表示更新が遅くなることがあります。対象を絞り込むと改善します。

```bash
docker stats $(docker ps --format "{{.Names}}" | grep app)
```

### Windows/WSL2でパーセンテージが100%を超える

複数CPUコアを使っている場合、CPU%はコア数分（例: 4コアなら最大400%）まで表示されるのが仕様です。異常ではありません。

---

## よくある質問

**Q: `docker stats` と `docker top` の違いは何ですか？**
`docker stats` はコンテナ全体のCPU・メモリ・I/Oの集計値をリアルタイム表示します。`docker top` はコンテナ内で実行中のプロセス一覧を表示するコマンドで、用途が異なります。

**Q: 停止中のコンテナの情報も見られますか？**
いいえ、`docker stats` は起動中のコンテナのみが対象です。停止中のコンテナは表示されません。

**Q: CPU使用率が100%を超えることがあるのはなぜですか？**
`docker stats` のCPU%はホストの全論理コア数を基準に計算されるため、マルチコアを使い切ると100%を超えて表示されます（例: 4コア使用時は最大400%）。

**Q: `docker-compose` 環境でも使えますか？**
はい。`docker stats` はDocker Composeで起動したコンテナも通常のコンテナと同様に扱えます。特定サービスだけ見たい場合はコンテナ名を指定してください。

**Q: リソース使用量に上限を設定して制限したい場合は？**
`docker run` 実行時に `--cpus` や `--memory` オプションを指定します。

```bash
docker run --cpus="1.5" --memory="1g" my-image
```

**Q: Kubernetes でも似たコマンドはありますか？**
`kubectl top pod` で同様にPodごとのCPU・メモリ使用量を確認できます（metrics-serverの導入が必要です）。

---

## 関連記事

- [docker logs コマンド完全ガイド](/posts/docker-logs)
- [docker exec でコンテナ内に入る方法](/posts/docker-exec-bash)
- [Docker のプロセス管理（ps / stop / rm）](/posts/docker-delete-image-container)
- [docker system prune でディスク容量を解放する](/posts/docker-system-prune)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
