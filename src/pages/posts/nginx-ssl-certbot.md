---
title: "nginxにLet's EncryptのSSL証明書を設定する方法（certbot）"
date: '2026-05-23'
category: 'nginx'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['nginx', 'SSL', 'certbot', 'HTTPS', "Let's Encrypt"]
en_tags: ['nginx', 'SSL', 'certbot', 'HTTPS', "Let's Encrypt"]
description: 'nginxにcertbotでSSL証明書を取得・設定してHTTPS化する手順を解説。無料SSL証明書の自動更新設定方法もわかりやすく紹介します。'
---

## やりたかったこと

VPSで動かしているnginxにSSL証明書を設定して、HTTPSでアクセスできるようにしたかった。
Let's Encryptの証明書はcertbotを使えば無料で取得できる。

## certbotをインストールする

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

## SSL証明書を取得する

```bash
sudo certbot --nginx -d example.com -d www.example.com
```

対話形式で進む。メールアドレスを入力して、HTTPSへのリダイレクトを選ぶだけ。

```
Enter email address: your@email.com
(A)gree/(C)ancel: A
(Y)es/(N)o: N
Select the appropriate number [1-2]: 2
```

## nginxの設定が自動で変わる

certbotがnginxの設定ファイルを自動で書き換えてくれる。

```nginx
server {
    listen 443 ssl;
    server_name example.com www.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        root /var/www/html;
        index index.html;
    }
}

server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$host$request_uri;
}
```

## 証明書の自動更新

Let's Encryptの証明書は90日で期限切れになる。certbotはsystemdタイマーで自動更新してくれる。

```bash
# 自動更新のテスト
sudo certbot renew --dry-run
```

```bash
# タイマーの状態を確認
sudo systemctl status certbot.timer
```

## よく使うコマンド

```bash
# 証明書の一覧を見る
sudo certbot certificates

# 手動で証明書を更新
sudo certbot renew

# 特定の証明書を削除
sudo certbot delete --cert-name example.com

# nginxの設定構文チェック
sudo nginx -t

# nginxをリロード
sudo systemctl reload nginx
```

## ハマったポイント

- ポート80が閉じていると証明書の取得に失敗する（ufwでポートを開けておく）
- Cloudflare経由の場合はオレンジ雲をグレー（DNSのみ）にしてからcertbotを実行する
- `www.`ありとなしの両方を`-d`で指定しないと、片方がHTTPSにならない
- `server_name`が正しく設定されていないとcertbotがnginxを認識しない
- VPSのIPとドメインのDNS設定が一致していないと失敗する

certbot実行前にUFWでポート80を開放しておく必要がある。[LinuxのUFWファイアウォール設定の基本](/posts/linux-firewall-ufw)で `sudo ufw allow 80` を確認してほしい。

## 関連記事

- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [Linuxのファイアウォール設定（ufw）](/posts/linux-firewall-ufw)
- [VPSでDockerを使う基本的なセットアップ](/posts/vps-docker-setup)
- [SSHの基本的な使い方](/posts/linux-ssh-basics)

## おすすめのVPS／ドメイン

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
