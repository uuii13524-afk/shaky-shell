---
title: 'AstroでSEOに必要なmetaタグを設定する方法'
date: '2026-05-18'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'AstroサイトにSEOに必要なtitle・description・OGPなどのmetaタグを設定する方法を解説。BaseHeadコンポーネントを使った管理方法も紹介します。'
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

SEOをさらに強化したい場合は、[Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)と組み合わせることで検索エンジンへのクロールを適切に制御できる。

## 関連記事

- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
- [AstroでMarkdownのスタイルを設定する方法](/posts/astro-markdown-styles)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
