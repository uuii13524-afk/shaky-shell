---
title: 'nginxのリバースプロキシ設定（Node.jsアプリをnginxで公開する）'
date: '2026-05-23'
category: 'nginx'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['nginx', 'リバースプロキシ', 'Node.js', 'VPS']
en_tags: ['nginx', 'reverse proxy', 'Node.js', 'VPS']
---

## やりたかったこと

Node.jsで作ったアプリをVPS上でnginxを使って公開したかった。
ポート3000で動いているアプリを80番・443番ポートで外部公開するためにリバースプロキシの設定が必要だった。

## リバースプロキシの仕組み

```
クライアント → nginx（80/443）→ Node.jsアプリ（3000）
```

nginxがリクエストを受けてバックエンドのアプリに転送する。
直接アプリのポートを公開しなくて済むのでセキュリティ面でも有利。

## 基本的なリバースプロキシ設定

`/etc/nginx/sites-available/myapp` を作成する。

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

シンボリックリンクを作成して有効化する。

```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Node.jsアプリ側の設定

アプリはlocalhost（127.0.0.1）でlistenするだけでよい。

```js
const express = require('express');
const app = express();

app.listen(3000, '127.0.0.1', () => {
  console.log('Server running on port 3000');
});
```

外部に直接ポート3000を公開しない場合はファイアウォールで塞いでおく。

```bash
sudo ufw deny 3000
sudo ufw allow 80
sudo ufw allow 443
```

## WebSocketのプロキシ設定

WebSocketを使う場合は追加のヘッダーが必要。

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

`Upgrade` と `Connection` ヘッダーがないとWebSocketのハンドシェイクが失敗する。

## 複数アプリを同一サーバーで動かす

ドメインやパスで振り分けることができる。

```nginx
# ドメインで振り分け
server {
    listen 80;
    server_name app1.example.com;
    location / {
        proxy_pass http://localhost:3000;
    }
}

server {
    listen 80;
    server_name app2.example.com;
    location / {
        proxy_pass http://localhost:4000;
    }
}
```

```nginx
# パスで振り分け
server {
    listen 80;
    server_name example.com;

    location /api/ {
        proxy_pass http://localhost:3000/;
    }

    location / {
        proxy_pass http://localhost:4000;
    }
}
```

## SSL（HTTPS）対応

CertbotでSSLを設定すると `/etc/nginx/sites-available/myapp` が自動で書き換えられる。

```bash
sudo certbot --nginx -d example.com
```

Certbotが `proxy_pass` の設定はそのままにしてSSLの設定だけ追加してくれる。

## ハマったポイント

- `proxy_set_header Host $host;` を忘れるとバックエンド側でホスト名が取れない
- `proxy_http_version 1.1;` を指定しないとWebSocketが接続できない
- `proxy_pass http://localhost:3000/;` の末尾スラッシュの有無でパスの扱いが変わる（末尾スラッシュありだとlocationのパス部分が除去される）
- Node.jsアプリが127.0.0.1でlistenしていないと `502 Bad Gateway` になる
- `nginx -t` でテストしてからreloadしないと設定ミスで本番が落ちる

リバースプロキシの設定後にHTTPSも対応させたい場合は[nginxにLet's EncryptのSSL証明書を設定する方法（certbot）](/posts/nginx-ssl-certbot)で無料のSSL証明書を取得できる。

## 関連記事

- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [CertbotでnginxにSSL証明書を設定する方法](/posts/nginx-ssl-certbot)
- [VPSにDockerとnginxをセットアップする手順](/posts/vps-docker-setup)
- [Linuxのファイアウォール設定（ufw）](/posts/linux-firewall-ufw)

## おすすめのVPS／ドメイン

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
