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

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
