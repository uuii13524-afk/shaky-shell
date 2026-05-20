---
title: 'Cloudflareでリダイレクトルールを設定する方法'
date: '2026-05-16'
category: 'Cloudflare'
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

## 関連記事

- [Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)
- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
- [Cloudflare Analyticsを設定する方法](/posts/cloudflare-analytics-setup)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
