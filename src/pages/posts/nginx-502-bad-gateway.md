---
title: 'nginx 502 Bad Gatewayエラーの原因と解決方法'
date: '2026-05-20'
category: 'nginx'
---

## 症状

nginxを使ったリバースプロキシ構成でブラウザに以下が表示される。

```
502 Bad Gateway
nginx/1.xx.x
```

## 環境

- nginx
- Docker / Linux

## 原因と解決方法

### 原因1：バックエンドサービスが起動していない

nginxが転送先のサービス（Node.js・Python・Railsなど）に接続できない。

#### 確認方法

```bash
# サービスの状態を確認
systemctl status アプリ名
docker ps                    # Dockerの場合

# ポートが開いているか確認
ss -tlnp | grep 3000
```

#### 解決方法

バックエンドサービスを起動する。

```bash
systemctl start アプリ名
docker start コンテナ名
```

### 原因2：nginxの設定でポートが間違っている

```nginx
# 間違い
location / {
    proxy_pass http://localhost:3001;  # 実際は3000で動いている
}

# 正解
location / {
    proxy_pass http://localhost:3000;
}
```

### 原因3：Docker環境でのホスト名が間違っている

docker-compose環境ではlocalhostではなくサービス名を使う。

```nginx
# 間違い
proxy_pass http://localhost:3000;

# 正解（サービス名を使う）
proxy_pass http://app:3000;
```

### 原因4：バックエンドの起動に時間がかかっている

起動直後にアクセスすると502になることがある。
数秒待ってからアクセスする。

## ログで確認する

```bash
tail -f /var/log/nginx/error.log
```

エラーの詳細が確認できる。

## ハマったポイント

- Docker環境では `localhost` ではなくサービス名でアクセスする
- バックエンドが起動していない場合が一番多い
- `nginx -t` で設定ファイルの構文チェックをする

## 関連記事

- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerのポートが既に使用中エラーが出た時の対処法](/posts/docker-port-already-in-use)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
