---
title: 'Cloudflareで独自ドメインのSSL設定を確認する方法'
date: '2026-05-20'
category: 'Cloudflare'
---

## やりたかったこと

独自ドメインを設定したサイトがhttpsで正しく表示されるか確認したかった。
Cloudflareを使っている場合はSSL設定をCloudflare側で管理する。

## 環境

- Cloudflare
- 独自ドメイン

## SSL設定の確認方法

### 1. SSL/TLS設定を確認

1. Cloudflareダッシュボードにログイン
2. 対象ドメインをクリック
3. 左メニュー「SSL/TLS」をクリック
4. 「Overview」タブを確認

**推奨設定：「Full」または「Full (strict)」**

- Off：HTTPのみ。セキュリティなし
- Flexible：ブラウザ↔Cloudflare間のみHTTPS
- Full：全区間HTTPS。オリジンの証明書は自己署名でもOK
- Full (strict)：全区間HTTPS。オリジンの証明書が有効である必要がある

Cloudflare Pagesを使っている場合は「Full」でOK。

### 2. 証明書の確認

左メニュー「SSL/TLS」→「Edge Certificates」を確認。

「Universal SSL Status」が「Active Certificate」になっていれば証明書は有効。

### 3. HTTPSリダイレクトの設定

左メニュー「SSL/TLS」→「Edge Certificates」→「Always Use HTTPS」をオンにする。
これでHTTPアクセスを自動的にHTTPSにリダイレクトする。

## 症状別の対処法

### サイトにアクセスすると「安全ではない」と表示される

SSL/TLSの設定が「Off」または「Flexible」になっている可能性がある。
「Full」に変更する。

### 証明書エラーが表示される

証明書の発行に時間がかかっている場合がある。
ドメイン設定後15分〜24時間待つ。

### Mixed Contentエラーが出る

ページ内にHTTPのリソースが含まれている。
画像やスクリプトのURLをHTTPSに変更する。

## ハマったポイント

- ネームサーバーをCloudflareに変更しただけでは証明書が即座に有効にならない
- 証明書の発行は自動だが時間がかかる場合がある
- Cloudflare Pagesを使っている場合はSSL設定はほぼ自動で完了する
