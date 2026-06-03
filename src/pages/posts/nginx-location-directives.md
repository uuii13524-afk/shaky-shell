---
title: 'nginxのlocationディレクティブの書き方と優先順位'
date: '2026-06-01'
category: 'nginx'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['nginx', 'location', 'サーバー設定', 'Webサーバー']
en_tags: ['nginx', 'location directive', 'server config', 'web server']
description: 'nginxのlocationディレクティブの書き方と優先順位を解説。完全一致・前方一致・正規表現の違いや実用的な設定例をまとめた。'
---
## やりたかったこと
nginxの設定でURLごとに別々の処理をしたかった。
`/api/` のパスだけバックエンドに転送して、それ以外は静的ファイルを返す設定を書こうとしたらlocationの書き方で詰まった。

## locationディレクティブの種類

### 完全一致（= 修飾子）
```nginx
location = /favicon.ico {
    log_not_found off;
    access_log off;
}
```
- URLが完全に一致した場合だけマッチする
- 優先度が最も高い
- faviconやrobots.txtのログを抑制するのによく使う

### 前方一致（修飾子なし）
```nginx
location /api/ {
    proxy_pass http://localhost:3000;
}
```
- `/api/` から始まるすべてのURLにマッチする
- 設定がシンプルで一番よく使う

### 前方一致優先（^~ 修飾子）
```nginx
location ^~ /static/ {
    root /var/www;
}
```
- マッチしたら正規表現ブロックの評価をスキップする
- 静的ファイルを正規表現より優先したい時に使う

### 正規表現（~ または ~* 修飾子）
```nginx
# 大文字小文字を区別する
location ~ \.php$ {
    fastcgi_pass unix:/run/php/php8.2-fpm.sock;
    include fastcgi_params;
}

# 大文字小文字を区別しない
location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2)$ {
    expires 30d;
    access_log off;
}
```
- `~` は大文字小文字を区別する
- `~*` は区別しない
- 画像・CSS・JSなどの静的ファイルキャッシュ設定によく使う

## マッチの優先順位

1. `=` 完全一致（最優先）
2. `^~` 前方一致優先（正規表現をスキップ）
3. `~` または `~*` 正規表現（定義順で評価）
4. 修飾子なしの前方一致（最長一致）

## よく使う設定例

### PHPアプリとAPIの振り分け
```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/html;

    location = / {
        index index.php;
    }

    location /api/ {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/run/php/php8.2-fpm.sock;
        include fastcgi_params;
    }
}
```

### 静的ファイルのキャッシュ設定
```nginx
location ~* \.(jpg|jpeg|png|gif|ico|svg|css|js|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}
```

## ハマったポイント
- `=` は完全一致なので `/favicon.ico/` のようなスラッシュ付きにはマッチしない
- 正規表現ブロックは定義した順番で評価されるので、より厳密なパターンを先に書く
- `proxy_pass` の末尾スラッシュの有無でパスの扱いが変わる（`/api/foo` → `/foo` になる場合がある）
- location をネストする時は `alias` と `root` の違いに注意（`alias` はパスを置換する）
- 設定変更後は `nginx -t` でテストしてから `systemctl reload nginx` するのが安全

## 関連記事
- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [nginxのリバースプロキシ設定（Node.jsアプリをnginxで公開する）](/posts/nginx-reverse-proxy)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [nginxにLet's EncryptのSSL証明書を設定する方法（certbot）](/posts/nginx-ssl-certbot)
- [nginxでgzip圧縮を有効にしてページを高速化する](/posts/nginx-gzip-compression)

## おすすめのVPS／ドメイン／スクール
VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
