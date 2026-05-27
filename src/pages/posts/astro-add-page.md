---
title: 'Astroで新しいページを追加する基本的な方法'
date: '2026-05-08'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

Astroで新しいページを追加したかった。

## 基本的なページの追加方法

```
src/
  pages/
    index.astro    → https://ドメイン/
    about.astro    → https://ドメイン/about
    posts/
      first.md     → https://ドメイン/posts/first
```

## Markdownファイルでページを作成

```markdown
---
title: '記事タイトル'
date: '2026-05-08'
---

## 見出し

本文をここに書く。
```

## ハマったポイント

- `src/pages/` 以外に置いてもページにならない
- ファイル名がそのままURLになる

ページが増えてきたら、[AstroでSEOに必要なmetaタグを設定する方法](/posts/astro-seo-meta-tags)も合わせて対応しておくとよい。

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
