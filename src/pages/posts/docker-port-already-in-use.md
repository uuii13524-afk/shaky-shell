---
title: 'Dockerでポートが既に使用中エラーが出た時の対処法'
date: '2026-05-14'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
---

## 症状

```
Error response from daemon: Bind for 0.0.0.0:8080 failed: port is already allocated
```

## 解決方法

### 別のポートを使う

```bash
docker run -d -p 8081:80 nginx
```

### 使用中のポートを確認して解放する

**Windows**

```
netstat -ano | findstr :8080
```

タスクマネージャーで該当プロセスを終了。

**Mac/Linux**

```bash
lsof -i :8080
kill -9 PID
```

### 起動中のDockerコンテナを停止する

```bash
docker ps
docker stop コンテナID
```

## ハマったポイント

- 以前起動したコンテナが残っていてポートを占有していることが多い
- `docker ps -a` で停止中のコンテナも確認する

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [Linuxでプロセスを確認・終了する方法（ps/kill）](/posts/linux-process-management)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
