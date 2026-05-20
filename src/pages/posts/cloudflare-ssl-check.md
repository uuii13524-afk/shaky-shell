---
title: 'Cloudflareで独自ドメインのSSL設定を確認する方法'
date: '2026-05-20'
category: 'Cloudflare'
---

## やりたかったこと

独自ドメインを設定したサイトがhttpsで正しく表示されるか確認したかった。

## 環境

- Cloudflare
- 独自ドメイン

## SSL設定の確認方法

1. Cloudflareダッシュボード→対象ドメイン
2. 左メニュー「SSL/TLS」→「Overview」

**推奨設定：「Full」**

- Off：HTTPのみ
- Flexible：ブラウザ↔Cloudflare間のみHTTPS
- Full：全区間HTTPS（Cloudflare Pages使用時はこれでOK）
- Full (strict)：オリジンの証明書が有効である必要がある

## HTTPSリダイレクトの設定

「SSL/TLS」→「Edge Certificates」→「Always Use HTTPS」をオンにする。

## 症状別の対処法

### 「安全ではない」と表示される

SSL/TLSの設定が「Off」または「Flexible」→「Full」に変更する。

### 証明書エラーが表示される

証明書の発行に時間がかかっている。15分〜24時間待つ。

### Mixed Contentエラー

ページ内にHTTPのリソースが含まれている。URLをHTTPSに変更する。

## ハマったポイント

- Cloudflare Pagesを使っている場合はSSL設定はほぼ自動で完了する
- 証明書の発行は自動だが時間がかかる場合がある

## 関連記事

- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
- [XserverドメインのネームサーバーをCloudflareに変更する方法](/posts/xserver-cloudflare-nameserver)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
