---
title: 'Dockerfileの基本的な書き方'
date: '2026-05-18'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'DockerfileのFROM・RUN・COPY・CMD・EXPOSEなど基本的な命令の書き方を解説。イメージのビルド手順と実践的なサンプルも紹介します。'
---

## やりたかったこと

Node.jsのアプリをDockerコンテナで動かそうとした。最初は `docker run node:18` でコンテナを起動してアプリを手動で入れていたが、毎回同じ手順を繰り返すのが面倒になってきた。Dockerfileを書けば同じ環境を一発で再現できると聞いて試してみた。

---

## 環境

- OS: Ubuntu 22.04 LTS
- Docker: 24.0.5
- Node.js: 22系（alpine）

---

## 試したこと・うまくいかなかったこと

最初、こんな書き方をした。

```dockerfile
FROM node:22
COPY . .
RUN npm install
CMD ["node", "server.js"]
```

ビルドは通ったが、毎回 `npm install` のキャッシュが効かずに全パッケージをダウンロードし直していた。2分近くかかっていて、コードを1行直すたびに待ち続けた。

次に `node_modules` もまるごとCOPYしてビルドしていたが、ホストとコンテナでCPUアーキテクチャが違うせいでバイナリが壊れて起動エラーになった。

```
Error: /app/node_modules/bcrypt/lib/binding/napi-v3/bcrypt_lib.node: invalid ELF header
```

`.dockerignore` を知らなかったのが原因だった。

---

## 解決策

`package*.json` だけを先にCOPYして `npm ci` を実行する。こうするとpackage.jsonが変わらない限りこのレイヤーのキャッシュが使い回されてビルドが速くなった。

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["node", "server.js"]
```

`.dockerignore` も必ず作る。これがないとホスト側の `node_modules` がコンテナにコピーされてイメージが数GB単位で膨れ上がる。

```
node_modules
dist
.env
.git
*.log
```

ビルドして起動するコマンド:

```bash
docker build -t myapp .
docker run -d -p 3000:3000 myapp
```

これで起動した。

---

## ハマったポイント

- `COPY package*.json ./` を `COPY . .` より先に書かないとキャッシュが全く効かない。ちょっとしたコード修正のたびに `npm ci` が走って3分待ちになった
- `.dockerignore` なしでビルドすると `node_modules`（700MB超）がイメージに入る。 `docker images` で確認したら1.8GBになっていて驚いた
- `RUN npm install` より `RUN npm ci` のほうがCI/CDでは安定する。`package-lock.json` がないと `npm ci` はエラーになるのでlockファイルは必ずコミットしておく
- `WORKDIR /app` を省略すると `/` 直下にファイルが散らばってあとで管理しにくくなった
- `CMD` と `ENTRYPOINT` の違いで1時間ハマった。`CMD` は上書き可能、`ENTRYPOINT` は固定と覚えた

---

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
