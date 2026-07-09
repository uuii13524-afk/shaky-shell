---
title: 'docker inspect コマンドの使い方｜コンテナ・イメージの詳細情報を確認する方法'
date: '2026-07-09'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker inspect', 'トラブルシューティング']
description: 'docker inspectコマンドでコンテナやイメージの詳細情報（IPアドレス・環境変数・マウント・ヘルスチェック等）を確認する方法。--formatによる絞り込みやjqとの組み合わせ、よくあるエラーを解説。'
---

## ひとことで言うと

```bash
# コンテナの全情報をJSONで表示
docker inspect <コンテナ名またはID>

# 特定の項目だけ取り出す（IPアドレスの例）
docker inspect -f '{{.NetworkSettings.IPAddress}}' <コンテナ名>
```

---

## やりたかったこと / 現象

コンテナの中で何が起きているのか調べたい、コンテナに割り当てられたIPアドレスを知りたい、マウントされているボリュームのパスを確認したい——`docker ps` や `docker logs` では表示されないこうした詳細情報を探しているときに `docker inspect` にたどり着く人が多いはずです。

`docker inspect` はコンテナやイメージ、ネットワーク、ボリュームなど、Dockerが管理するオブジェクトの設定情報をJSON形式で丸ごと出力してくれるコマンドです。情報量が多い分、目的の項目をどう絞り込むかがポイントになります。

---

## 環境

- Docker: 20.10以降で動作確認
- OS: Linux / macOS / Windows（WSL2）

---

## 解決策

### 1. 基本構文

```bash
docker inspect <コンテナ名/ID>
docker inspect <イメージ名/ID>
```

コンテナ名とイメージ名が重複していない限り、`docker inspect` は自動的に対象の種類を判別します。明示的に指定したい場合は `--type` オプションを使います。

```bash
docker inspect --type container <名前>
docker inspect --type image <名前>
```

### 2. IPアドレスを確認する

```bash
docker inspect -f '{{.NetworkSettings.IPAddress}}' <コンテナ名>
```

デフォルトブリッジネットワーク以外（`docker network create` で作った独自ネットワークなど）に接続している場合は、以下のように取得します。

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <コンテナ名>
```

### 3. 環境変数を確認する

```bash
docker inspect -f '{{.Config.Env}}' <コンテナ名>
```

### 4. マウントされているボリュームを確認する

```bash
docker inspect -f '{{.Mounts}}' <コンテナ名>
```

見やすく整形したい場合はJSON全体を `jq` に渡すのがおすすめです。

```bash
docker inspect <コンテナ名> | jq '.[0].Mounts'
```

### 5. ヘルスチェックの状態を確認する

```bash
docker inspect -f '{{.State.Health.Status}}' <コンテナ名>
```

`healthy` / `unhealthy` / `starting` のいずれかが返ります。`HEALTHCHECK` を定義していないイメージでは `<no value>` になります。

### 6. 終了コードを確認する

```bash
docker inspect -f '{{.State.ExitCode}}' <コンテナ名>
```

コンテナが異常終了した原因調査の第一歩として、終了コードの確認はよく行われます。

### 7. 複数のコンテナをまとめて調べる

```bash
docker inspect -f '{{.Name}}: {{.State.Status}}' $(docker ps -aq)
```

---

## よくあるエラーと対処

### `Error: No such object: <名前>`

コンテナ名やイメージ名のタイプミス、または対象がすでに削除されていることが原因です。`docker ps -a` や `docker images` で正確な名前を確認してください。

```bash
docker ps -a
docker inspect <正しい名前>
```

### `template: :1: unexpected "}" in operand`

`-f`（`--format`）で指定するGoテンプレートの構文ミスです。`{{ }}` の対応や `.` の位置を確認してください。

```bash
# 誤り
docker inspect -f '{{.NetworkSettings.IPAddress' <コンテナ名>

# 正しい
docker inspect -f '{{.NetworkSettings.IPAddress}}' <コンテナ名>
```

### 出力結果が空 `[]`

コンテナ名・イメージ名を1つも指定していないか、複数指定した際に該当するものが1つもない場合に発生します。引数を確認してください。

### JSONが長すぎて読みにくい

`docker inspect` の出力はネストが深く、そのまま見ると情報量が多すぎます。`jq` や `--format` を使って必要な項目だけに絞り込むと読みやすくなります。

```bash
docker inspect <コンテナ名> | jq '.[0] | {Name, State, NetworkSettings}'
```

---

## よくある質問

**Q: `docker inspect` と `docker stats` の違いは？**
`docker inspect` は設定情報（IPアドレス・環境変数・マウント等）の静的なスナップショットを表示します。一方 `docker stats` はCPU・メモリ使用率などのリアルタイムなリソース状況を表示するコマンドで、目的が異なります。

**Q: コンテナが停止していても `docker inspect` は使えますか？**
使えます。停止中のコンテナでも設定情報や最後の終了コード（`State.ExitCode`）などを確認できます。ただしネットワーク情報の一部は停止中には取得できません。

**Q: `--format` と `-f` は何が違いますか？**
同じオプションの省略形と正式名です。動作に違いはありません。

**Q: イメージに対して `docker inspect` を使うと何がわかりますか？**
イメージのレイヤー構成、デフォルトの環境変数、`CMD`/`ENTRYPOINT`、公開ポート、作成日時などがわかります。

**Q: ネットワークやボリュームにも `docker inspect` は使えますか？**
使えます。`docker network inspect <ネットワーク名>` や `docker volume inspect <ボリューム名>` のように、対象ごとのサブコマンドとしても実行できます。

---

## 関連記事

- [docker logs コマンドの使い方](/posts/docker-logs)
- [docker network の基本](/posts/docker-network-basics)
- [docker ps コマンドの使い方](/posts/docker-ps-command)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
