---
title: 'Dockerfileの基本的な書き方'
date: '2026-05-18'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
---

## Dockerfileの基本構成

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

## .dockerignoreファイル

```
node_modules
dist
.env
.git
*.log
```

## イメージをビルドして実行

```bash
docker build -t myapp .
docker run -d -p 3000:3000 myapp
```

## ハマったポイント

- `COPY package*.json ./` してから `RUN npm ci` を分けるとキャッシュが効く
- `.dockerignore` がないと `node_modules` がコピーされてイメージが巨大になる

DockerfileでビルドしたイメージをCI/CDで自動デプロイしたい場合は[GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)と組み合わせると効率が上がる。

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
