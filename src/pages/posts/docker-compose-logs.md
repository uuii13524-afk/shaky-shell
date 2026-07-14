---
title: 'docker compose logs の使い方｜複数サービスのログをまとめて確認する'
date: '2026-07-14'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker-compose', 'ログ確認']
description: 'docker compose logs でサービスごとのログをまとめて確認する方法を解説。リアルタイム監視やサービス絞り込み、よくあるエラーの対処法も紹介します。'
---

## ひとことで言うと

```bash
# 全サービスのログを表示
docker compose logs

# リアルタイムで追跡（tail -f 相当）
docker compose logs -f

# 特定サービスの直近100行だけ表示
docker compose logs -f --tail=100 web
```

---

## やりたかったこと / 現象

`docker compose up -d` でバックグラウンド起動したら、コンテナが落ちたのか動いているのかログが見えなくなった。複数サービスを動かしていると、どのコンテナのログか分からず調査が進まない。

---

## 環境

- Docker Engine 24.x 以降
- Docker Compose v2（`docker compose` コマンド）
- OS: Ubuntu 22.04 / macOS / WSL2

> **注意:** 旧来の `docker-compose`（v1）でも同様のオプションが使えます。

---

## 解決策

### 基本の使い方

```bash
docker compose logs
```

`docker-compose.yml` に定義された**全サービス**の標準出力・標準エラー出力をまとめて表示します。サービス名がプレフィックスとして色分け表示されるため、どのコンテナのログかひと目で分かります。

### リアルタイムで監視する

```bash
docker compose logs -f
# または
docker compose logs --follow
```

`tail -f` と同様に、新しいログが出力されるたびに画面に流れます。Ctrl+C で終了します。

### 特定のサービスだけ表示する

```bash
docker compose logs web
docker compose logs web db
```

サービス名を指定すると、そのサービスのログだけに絞り込めます。複数指定も可能です。

### 直近のログだけ表示する

```bash
docker compose logs --tail=100 web
docker compose logs -f --tail=50
```

`--tail` で表示する行数を指定できます。過去ログが大量にある場合に便利です。

### タイムスタンプを表示する

```bash
docker compose logs -t
# または
docker compose logs --timestamps
```

各ログ行に発生時刻が付与されるため、他システムのログと突き合わせる際に役立ちます。

### 指定時刻以降のログだけ表示する

```bash
docker compose logs --since 2026-07-14T09:00:00
docker compose logs --since 30m
```

`--since` には日時のほか、`30m`（30分前）や `2h`（2時間前）といった相対時間も指定できます。障害調査の開始時刻を絞り込むときに便利です。

---

## docker logs との違い

| コマンド | 対象 | 用途 |
|---------|------|------|
| `docker logs <container>` | 単一コンテナ | コンテナ名/IDを直接指定して確認 |
| `docker compose logs [service]` | Compose管理下の1つ以上のサービス | サービス名で横断的に確認 |

複数コンテナを組み合わせて動かしている場合は、コンテナIDを都度調べなくて済む `docker compose logs` の方が圧倒的に楽です。

---

## よくあるエラーと対処

### ログが何も表示されない

```bash
# コンテナが起動しているか確認
docker compose ps

# サービス名のスペルミスがないか確認
docker compose config --services
```

コンテナがそもそも起動していない、またはサービス名を間違えている可能性があります。

### `no such service: web`

`docker-compose.yml` に定義されていないサービス名を指定しています。

```bash
docker compose config --services
```

で正しいサービス名を確認してください。

### ログが古い情報のまま止まって見える

```bash
docker compose logs -f --tail=0
```

`--tail=0` を付けると過去ログを表示せず、これ以降に出力される新しいログだけを待ち受けられます。バッファリングされた大量の過去ログに惑わされずに済みます。

### アプリのログがバッファリングされて表示が遅れる

Node.js や Python のアプリで標準出力がバッファリングされていると、ログがまとめて出力されることがあります。

```dockerfile
# Node.js の例
ENV NODE_OPTIONS="--unhandled-rejections=strict"
```

```dockerfile
# Python の例（バッファリング無効化）
ENV PYTHONUNBUFFERED=1
```

---

## よくある質問

**Q: `docker compose logs` と `docker compose logs -f` の違いは何ですか？**  
`docker compose logs` は現時点までのログを一度だけ表示して終了します。`-f`（`--follow`）を付けると、新しいログが出力されるたびにリアルタイムで表示し続けます。

**Q: ログの色分けを消すことはできますか？**  
`--no-color` オプションを使います。ログをファイルにリダイレクトする場合など、色付けが不要なときに便利です。

```bash
docker compose logs --no-color > app.log
```

**Q: コンテナを削除した後もログは見られますか？**  
いいえ。コンテナを削除するとログも一緒に消えます。長期保存が必要な場合は、ログドライバーを `json-file` 以外（`syslog`、`fluentd` など）に設定するか、アプリ側でログをファイル出力・外部転送してください。

**Q: 特定のエラーメッセージだけ抽出したいです。**  
`grep` と組み合わせると便利です。

```bash
docker compose logs | grep -i error
```

**Q: ログの量が多すぎてターミナルが埋め尽くされます。**  
`--tail` で表示件数を絞るか、`| less` でページングして確認してください。

```bash
docker compose logs --tail=200 | less
```

---

## 関連記事

- [docker compose down の使い方](/posts/docker-compose-down)
- [docker logs でコンテナのログを確認する](/posts/docker-logs)
- [docker compose up の使い方](/posts/docker-compose-basic)
- [docker ps コマンドの使い方](/posts/docker-ps-command)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
