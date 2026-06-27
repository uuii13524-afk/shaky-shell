---
title: 'docker buildコマンドの使い方完全ガイド｜Dockerfileからイメージを作成する'
date: '2026-06-27'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['docker build', 'Dockerfile', 'Dockerイメージ', 'docker']
description: 'docker buildコマンドでDockerfileからイメージを作成する方法を解説。タグ付け・ビルドコンテキスト・キャッシュ・マルチステージビルドまで網羅。'
---

## ひとことで言うと

```bash
# カレントディレクトリのDockerfileでイメージをビルド
docker build -t myapp:latest .

# 別ディレクトリのDockerfileを指定してビルド
docker build -t myapp:latest -f ./docker/Dockerfile .
```

---

## やりたかったこと / 現象

Dockerfileを書いたのに、どうやってイメージを作ればいいかわからない。`docker build`コマンドの使い方を知りたい、というケースは非常によくあります。

本記事では`docker build`の基本から、タグ付け・キャッシュ制御・マルチステージビルドまで実践的な使い方を解説します。

---

## 環境

- Docker Engine 24.x 以上
- OS: Ubuntu 22.04 / macOS / Windows (WSL2)

---

## 解決策

### 基本的なビルド手順

まずシンプルなDockerfileを用意します。

```dockerfile
# Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "index.js"]
```

ビルドコマンドを実行します。

```bash
# カレントディレクトリ（.）をビルドコンテキストとしてビルド
docker build -t myapp:latest .
```

### タグの付け方

```bash
# -t オプションで名前とタグを指定
docker build -t myapp:1.0.0 .

# 複数のタグを同時に付ける
docker build -t myapp:latest -t myapp:1.0.0 .

# レジストリ名を含む完全なタグ
docker build -t ghcr.io/yourname/myapp:latest .
```

### Dockerfileのパスを指定する

```bash
# -f でDockerfileのパスを指定
docker build -t myapp:latest -f ./docker/Dockerfile .

# 別ディレクトリをビルドコンテキストにする
docker build -t myapp:latest -f Dockerfile /path/to/context
```

### ビルド引数（ARG）を渡す

```dockerfile
# Dockerfile内での定義
ARG NODE_ENV=production
ENV NODE_ENV=$NODE_ENV
```

```bash
# --build-arg でビルド時の変数を注入
docker build --build-arg NODE_ENV=development -t myapp:dev .
```

### キャッシュを無効化してクリーンビルド

```bash
# --no-cache で全レイヤーを再ビルド
docker build --no-cache -t myapp:latest .
```

### マルチステージビルドでイメージを軽量化

```dockerfile
# Dockerfile（マルチステージ）
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

```bash
# 通常通りビルドするだけでOK（最終ステージのみイメージ化）
docker build -t myapp:slim .

# 特定のステージまでビルドする
docker build --target builder -t myapp:builder .
```

### ビルド後にイメージを確認する

```bash
# ビルドしたイメージの一覧表示
docker images

# イメージの詳細情報
docker inspect myapp:latest

# イメージのサイズ確認
docker images myapp
```

---

## よくあるエラーと対処

### `COPY failed: file not found`

```
COPY failed: COPY instruction failed: failed to copy './src': 
no such file or directory
```

**原因**: ビルドコンテキスト外のファイルをCOPYしようとしている、またはファイルが存在しない。

**対処**:
```bash
# ビルドコンテキスト（.）の内容を確認
ls -la

# .dockerignoreで除外されていないか確認
cat .dockerignore
```

### `failed to solve: failed to read dockerfile`

```
failed to solve with frontend dockerfile.v0: 
failed to read dockerfile: open Dockerfile: no such file or directory
```

**原因**: カレントディレクトリにDockerfileが存在しない。

**対処**:
```bash
# ファイルの存在確認
ls Dockerfile

# パスを明示的に指定
docker build -f ./path/to/Dockerfile -t myapp .
```

### `error: pull access denied`

```
pull access denied for baseimage, repository does not exist 
or may require 'docker login'
```

**原因**: FROMで指定したベースイメージが存在しない、またはプライベートレジストリの認証が切れている。

**対処**:
```bash
# Docker Hubへログイン
docker login

# イメージ名のタイポを確認
docker pull node:20-alpine
```

### `no space left on device`

**原因**: Dockerのビルドキャッシュやイメージがディスクを圧迫している。

**対処**:
```bash
# 不要なキャッシュを削除
docker builder prune

# 使っていないイメージ・コンテナを一括削除
docker system prune -a
```

---

## よくある質問

**Q: `.`（ドット）はビルドコマンドで何を意味しますか？**
ビルドコンテキストのパスです。Dockerデーモンにこのディレクトリ以下のファイルを送信します。COPY命令やADD命令はこのコンテキスト内のファイルのみ参照できます。

**Q: ビルドコンテキストが大きくてビルドが遅いときは？**
`.dockerignore`ファイルを作成して不要なファイルを除外しましょう。`node_modules`・`.git`・`dist`などを除外するだけで大幅に高速化できます。

```
# .dockerignore
node_modules
.git
dist
*.log
.env
```

**Q: タグを省略した場合はどうなりますか？**
`-t`を省略するとタグが`<none>`になります。あとから`docker tag`で付与できますが、最初から`-t`を付けるのがベストプラクティスです。

**Q: マルチステージビルドを使うメリットは何ですか？**
ビルド用ツールチェーン（コンパイラ、devDependencies など）を最終イメージに含めずに済むため、イメージサイズを大幅に削減できます。セキュリティ面でも不要なツールが入らないため有利です。

**Q: `docker build`と`docker buildx build`の違いは？**
`docker buildx`はBuildKitベースの拡張ビルドコマンドで、マルチプラットフォームビルド（AMD64/ARM64など）やより高度なキャッシュ戦略が利用できます。通常用途では`docker build`で十分です。

**Q: ビルド中にキャッシュを活用するコツは？**
変更頻度の低いレイヤー（`COPY package*.json`→`RUN npm install`）を先に書き、変更頻度の高いソースコードのCOPYを後ろに置くことでキャッシュが効きやすくなります。

---

## 関連記事

- [docker execコマンドでコンテナ内に入る方法](/posts/docker-exec-bash)
- [docker logsでコンテナのログを確認する方法](/posts/docker-logs)
- [Dockerfileの基本的な書き方](/posts/docker-dockerfile-basics)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerイメージ・コンテナの削除方法](/posts/docker-delete-image-container)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
