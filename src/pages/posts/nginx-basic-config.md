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

nginxを外部に公開する前に[LinuxのUFWファイアウォール設定の基本](/posts/linux-firewall-ufw)でポート80・443を開放しておくことを忘れずに。

## ConoHa VPSでDockerを本番環境で使う

ローカルでDockerを動かせるようになったら、次は本番サーバーへの展開です。
ConoHa VPSならDockerがすぐに使える環境を低コストで用意できます。

<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4YQYYA" rel="nofollow">ConoHa VPSを見てみる →</a>
<img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4YQYYA" alt="">

## XServer VPSで本番環境を用意する

ローカルでの動作確認ができたら、次は本番サーバーへの展開です。
XServer VPSなら高性能な環境を低コストで用意できます。

<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25ES2Q" rel="nofollow">エックスサーバーのVPSサーバー</a>
<img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25ES2Q" alt="">

## 関連記事

- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
- [Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)


## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
