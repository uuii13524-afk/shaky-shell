---
title: 'XserverドメインのネームサーバーをCloudflareに変更する方法'
date: '2026-05-02'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

Cloudflare PagesにカスタムドメインをXserverで取得したドメインで設定したかった。

## 環境

- Xserverドメイン
- Cloudflare Pages

## 手順

1. Cloudflareで「Connect a domain」を選択
2. ネームサーバーが2つ発行される
3. Xserverのネームサーバー設定で「その他のサービスで利用する」を選択
4. 発行されたネームサーバーを1・2に入力
5. Cloudflareで「I updated my nameservers」を押す
6. 数十分〜1時間程度でActiveになる

## ハマったポイント

- CloudflareにはWorkers用とPages用の画面が別にあって迷った
- 反映まで時間がかかるので焦らず待つ
- Activeになってから改めてCustom domainsでドメインを設定する必要がある

## 関連記事

- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
- [Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
