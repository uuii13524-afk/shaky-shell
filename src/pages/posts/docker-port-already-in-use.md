---
title: 'Dockerでポートが既に使用中エラーが出た時の対処法'
date: '2026-05-20'
category: 'Docker'
---

## 症状

Dockerコンテナを起動しようとすると以下のエラーが出る。

```
Error response from daemon: driver failed programming external connectivity on endpoint:
Bind for 0.0.0.0:8080 failed: port is already allocated
```

または

```
Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use
```

## 環境

- Docker Desktop（Windows / Mac）
- Docker（Linux）

## 原因

指定したポートが他のプロセスまたは別のDockerコンテナに使われている。

## 解決方法

### 方法1：別のポートを使う

```bash
# 8080が使われているなら8081を使う
docker run -d -p 8081:80 nginx
```

### 方法2：使用中のポートを確認して解放する

**Windowsの場合**

```
netstat -ano | findstr :8080
```

PIDを確認してタスクマネージャーで該当プロセスを終了する。

**Mac / Linuxの場合**

```bash
lsof -i :8080
kill -9 PID
```

### 方法3：起動中のDockerコンテナを確認して停止する

```bash
docker ps                    # 起動中のコンテナを確認
docker stop コンテナID       # 該当コンテナを停止
```

### 方法4：Docker Desktopを再起動する

Docker Desktopを完全に終了して再起動する。

## ハマったポイント

- 以前起動したコンテナが残っていてポートを占有していることが多い
- `docker ps -a` で停止中のコンテナも確認する
- 開発時はポート番号を統一するとトラブルが減る

## 関連記事

- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
