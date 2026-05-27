---
title: 'Cloudflareでリダイレクトルールを設定する方法'
date: '2026-05-16'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
---

## リダイレクトルールの設定手順

1. Cloudflareダッシュボード→対象ドメイン
2. 左メニュー「Rules」→「Redirect Rules」
3. 「Create rule」をクリック

## 旧URLから新URLにリダイレクト

**条件：**URIパス → 等しい → /old-page

**アクション：**静的リダイレクト → https://example.com/new-page → 301

## ステータスコードの使い分け

| コード | 意味 |
|--------|------|
| 301 | 恒久的なリダイレクト |
| 302 | 一時的なリダイレクト |

## ハマったポイント

- ルールの順番が重要
- 無料プランではリダイレクトルールは10個まで
- `Always Use HTTPS` がオンならHTTP→HTTPSのルールは不要

Cloudflareのリダイレクトルールで対応できない複雑なロジックが必要な場合は、[Cloudflare Workers入門：サーバーレス関数を作る方法](/posts/cloudflare-workers-intro)を使って柔軟に処理できる。

## 関連記事

- [Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)
- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
- [Cloudflare Analyticsを設定する方法](/posts/cloudflare-analytics-setup)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
