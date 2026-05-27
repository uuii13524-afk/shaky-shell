---
title: 'nginx 502 Bad Gatewayエラーの原因と解決方法'
date: '2026-05-20'
category: 'nginx'
layout: '../../layouts/PostLayout.astro'
description: 'nginx 502 Bad Gatewayエラーの原因調査と解決方法を解説。バックエンドサービスの起動確認・プロキシ設定ミスの特定方法を紹介します。'
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

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
