---
title: 'Cloudflare AnalyticsをAstroサイトに設定する方法'
date: '2026-05-19'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
---

## Cloudflare Analyticsとは

- Cookieを使わない
- プライバシーに配慮した計測
- Cloudflare Pagesを使っている場合は自動で有効になることがある

## 設定手順

1. Cloudflareダッシュボード→「Analytics & Logs」→「Web Analytics」
2. 「Add a site」→URLを入力
3. 発行されたスクリプトタグをコピー

Astroのレイアウトファイルの `</body>` 直前に貼り付ける。

```astro
<script defer src='https://static.cloudflareinsights.com/beacon.min.js'
  data-cf-beacon='{"token": "トークン"}'></script>
```

## 確認できるデータ

- ページビュー数・ユニーク訪問者数
- 上位ページ・参照元
- 国別アクセス

## ハマったポイント

- データの反映に数時間かかることがある
- Cookieなしのためアドブロッカーに影響されにくい

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
