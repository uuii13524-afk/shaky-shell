---
title: 'XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順'
date: '2026-05-05'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'XserverのドメインをCloudflare Pagesのカスタムドメインに設定する全手順を解説。ネームサーバー変更からDNS設定・HTTPS化まで紹介します。'
---

## やりたかったこと

Xserverで取得したドメインをCloudflare Pagesのカスタムドメインとして設定したかった。

## 環境

- Xserverドメイン
- Cloudflare Pages
- Astro

## 全体の流れ

```
Cloudflareでネームサーバーを確認
↓
XserverでネームサーバーをCloudflareに変更
↓
CloudflareでActive確認
↓
Cloudflare PagesにカスタムドメインをActivate
```

## 手順

### 1. CloudflareにドメインをConnect

1. 「Workers & Pages」→プロジェクト→「Custom domains」
2. 「Set up a custom domain」→ドメイン入力→「Continue」
3. 「Begin DNS transfer」→「Continue to activation」
4. Cloudflareのネームサーバーが2つ表示される

### 2. XserverでネームサーバーをCloudflareに変更

1. Xserverドメイン管理画面にログイン
2. 「ネームサーバー設定」→「その他のサービスで利用する」
3. ネームサーバー1・2にCloudflareのアドレスを入力して保存

### 3. Cloudflareで確認・Active待ち

1. 「I updated my nameservers」を押す
2. 数十分〜1時間待つ
3. ステータスが「Active」になったら完了

### 4. カスタムドメインをActivate

1. 「Custom domains」→ドメイン入力→「Continue」
2. 「Activate domain」を押す

## ハマったポイント

- ネームサーバー変更前にカスタムドメインを設定しようとしても進めない
- Activeを確認してから改めてCustom domainsの設定をする（2段階）

## 関連記事

- [XserverドメインのネームサーバーをCloudflareに変更する方法](/posts/xserver-cloudflare-nameserver)
- [Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
## より詳しく学びたい方へ

この記事の内容をさらに深掘りした実践ガイドをZennで公開しています。

[VPS・GitHub Actions・Cloudflare 実践構築ガイド](https://zenn.dev/errnotes/books/6ec5fb4840cea2)
