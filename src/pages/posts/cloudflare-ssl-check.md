---
title: 'Cloudflareで独自ドメインのSSL設定を確認する方法'
date: '2026-05-07'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

独自ドメインがhttpsで正しく表示されるか確認したかった。

## SSL設定の確認方法

1. Cloudflareダッシュボード→対象ドメイン
2. 左メニュー「SSL/TLS」→「Overview」

推奨設定：「Full」（Cloudflare Pages使用時）

## HTTPSリダイレクトの設定

「SSL/TLS」→「Edge Certificates」→「Always Use HTTPS」をオンにする。

## 症状別の対処法

- 「安全ではない」→SSL/TLSを「Full」に変更
- 証明書エラー→15分〜24時間待つ
- Mixed Contentエラー→URLをHTTPSに変更

SSL設定が完了したら、不要なポートを閉じるために[Cloudflareでリダイレクトルールを設定する方法](/posts/cloudflare-redirect-rules)でHTTP→HTTPSのリダイレクトも合わせて確認しておくとよい。

## 関連記事

- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
- [XserverドメインのネームサーバーをCloudflareに変更する方法](/posts/xserver-cloudflare-nameserver)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
