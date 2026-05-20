---
title: 'nginx 502 Bad Gatewayエラーの原因と解決方法'
date: '2026-05-20'
category: 'nginx'
---

## 症状

```
502 Bad Gateway
nginx/1.xx.x
```

## 原因と解決方法

### バックエンドサービスが起動していない

```bash
systemctl status アプリ名
docker ps
systemctl start アプリ名
```

### nginxの設定でポートが間違っている

```nginx
# 正解
location / {
    proxy_pass http://localhost:3000;
}
```

### Docker環境でのホスト名が間違っている

```nginx
# 間違い
proxy_pass http://localhost:3000;

# 正解（サービス名を使う）
proxy_pass http://app:3000;
```

## ログで確認する

```bash
tail -f /var/log/nginx/error.log
```

## ハマったポイント

- Docker環境では `localhost` ではなくサービス名でアクセスする
- バックエンドが起動していない場合が一番多い

## 関連記事

- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerでポートが既に使用中エラーが出た時の対処法](/posts/docker-port-already-in-use)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
