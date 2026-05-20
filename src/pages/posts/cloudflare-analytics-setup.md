---
title: 'Cloudflare AnalyticsをAstroサイトに設定する方法'
date: '2026-05-20'
category: 'Cloudflare'
---

## やりたかったこと

AstroサイトのアクセスデータをCloudflare Analyticsで確認したかった。
Google Analyticsと違いCookieなしで計測できる。

## 環境

- Cloudflare Pages
- Astro

## Cloudflare Analyticsとは

- Cookieを使わない
- プライバシーに配慮した計測
- Cloudflareのダッシュボードで確認できる
- Cloudflare Pagesを使っている場合は自動で有効

## 設定手順

### Cloudflare Pages使用時（自動）

Cloudflare Pagesにデプロイしている場合はWeb Analyticsが自動で有効になっている場合がある。

1. Cloudflareダッシュボード→「Analytics & Logs」→「Web Analytics」
2. サイトが表示されていれば自動計測中

### 手動でBeaconを設置する場合

1. Cloudflareダッシュボード→「Analytics & Logs」→「Web Analytics」
2. 「Add a site」をクリック
3. サイトのURLを入力
4. 発行されたスクリプトタグをコピー

Astroのレイアウトファイルの `</body>` の直前に貼り付ける。

```astro
---
// src/layouts/BaseLayout.astro
---
<html>
  <head>...</head>
  <body>
    <slot />
    <!-- Cloudflare Web Analytics -->
    <script defer src='https://static.cloudflareinsights.com/beacon.min.js'
      data-cf-beacon='{"token": "トークン"}'></script>
  </body>
</html>
```

## 確認できるデータ

- ページビュー数
- ユニーク訪問者数
- 上位ページ
- 参照元
- 国別アクセス
- デバイス・ブラウザ

## ハマったポイント

- Cloudflare Pagesを使っている場合はビルトインのAnalyticsが自動で計測される
- データの反映に数時間かかることがある
- Cookieなしのためアドブロッカーに影響されにくい

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
