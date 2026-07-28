---
title: 'nginxで413 Request Entity Too Largeが出た時の対処法'
date: '2026-07-28'
category: 'nginx'
layout: '../../layouts/PostLayout.astro'
description: 'nginxをリバースプロキシとして立てたAPIサーバーに大きめのファイルをアップロードすると413 Request Entity Too Largeで弾かれる症状を解説。原因のclient_max_body_size制限と、設定追記からリロードまでの解決手順を紹介します。'
ja_tags: ['nginx', '413', 'Request Entity Too Large', 'client_max_body_size']
en_tags: ['nginx', '413', 'Request Entity Too Large', 'client_max_body_size']
---

## やりたかったこと（または「症状」）

さくらのVPSに構築したNode.js製の画像アップロードAPI（Express + multer）の前段に、nginxをリバースプロキシとして置いていた。ローカルでは問題なく動いていたので、本番環境でも動作確認のつもりで少し大きめの画像ファイル（約15MB）を`curl`でアップロードしてみたところ、以下のエラーで弾かれた。

```bash
curl -X POST https://api.example.com/upload \
  -F "file=@./sample-photo.jpg"
```

```text
<html>
<head><title>413 Request Entity Too Large</title></head>
<body>
<center><h1>413 Request Entity Too Large</h1></center>
<hr><center>nginx/1.24.0 (Ubuntu)</center>
</body>
</html>
```

同じエンドポイントに1MB程度の小さい画像を送ると成功するのに、ファイルサイズを上げただけで413になる。Expressアプリ側のコードは一切変更していなかったので、最初はどこで弾かれているのか見当がつかなかった。

## 環境

- OS: Ubuntu 22.04.4 LTS（さくらのVPS）
- nginx: 1.24.0（`apt`経由でインストール）
- バックエンド: Node.js 20.11.1 + Express 4.19.2 + multer 1.4.5-lts.1（アップロード先ポート3000）
- 構成: nginxがリバースプロキシとしてポート443で待ち受け、`proxy_pass`でExpressアプリへ転送

## 試したこと

まずExpress側のボディサイズ制限を疑った。`express.json()`や`express.urlencoded()`にはデフォルトで100kb程度の上限があると聞いたことがあったからだ。multerの設定を確認したが、`limits`オプション自体を指定しておらず、multer側には特にサイズ制限をかけていなかった。

```js
const upload = multer({ dest: 'uploads/' });
```

念のためExpressアプリを直接（nginxを経由せず）ポート3000にリクエストしてみることにした。VPS内で`curl`をローカルホスト宛に実行する。

```bash
curl -X POST http://localhost:3000/upload \
  -F "file=@./sample-photo.jpg"
```

```text
{"status":"ok","filename":"1721958812345-sample-photo.jpg","size":15234871}
```

nginxを経由しなければ同じ15MBのファイルが問題なくアップロードできた。これでExpress・multer側には制限がなく、nginxの層でリクエストが止められていると分かった。次にnginxのエラーログを確認した。

```bash
sudo tail -n 5 /var/log/nginx/error.log
```

```text
2026/07/28 10:42:03 [error] 8821#8821: *14 client intended to send too large body: 15728694 bytes, client: 203.0.113.45, server: api.example.com, request: "POST /upload HTTP/1.1", host: "api.example.com"
```

`client intended to send too large body`という記述から、nginxが自身のボディサイズ上限に基づいてリクエストを拒否していることが確定した。アップストリーム（Expressアプリ）に転送する前の時点で、nginx自身が413を返していた。

## 原因

nginxには`client_max_body_size`というディレクティブがあり、クライアントからのリクエストボディの最大サイズを制御している。このディレクティブのデフォルト値は`1m`（1メガバイト）で、明示的に設定を変更していない限り、それを超えるボディを持つリクエストはアップストリームへ転送される前にnginx自身が`413 Request Entity Too Large`で即座に拒否する。今回のケースでは15MBのファイルを送っていたため、デフォルトの1MB制限に引っかかっていた。1MB程度の小さいテスト画像では制限内に収まっていたため、たまたま成功していたにすぎない。

## 解決方法

### 1. nginxの設定ファイルに`client_max_body_size`を追記する

```bash
sudo nano /etc/nginx/sites-available/api.example.com.conf
```

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    client_max_body_size 20m;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

`server`ブロック直下に`client_max_body_size 20m;`を追加した。今回扱う画像は最大でも数十MB程度と想定していたため、少し余裕を持たせて20MBに設定した。

### 2. 設定ファイルの文法をチェックする

```bash
sudo nginx -t
```

```text
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

`nginx -t`で構文エラーがないことを確認してからリロードする。ここでエラーが出た場合、リロードすると最悪の場合nginxが起動しなくなるため、必ずこの手順を先に行う。

### 3. nginxをリロードして反映する

```bash
sudo systemctl reload nginx
```

`restart`ではなく`reload`を使うことで、既存のコネクションを切断せずに設定だけを再読み込みできる。

### 4. 再度同じファイルでアップロードを確認する

```bash
curl -X POST https://api.example.com/upload \
  -F "file=@./sample-photo.jpg"
```

```text
{"status":"ok","filename":"1721958933210-sample-photo.jpg","size":15234871}
```

413エラーは出なくなり、15MBのファイルがExpressアプリまで届いて正常にレスポンスが返ってきた。

## ハマったポイント

- 最初は`server`ブロックではなく`http`ブロックに設定を書こうとしたが、複数の`server_name`を1つの`nginx.conf`で管理していたため、他のサーバーブロックにまで制限が影響しないよう、あえて対象の`server`ブロック内に限定して記述した
- `client_max_body_size 0;`にすれば上限なしにできると知ったが、意図しない巨大アップロードやDoS的なリクエストを受け付けてしまうリスクがあるため、想定する最大ファイルサイズより少し大きい程度の具体的な値（`20m`）に留めた
- Cloudflareを経由する構成だったため、Cloudflare自体のアップロード上限（無料プランは100MB）にも別途引っかかる可能性があると気づいた。nginx側だけ上限を上げても、Cloudflare側の上限を超えるリクエストは別のエラーになる
- `nginx -t`を省略して`systemctl reload nginx`を実行しそうになったが、タイプミスで`;`を書き忘れていたことに気づけたのは`nginx -t`のおかげだった

## よくある質問

**Q: `client_max_body_size`を極端に大きく（例: `1000m`）しておけば安心ですか？**
上限を大きくしすぎると、意図しない大容量アップロードや悪意あるリクエストによってディスクやメモリを圧迫するリスクが上がる。実際にアプリケーションが受け付ける想定の最大サイズより少し余裕を持たせる程度に留めるのが安全。

**Q: nginxの設定を直しても413が消えません。**
バックエンド側（今回でいうExpressやmulter、あるいはPHPの`upload_max_filesize`など）にも別のボディサイズ上限が設定されていることがある。`error.log`にどのタイミングでエラーが出ているか（nginxかアプリケーションか）を先に確認するとよい。

**Q: Dockerコンテナ内で動かしているnginxでも同じ設定でよいですか？**
基本的な考え方は同じで、コンテナ内の`nginx.conf`または`conf.d`配下の設定に`client_max_body_size`を追記すればよい。設定ファイルをホストからボリュームマウントしている場合は、変更後にコンテナ内で`nginx -s reload`するか、コンテナ自体を再起動する必要がある。

## 関連記事

- [nginxをリバースプロキシとして設定する方法](/posts/nginx-reverse-proxy)
- [nginxの基本設定ファイルの書き方](/posts/nginx-basic-config)
- [nginxのアクセスログを確認する方法](/posts/nginx-access-log)
- [nginxで403 Forbiddenが出た時の対処法](/posts/nginx-403-forbidden)
- [VPSにDockerをインストールしてWebサーバーを構築する方法](/posts/vps-docker-setup)
