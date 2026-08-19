---
title: 'nginxで403 Forbiddenが出た時の対処法'
date: '2026-07-20'
category: 'nginx'
layout: '../../layouts/PostLayout.astro'
description: 'nginxでcurlが403 Forbiddenを返す症状を解説します。原因はindex.html自体ではなく/home/deployなど祖先ディレクトリの実行権限不足で、namei -lで特定しchmod o+xで解決する手順を紹介します。'
ja_tags: ['nginx', '403', 'Forbidden', 'パーミッション', 'Linux']
en_tags: ['nginx', '403', 'forbidden', 'permission', 'linux']
---

## やりたかったこと（または「症状」）

VPS上でnginxを設定し直して静的サイトを配信しようとしたら、ブラウザでもcurlでも403 Forbiddenしか返ってこなくなった。設定ファイル自体は前日まで動いていたものをコピーしただけなので、どこが悪いのか見当がつかず、1時間近く同じ設定を読み返す羽目になった。

```text
$ curl -I https://example.com/
HTTP/1.1 403 Forbidden
Server: nginx/1.24.0
Date: Mon, 20 Jul 2026 09:12:03 GMT
Content-Type: text/html
Content-Length: 153
Connection: keep-alive
```

---

## 環境

- OS: Ubuntu 22.04 LTS（さくらのVPS）
- nginx: 1.24.0（Ubuntu標準パッケージ）
- デプロイ方法: `rsync` でビルド済みの静的ファイルを `/var/www/example.com/html` に転送
- 実行ユーザー: デプロイ用の一般ユーザー `deploy`（rootではない）

---

## 試したこと

最初に、403は権限系のエラーだと分かっていたので `root` ディレクティブのパスを疑い、`ls -la` でディレクトリの中身を確認した → ファイルは存在していて中身も正しかった → パスの指定ミスではないという結論になり、この時点では原因が分からなかった。

```bash
ls -la /var/www/example.com/html
```

```text
total 12
drwxr-xr-x 2 deploy deploy 4096 Jul 20 09:00 .
drwxr-xr-x 3 deploy deploy 4096 Jul 19 22:10 ..
-rw-r--r-- 1 deploy deploy  612 Jul 20 09:00 index.html
```

次に、`index.html` のパーミッションが `644` で読み取り可能になっていることを確認したうえで `systemctl restart nginx` を実行してみたが、403は変わらなかった。ファイル自体のパーミッションは問題なく、別の層で止められていると気づいたのはこの後だった。

```bash
systemctl restart nginx
curl -I https://example.com/
```

```text
HTTP/1.1 403 Forbidden
```

---

## 原因

nginxがファイルを配信するには、`index.html` 自体の読み取り権限だけでなく、`root` に指定したパスの**祖先ディレクトリすべて**に、nginxの実行ユーザー（多くの場合 `www-data`）が「通過（実行権限 `x`）」できる権限を持っている必要がある。今回は `rsync` でデプロイした際にホームディレクトリ配下 `/home/deploy/www` を経由しており、途中の `/home/deploy` のパーミッションが `750` になっていたため、`www-data` がそのディレクトリを通過できずファイルにたどり着けなかった。ファイル単体の権限だけを見ていても気づけない原因だった。

---

## 解決方法

### 経路上のディレクトリ権限を1階層ずつ確認する

```bash
namei -l /var/www/example.com/html/index.html
```

```text
f: /var/www/example.com/html/index.html
drwxr-xr-x root     root     /
drwxr-xr-x root     root     var
drwxr-xr-x root     root     www
drwxr-xr-x deploy   deploy   example.com
drwxr-xr-x deploy   deploy   html
-rw-r--r-- deploy   deploy   index.html
```

`namei -l` を使うと、ルートから対象ファイルまでの全階層のパーミッションと所有者を一度に確認できる。今回は `/var/www` 配下は問題なく、実際に権限が欠けていたのは別サーバーで検証していた `/home/deploy/www` 構成の方だった。

### 実行権限が欠けているディレクトリにxを付与する

```bash
chmod o+x /home/deploy
```

```text
（出力なし。実行後にnamei -lで750→755になったことを確認）
```

ディレクトリの実行権限（`x`）は「そのディレクトリの中に入って中身を参照する権限」を意味する。書き込み権限とは独立しているため、他人に書き換えさせずに配信だけ許可したい場合はこの `o+x` の付与だけで十分になる。

### nginxのエラーログで裏付けを取る

```bash
tail -n 5 /var/log/nginx/error.log
```

```text
2026/07/20 09:11:58 [error] 812#812: *3 open() "/home/deploy/www/index.html" failed (13: Permission denied), client: 203.0.113.5, server: example.com, request: "GET / HTTP/1.1"
```

`(13: Permission denied)` が出ていれば原因はパーミッションであり、パスの指定ミス（`is not found`）とは切り分けられる。この行を最初に確認していれば、`root` パスそのものを疑う遠回りをせずに済んだ。

---

## ハマったポイント

- `index.html` のパーミッションだけを `ls -la` で確認して安心してしまい、祖先ディレクトリの権限まで見ていなかったせいで30分以上原因が分からなかった
- ホームディレクトリ配下（`/home/deploy/www`）を公開ディレクトリとして使っていたため、Ubuntuのデフォルト設定 `750` がそのまま残っていて `www-data` から読めなかった
- `chmod -R 755` を対象ディレクトリに一括で使いそうになったが、それだと祖先ディレクトリの権限までは変わらないため意味がなかった。祖先を1階層ずつ `o+x` する必要があった
- エラーログを見る前に `systemctl restart` を何度も試していて、無駄な再起動を繰り返した

---

## よくある質問

**Q: nginxで403 Forbiddenとindex.htmlがありませんの違いは？**
403はファイルの存在は確認できているがアクセス権限がなくて拒否されている状態、404はファイル自体が見つからない状態を指す。エラーログに `Permission denied` と出ていれば403系のパーミッション問題、`No such file or directory` と出ていれば404系のパス問題として切り分けられる。

**Q: index_forbiddenと表示される場合との違いは？**
`autoindex` が無効な状態でディレクトリに `index.html` が存在しない場合、nginxはディレクトリ一覧を返そうとして拒否する「index.html」の`index_forbidden`というエラーになる。これはパーミッションではなく `index` ファイルの有無が原因なので、`ls` で対象ディレクトリに `index.html` があるか先に確認するとよい。

**Q: /var/www配下ならこの問題は起きない？**
`/var/www` はデフォルトで祖先ディレクトリが `755` になっていることが多く起きにくいが、`/home/ユーザー名/...` のようにホームディレクトリ配下を公開パスにすると、Ubuntuのデフォルトのホームディレクトリ権限 `750` が原因で同じ403が起きやすい。公開用ディレクトリは `/var/www` 配下に置くのが無難。

---

## 関連記事

- [nginxで404 Not Foundが出る原因と対処法](/posts/nginx-404-not-found)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [nginxのlocationディレクティブの書き方と優先順位](/posts/nginx-location-directives)
- [Linuxのファイルパーミッション（chmod/chown）完全ガイド](/posts/linux-file-permissions)
