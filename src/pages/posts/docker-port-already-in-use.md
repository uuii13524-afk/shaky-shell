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
