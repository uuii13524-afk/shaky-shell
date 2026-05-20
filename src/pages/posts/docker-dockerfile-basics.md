---
title: 'Dockerfileの基本的な書き方'
date: '2026-05-20'
category: 'Docker'
---

## やりたかったこと

自分のアプリをDockerイメージにしたかった。
Dockerfileを書くことで環境をコード化できる。

## 環境

- Docker Desktop（Windows / Mac）
- Docker（Linux）

## Dockerfileの基本構成

```dockerfile
# ベースイメージを指定
FROM node:22-alpine

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をコピーしてインストール
COPY package*.json ./
RUN npm ci

# ソースコードをコピー
COPY . .

# ビルド
RUN npm run build

# ポートを公開
EXPOSE 3000

# コンテナ起動時に実行するコマンド
CMD ["node", "server.js"]
```

## よく使うDockerfileの命令

```dockerfile
FROM イメージ名:タグ      # ベースイメージ
WORKDIR /パス            # 作業ディレクトリ
COPY コピー元 コピー先    # ファイルをコピー
RUN コマンド             # コマンドを実行（イメージビルド時）
ENV 変数名=値            # 環境変数を設定
EXPOSE ポート番号         # ポートを公開（ドキュメント用）
CMD ["コマンド"]         # コンテナ起動時のコマンド
ENTRYPOINT ["コマンド"]  # コンテナのエントリーポイント
```

## .dockerignoreファイル

不要なファイルをビルドに含めないようにする。

```
node_modules
dist
.env
.git
*.log
```

## イメージをビルドして実行

```bash
docker build -t myapp .           # ビルド
docker run -d -p 3000:3000 myapp  # 起動
```

## ハマったポイント

- `COPY . .` の前に `COPY package*.json ./` して `RUN npm ci` を分けると、ソースコード変更時にnpm installをスキップしてキャッシュが効く
- `.dockerignore` を設定しないと `node_modules` がコピーされてイメージが巨大になる
- `alpine` タグのイメージは軽量だが一部のパッケージが動かないことがある

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
