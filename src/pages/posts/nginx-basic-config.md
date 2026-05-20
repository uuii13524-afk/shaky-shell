---
title: 'nginxの基本的な設定ファイルの書き方'
date: '2026-05-20'
category: 'nginx'
---

## やりたかったこと

nginxの設定ファイルを書けるようになりたかった。
最低限の設定をまとめる。

## 環境

- nginx
- Linux / Docker

## 設定ファイルの場所

```
/etc/nginx/nginx.conf          # メイン設定ファイル
/etc/nginx/conf.d/             # サイト別の設定ファイル
/etc/nginx/sites-available/    # Ubuntuでよく使われる場所
```

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

## よく使う設定

### HTTPSリダイレクト

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

### リバースプロキシ

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 静的ファイルのキャッシュ設定

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, no-transform";
}
```

## 設定の確認とリロード

```bash
nginx -t                    # 設定ファイルの構文チェック
nginx -s reload             # 設定をリロード（再起動不要）
systemctl restart nginx     # nginxを再起動
systemctl status nginx      # nginxの状態確認
```

## ハマったポイント

- 設定変更後は必ず `nginx -t` で構文チェックをしてから `nginx -s reload`
- `server_name` にドメインを正しく設定しないと意図した設定が適用されない
- セミコロン `;` が抜けるとエラーになる
- ログは `/var/log/nginx/error.log` で確認できる

## 関連記事

- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)
