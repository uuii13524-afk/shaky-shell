---
title: 'AstroでSEOに必要なmetaタグを設定する方法'
date: '2026-05-18'
category: 'Astro'
---

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

## OGPタグ

```astro
<meta property="og:title" content="ページタイトル" />
<meta property="og:description" content="説明文" />
<meta property="og:url" content="https://example.com/page" />
<meta property="og:type" content="article" />
```

## レイアウトコンポーネントで共通化する

```astro
---
const { title, description } = Astro.props;
---
<html>
  <head>
    <title>{title}</title>
    <meta name="description" content={description} />
  </head>
  <body><slot /></body>
</html>
```

## ハマったポイント

- `description` は120〜160文字程度が推奨
- `canonical` タグを設定しないと重複コンテンツとみなされることがある

## 関連記事

- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
- [AstroでMarkdownのスタイルを設定する方法](/posts/astro-markdown-styles)
