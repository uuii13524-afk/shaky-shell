---
title: 'nginxでレート制限（rate limiting）を設定する方法'
date: '2026-06-03'
category: 'nginx'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['nginx', 'レート制限', 'rate limiting', 'セキュリティ', 'DDoS対策']
en_tags: ['nginx', 'rate limiting', 'security', 'DDoS protection', 'web server']
description: 'nginxのlimit_req_zoneとlimit_reqディレクティブを使ってレート制限を設定する方法。APIへのブルートフォース攻撃やDDoS対策の基本を解説。'
---
## やりたかったこと
nginxで特定のURLへのリクエスト数を制限したかった。
APIエンドポイントへのブルートフォース攻撃や、過剰なリクエストをブロックするために設定してみた。

## limit_req_zoneを設定する

nginx.conf（または `/etc/nginx/conf.d/` 配下の設定ファイル）の `http` ブロックに追加する。

```nginx
http {
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
}
```

- `$binary_remote_addr`：クライアントのIPアドレスをキーにする
- `zone=mylimit:10m`：ゾーン名と共有メモリのサイズ（10MBで約16万IPを管理できる）
- `rate=10r/s`：1秒あたり10リクエストまで許可

`r/m` にすれば「1分あたり〇件」にもできる。

```nginx
limit_req_zone $binary_remote_addr zone=loginlimit:10m rate=5r/m;
```

## limit_reqでエンドポイントに適用する

`server` または `location` ブロックで制限を適用する。

```nginx
server {
    location /api/ {
        limit_req zone=mylimit burst=20 nodelay;
        proxy_pass http://localhost:3000;
    }
}
```

- `burst=20`：一時的に20リクエストまでのバーストを許可する
- `nodelay`：バーストしたリクエストを遅延なく処理し、超えたら即エラーを返す

`nodelay` を付けないと、超過したリクエストはキューに入って処理が遅延する。

## ログインページに厳しめの制限をかける

ブルートフォース対策にはバーストを小さく設定するといい。

```nginx
location /login {
    limit_req zone=loginlimit burst=5;
    proxy_pass http://localhost:3000;
}
```

## レスポンスコードを503から429に変更する

デフォルトは503（Service Unavailable）だが、429（Too Many Requests）のほうがHTTPの仕様として正しい。

```nginx
http {
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
    limit_req_status 429;
}
```

## 設定を反映する

```bash
# 構文チェック
sudo nginx -t

# リロード（サービス停止なし）
sudo systemctl reload nginx
```

## ハマったポイント
- `limit_req_zone` は `http` ブロックに書く。`server` や `location` に書くとエラーになる
- `burst` を設定しないと通常のユーザーも弾かれやすい。適切な値に調整が必要
- レート制限に引っかかったリクエストはエラーログに記録される。`/var/log/nginx/error.log` で確認できる
- クライアントがNATやリバースプロキシの後ろにいる場合は `$remote_addr` ではなく `$http_x_forwarded_for` を使う必要がある場合もある
- `nginx -t` で確認してから `reload` する。`restart` だと一瞬サービスが止まるので注意

## 関連記事
- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [nginxのlocationディレクティブの書き方と優先順位](/posts/nginx-location-directives)
- [nginxのリバースプロキシ設定（Node.jsアプリをnginxで公開する）](/posts/nginx-reverse-proxy)
- [LinuxのUFWファイアウォール設定の基本](/posts/linux-firewall-ufw)
- [nginxにLet's EncryptのSSL証明書を設定する方法（certbot）](/posts/nginx-ssl-certbot)

## おすすめのVPS／ドメイン／スクール
VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
