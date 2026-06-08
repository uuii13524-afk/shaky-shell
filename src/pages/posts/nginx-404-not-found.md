---
title: 'nginxで404 Not Foundが出る原因と対処法'
date: '2026-06-07'
category: 'nginx'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['nginx', '404', 'Not Found', 'サーバー設定', 'Linux']
en_tags: ['nginx', '404', 'not found', 'server config', 'linux']
description: 'nginxで404 Not Foundが出る原因と解決方法。rootパスのミス・locationの書き方・ファイルパーミッションなど実際に詰まった点をまとめた。'
---
## やりたかったこと

VPSにnginxを入れてNext.jsのビルド済み静的ファイルを配信しようとしたら、どのURLを叩いても404 Not Foundしか返ってこなかった。設定ファイルはドキュメントのコピペなのに全然動かなくて、原因を探すのに2時間かかった。

## 環境

- Ubuntu 22.04
- nginx 1.18.0
- Next.js 14.x（静的エクスポート、`out/` ディレクトリに出力）

## nginxの404が出る主な原因

### 原因1: rootパスが存在しないか空

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/html/out;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

`root` に指定したディレクトリが実際にあるか確認する。

```bash
ls -la /var/www/html/out
```

ディレクトリが存在しない・空だと問答無用で404になる。Next.jsなら `npm run build` のあとに `npm run export`（またはOutputの設定）を実行してから配置する必要があった。

### 原因2: SPAなのにtry_filesが=404で終わっている

```nginx
# SPAで全ページ404になるパターン
location / {
    try_files $uri $uri/ =404;
}
```

```nginx
# 正しい設定
location / {
    try_files $uri $uri/ /index.html;
}
```

`=404` を最後に書くと、ファイルが直接存在しないURLはすべて404になる。React/Next.js/Vue.jsのSPAはパスがファイルに対応していないので、`/index.html` にフォールバックさせる必要がある。

### 原因3: ファイルのパーミッションが足りない

```bash
# nginxはwww-dataユーザーで動いている
ls -la /var/www/html/out/

# 755または644以上が必要
chmod -R 755 /var/www/html/out
chown -R www-data:www-data /var/www/html/out
```

ownerがrootのままだとnginxが読めずに403や404が返ることがある。

### 原因4: rootとaliasの挙動の違い

```nginx
# rootはlocationのパスを含めたパスでファイルを探す
location /static/ {
    root /var/www/files;
    # /static/foo.js → /var/www/files/static/foo.js を探す
}

# aliasはlocationのパスを除いたパスで探す
location /static/ {
    alias /var/www/files/;
    # /static/foo.js → /var/www/files/foo.js を探す
}
```

`root` を使うと `/static/` ディレクトリがファイルパスに含まれてしまう。意図によってどちらを使うか決める必要がある。

## 試したこと・うまくいかなかったこと

### nginx -tをやらずに再起動を繰り返した

設定を直すたびに `systemctl restart nginx` していたが、何も変わらなかった。
しばらくして気づいたが、設定に構文エラーがあってnginxが古い設定のまま動き続けていた。

```bash
# 構文チェックを先にやる
nginx -t

# エラーがなければリロード
systemctl reload nginx
```

`nginx -t` が FAILED のままでは `reload` しても `restart` しても設定は更新されない。

### エラーログを見ていなかった

404の原因を設定ファイルだけ見て探していたが、エラーログを見たら一発でわかった。

```bash
tail -f /var/log/nginx/error.log
```

```
2026/06/07 10:23:14 [error] 1234#1234: *1 "/var/www/html/out/about/index.html" is not found
```

ログを最初から見ていれば30分は無駄にしなかった。

## 解決策

`nginx -t` で構文エラーを確認し、rootのパスとファイルのパーミッションを修正したら直った。

```bash
# 確認の手順
nginx -t
ls -la /var/www/html/out/index.html
chown -R www-data:www-data /var/www/html/out
chmod -R 755 /var/www/html/out
systemctl reload nginx

# ログで確認
tail -f /var/log/nginx/error.log
```

エラーログに `is not found` が出ていたら rootのパスかパーミッションが原因。`Permission denied` が出ていたら chmod/chown が必要。

## ハマったポイント

- `nginx -t` を最初にやらなかったせいで、設定が反映されていないまま何度も確認ループした
- `root` と `alias` の動作が違うことを知らなくて、同じパスを書いているのに404になるケースに遭遇した
- SPAで `try_files $uri $uri/ =404` を使っていたせいで直リンクが全部404になった。`/index.html` へのフォールバックが必要だった
- `chown` でオーナーを変えたのに `chmod` を忘れていて、パーミッション不足で404が続いた
- エラーログを後から見たら原因が一行で書いてあった。最初にログを見る習慣を付けるべきだった

## 関連記事

- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [nginxのlocationディレクティブの書き方と優先順位](/posts/nginx-location-directives)
- [nginxのリバースプロキシ設定（Node.jsアプリをnginxで公開する）](/posts/nginx-reverse-proxy)
- [Linuxのファイルパーミッション（chmod/chown）完全ガイド](/posts/linux-file-permissions)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
