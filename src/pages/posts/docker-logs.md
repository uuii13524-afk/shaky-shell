---
title: 'docker logs コマンド完全ガイド｜コンテナログの確認・追跡・フィルタリング'
date: '2026-06-25'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker logs', 'コンテナ', 'ログ確認', 'デバッグ']
description: 'docker logsコマンドの使い方を徹底解説。リアルタイム追跡（-f）、行数指定（--tail）、タイムスタンプ表示、エラーログの絞り込みまで実例付きで紹介。'
---

## ひとことで言うと

```bash
# コンテナのログをすべて表示
docker logs <コンテナ名またはID>

# リアルタイムで追跡（tail -f 相当）
docker logs -f <コンテナ名>

# 最新100行だけ表示
docker logs --tail 100 <コンテナ名>
```

---

## やりたかったこと / 現象

Dockerコンテナが起動しない、アプリが正常に動かない、エラーが出ているときに「コンテナの中で何が起きているか」を確認したい。

`docker logs` はコンテナの標準出力（stdout）と標準エラー出力（stderr）を表示するコマンドで、トラブルシューティングに必須です。

---

## 環境

- Docker Engine 24.x 以上（Docker Desktop でも同様）
- OS: Linux / macOS / Windows（WSL2）

---

## 解決策

### 基本: ログをすべて表示する

```bash
docker logs my-container
```

コンテナ名の代わりにコンテナIDの先頭数文字でも可。

```bash
docker logs a1b2c3d4
```

### リアルタイムで追跡する（-f / --follow）

```bash
docker logs -f my-container
```

`Ctrl + C` で追跡を停止します。アプリのデプロイ直後や起動確認に便利です。

### 最新 N 行だけ表示する（--tail）

```bash
# 最新50行
docker logs --tail 50 my-container

# 最新100行をリアルタイム追跡
docker logs -f --tail 100 my-container
```

### タイムスタンプを付けて表示する（-t / --timestamps）

```bash
docker logs -t my-container
```

出力例:
```
2026-06-25T08:30:01.123456789Z Server started on port 3000
2026-06-25T08:30:02.456789012Z Connected to database
```

### 時刻でフィルタリングする（--since / --until）

```bash
# 過去1時間のログ
docker logs --since 1h my-container

# 特定時刻以降のログ
docker logs --since "2026-06-25T08:00:00" my-container

# 特定時刻までのログ
docker logs --until "2026-06-25T09:00:00" my-container

# 組み合わせ
docker logs --since "2026-06-25T08:00:00" --until "2026-06-25T09:00:00" my-container
```

### エラーログだけ抽出する（stderr）

```bash
# stderr のみ表示
docker logs my-container 2>&1 | grep -i error

# grep で絞り込む
docker logs my-container 2>&1 | grep "ERROR\|WARN\|Exception"
```

### docker-compose 環境でのログ確認

```bash
# 特定サービスのログ
docker-compose logs app

# 全サービスのログをリアルタイム追跡
docker-compose logs -f

# 最新50行を全サービス分
docker-compose logs --tail 50
```

---

## よくあるエラーと対処

### `Error: No such container: xxx`

```
Error response from daemon: No such container: my-container
```

コンテナ名またはIDが間違っています。まず存在するコンテナを確認しましょう。

```bash
# 起動中のコンテナ一覧
docker ps

# 停止済みを含む全コンテナ一覧
docker ps -a
```

### ログが何も表示されない

アプリが stdout ではなくファイルにログを書いている場合、`docker logs` には何も出ません。

```bash
# コンテナ内のログファイルを確認する
docker exec my-container cat /var/log/app.log
```

または、アプリのロギング設定を stdout 出力に変更することを推奨します。

### `unknown flag: --tail` エラー

古いバージョンの Docker では `--tail` が使えない場合があります。

```bash
docker --version
# Docker version 24.x.x 以上を推奨
```

### ログが多すぎて読めない

```bash
# less でページング
docker logs my-container 2>&1 | less

# ファイルに保存
docker logs my-container > container.log 2>&1
```

---

## よくある質問

**Q: 停止したコンテナのログも確認できますか？**
はい、`docker ps -a` でコンテナIDを確認し、`docker logs <ID>` で参照できます。停止後もログはホスト側に保存されています。

**Q: `docker logs -f` と `tail -f` の違いは何ですか？**
`docker logs -f` はコンテナのログドライバー経由でログを取得します。`tail -f` はファイルを直接監視するため、コンテナ内ファイルを監視するには `docker exec` との組み合わせが必要です。

**Q: ログの保存期間・容量に制限はありますか？**
デフォルトのログドライバー（json-file）では制限なしに蓄積されます。長期運用では以下のようにサイズ制限を設定することを推奨します。

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

**Q: `docker logs` はどこにデータを保存していますか？**
デフォルトでは `/var/lib/docker/containers/<コンテナID>/<コンテナID>-json.log` に JSON 形式で保存されます。

**Q: Kubernetes でも同じコマンドが使えますか？**
Kubernetes では `kubectl logs <Pod名>` を使います。オプションの多くは同様で、`-f`（追跡）、`--tail`（行数制限）が使えます。

**Q: ログドライバーを変更するとどうなりますか？**
`syslog` や `fluentd` などに変更すると `docker logs` が使えなくなる場合があります。本番環境では集中ロギング基盤（Fluentd + Elasticsearch など）を検討しましょう。

---

## 関連記事

- [docker exec でコンテナ内に入る方法](/posts/docker-exec-bash)
- [docker-compose の基本的な使い方](/posts/docker-compose-basic)
- [Dockerのプロセス管理（ps / stop / rm）](/posts/docker-delete-image-container)
- [Docker ネットワークの基礎](/posts/docker-network-basics)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
