---
title: 'nginxの基本的な設定ファイルの書き方'
date: '2026-05-12'
category: 'nginx'
layout: '../../layouts/PostLayout.astro'
---

## 基本的な設定ファイル

```nginx
server {
    listen 80;
    server_name example.com;

    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

## リバースプロキシ

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}
```

## 設定の確認とリロード

```bash
nginx -t          # 構文チェック
nginx -s reload   # リロード
```

## ハマったポイント

- 設定変更後は必ず `nginx -t` してから `nginx -s reload`
- セミコロン `;` が抜けるとエラー

## 関連記事

- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
- [Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)
