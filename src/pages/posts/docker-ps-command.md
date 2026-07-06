---
title: 'docker ps コマンドの使い方｜コンテナ一覧の確認・フィルタ・フォーマット指定まとめ'
date: '2026-07-06'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker ps', 'コンテナ管理']
description: 'docker psコマンドで実行中・停止中のコンテナ一覧を確認する方法。-a、--filter、--format、サイズ表示などのオプションとよくあるエラーを解説。'
---

## ひとことで言うと

```bash
# 実行中のコンテナ一覧
docker ps

# 停止中も含めた全コンテナ一覧
docker ps -a
```

---

## やりたかったこと / 現象

「今どのコンテナが動いているか確認したい」「さっき停止したコンテナの名前を思い出せない」「特定のイメージから起動したコンテナだけ絞り込みたい」——こうした場面で最初に使うのが `docker ps` です。

デフォルトでは実行中のコンテナしか表示されないため、「コンテナが消えた」と勘違いしてしまうことがよくあります。オプションの使い分けを押さえておくと、コンテナ管理が一気に楽になります。

---

## 環境

- Docker: 20.10以降で動作確認
- OS: Linux / macOS / Windows（WSL2）

---

## 解決策

### 1. 実行中のコンテナを確認する

```bash
docker ps
```

```
CONTAINER ID   IMAGE     COMMAND                  STATUS         PORTS                    NAMES
a1b2c3d4e5f6   nginx     "/docker-entrypoint.…"   Up 2 hours     0.0.0.0:80->80/tcp       my-nginx
```

デフォルトでは **実行中（Up状態）のコンテナのみ** が表示されます。

### 2. 停止中のコンテナも含めて全件表示する

```bash
docker ps -a
```

`Exited` になっているコンテナも一覧に含まれます。「コンテナが見つからない」と思ったら、まず `-a` を付けて確認しましょう。

### 3. 表示件数を絞り込む

```bash
# 直近作成した1件だけ表示
docker ps -l

# 直近作成した3件を表示
docker ps -n 3
```

### 4. コンテナIDだけを取得する

```bash
docker ps -aq
```

スクリプトで一括削除・一括停止する際によく使う書き方です。

```bash
# 停止中のコンテナをまとめて削除
docker rm $(docker ps -aq -f status=exited)
```

### 5. `--filter` で条件を絞り込む

```bash
# 特定イメージから起動したコンテナだけ表示
docker ps -a --filter "ancestor=nginx"

# 名前で絞り込む
docker ps -a --filter "name=my-nginx"

# 状態で絞り込む
docker ps -a --filter "status=exited"
```

### 6. `--format` で出力項目をカスタマイズする

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

```
NAMES       STATUS         PORTS
my-nginx    Up 2 hours     0.0.0.0:80->80/tcp
```

Goテンプレート形式で必要な列だけを表示できるため、横に長くなりがちな `docker ps` の出力を見やすく整理できます。

### 7. コンテナのディスクサイズを表示する

```bash
docker ps -s
```

`SIZE` 列にコンテナが使用しているディスク容量が追加されます。ディスク圧迫の調査に便利です。

---

## よくあるエラーと対処

### コンテナが一覧に出てこない

`docker ps` は実行中のコンテナしか表示しません。停止済みの場合は `-a` を付けて確認してください。

```bash
docker ps -a
```

### `docker: command not found`

Dockerがインストールされていないか、PATHが通っていません。インストール状況を確認しましょう。

```bash
docker --version
```

### `Cannot connect to the Docker daemon`

Dockerデーモンが起動していません。OSに応じて起動します。

```bash
# Linux (systemd)
sudo systemctl start docker

# macOS / Windows
# Docker Desktopを起動する
```

### `--filter` の条件を指定しても結果が0件になる

フィルタのキーやスペルミスが原因のことが多いです。`ancestor` はイメージ名、`name` はコンテナ名、`status` は `running` / `exited` / `paused` などの状態を指定します。指定値が正しいか再確認してください。

---

## よくある質問

**Q: `docker ps` と `docker container ls` の違いは何ですか？**
どちらも同じ結果を返します。`docker container ls` は新しいサブコマンド体系の呼び方で、`docker ps` は従来からのエイリアスです。

**Q: 停止中のコンテナだけを表示するには？**
`docker ps -a --filter "status=exited"` を使います。

**Q: コンテナ名だけをリスト表示したい場合は？**
`docker ps --format "{{.Names}}"` で名前だけを1行ずつ出力できます。

**Q: `docker ps` の出力が横に長くて見づらいときは？**
`--format` オプションでtable形式のテンプレートを指定すると、必要な列だけに絞って見やすくできます。

**Q: 複数の条件でフィルタできますか？**
`--filter` を複数回指定すると、AND条件として絞り込まれます。例: `docker ps -a --filter "status=exited" --filter "ancestor=nginx"`

**Q: `docker compose` で立ち上げたコンテナも同じように確認できますか？**
`docker ps` でも表示されますが、`docker compose ps` を使うとプロジェクト単位で見やすく整理されます。

---

## 関連記事

- [docker cp コマンドの使い方](/posts/docker-cp)
- [docker exec でコンテナ内に入る方法](/posts/docker-exec-bash)
- [docker logsコマンドの使い方](/posts/docker-logs)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
