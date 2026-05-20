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

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
