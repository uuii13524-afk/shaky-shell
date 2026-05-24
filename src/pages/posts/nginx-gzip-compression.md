---
title: 'nginxでgzip圧縮を有効にしてページを高速化する'
date: '2026-05-24'
category: 'nginx'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['nginx', 'gzip', 'パフォーマンス']
en_tags: ['nginx', 'gzip', 'performance']
---

## やりたかったこと

nginxで配信しているサイトのレスポンスが遅かった。
gzip圧縮を有効にすればファイルサイズが小さくなって速くなると聞いたので設定してみた。

## gzip圧縮とは

テキスト系のファイル（HTML・CSS・JS・JSONなど）を圧縮して転送するしくみ。
ブラウザ側で自動的に解凍してくれるので、ユーザーには影響ない。
圧縮率は種類によるが、JSやCSSは70〜80%削減できることもある。

## 設定ファイルを編集する

```bash
sudo nano /etc/nginx/nginx.conf
```

`http` ブロック内に以下を追加する。

```nginx
http {
    # gzip設定
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_types
        text/plain
        text/css
        text/xml
        application/json
        application/javascript
        application/xml
        application/xml+rss
        text/javascript
        image/svg+xml;
}
```

## 各設定の意味

| 設定 | 内容 |
|------|------|
| `gzip on` | gzip圧縮を有効にする |
| `gzip_vary on` | `Vary: Accept-Encoding` ヘッダーを付与する（CDN対応） |
| `gzip_proxied any` | プロキシ経由のリクエストも圧縮する |
| `gzip_comp_level 6` | 圧縮レベル（1〜9、6がバランス良い） |
| `gzip_types` | 圧縮するMIMEタイプ（画像は基本除外） |

## 設定を反映して確認する

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 圧縮が効いているか確認する

```bash
curl -H "Accept-Encoding: gzip" -I https://example.com
```

レスポンスヘッダーに `Content-Encoding: gzip` が出れば成功。

```
HTTP/2 200
content-type: text/html
content-encoding: gzip
```

Chrome DevToolsでも確認できる。
`Network` タブ → ファイルを選択 → `Response Headers` に `content-encoding: gzip` があればOK。

## サイトごとに設定する場合

`/etc/nginx/sites-available/` の個別設定ファイルで `server` ブロック内に書いても動く。

```nginx
server {
    listen 80;
    server_name example.com;

    gzip on;
    gzip_types text/css application/javascript;

    location / {
        root /var/www/html;
    }
}
```

## ハマったポイント

- `gzip_types` に `text/html` は書かなくてよい（`gzip on` にすると自動で対象になる）
- 画像（jpg/png/webp）はすでに圧縮済みなので `gzip_types` に入れても意味がない
- `gzip_comp_level` を9にすると圧縮率は上がるがCPU負荷も上がる。6で十分
- Cloudflare経由のサイトはCloudflare側でも圧縮されるので、nginxでの設定が上書きされることがある
- `gzip_vary on` を忘れるとCDNがgzip版と非gzip版を区別できずキャッシュがおかしくなる

## 関連記事

- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [nginxでリバースプロキシを設定する方法](/posts/nginx-reverse-proxy)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [CertbotでSSL証明書を取得する（nginx編）](/posts/nginx-ssl-certbot)

## おすすめのVPS／ドメイン

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
