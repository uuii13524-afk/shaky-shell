---
title: 'AstroでSEOに必要なmetaタグを設定する方法'
date: '2026-05-20'
category: 'Astro'
---

## やりたかったこと

AstroサイトのSEOを改善するためにmetaタグを適切に設定したかった。

## 環境

- Astro 5

## 基本的なmetaタグ

```astro
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ページタイトル - サイト名</title>
  <meta name="description" content="ページの説明文（120文字程度）" />
  <link rel="canonical" href="https://example.com/page" />
</head>
```

## OGPタグ（SNSシェア用）

```astro
<head>
  <!-- OGP -->
  <meta property="og:title" content="ページタイトル" />
  <meta property="og:description" content="ページの説明文" />
  <meta property="og:url" content="https://example.com/page" />
  <meta property="og:type" content="article" />
  <meta property="og:image" content="https://example.com/image.jpg" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="ページタイトル" />
  <meta name="twitter:description" content="ページの説明文" />
</head>
```

## レイアウトコンポーネントで共通化する

```astro
---
// src/layouts/BaseLayout.astro
const { title, description, url } = Astro.props;
const siteUrl = "https://example.com";
---
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <meta name="description" content={description} />
    <link rel="canonical" href={`${siteUrl}${url}`} />
    <meta property="og:title" content={title} />
    <meta property="og:description" content={description} />
  </head>
  <body>
    <slot />
  </body>
</html>
```

各ページで使う。

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---
<BaseLayout
  title="記事タイトル - ErrNotes"
  description="記事の説明文"
  url="/posts/my-article"
>
  <h1>記事タイトル</h1>
</BaseLayout>
```

## ハマったポイント

- `description` は120〜160文字程度が推奨
- `canonical` タグを設定しないと重複コンテンツとみなされることがある
- `og:image` は1200×630px推奨

## 関連記事

- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
