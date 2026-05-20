---
title: 'Astroで新しいページを追加する基本的な方法'
date: '2026-05-20'
category: 'Astro'
---

## やりたかったこと

Astroで新しいページを追加したかった。
Astroはファイルベースのルーティングなので、ファイルを置くだけでページが増える。

## 環境

- Astro 5

## 基本的なページの追加方法

`src/pages/about.astro` を作成すると `https://ドメイン/about` でアクセスできる。

```
src/
  pages/
    index.astro    → https://ドメイン/
    about.astro    → https://ドメイン/about
    contact.astro  → https://ドメイン/contact
```

## .astroファイルの基本構成

```astro
---
const title = "About";
---
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <title>{title}</title>
  </head>
  <body>
    <h1>{title}</h1>
    <p>ページの内容</p>
  </body>
</html>
```

## Markdownファイルでページを作成

`.md` ファイルも自動的にページになる。

```markdown
---
title: '記事タイトル'
date: '2026-05-20'
---

## 見出し

本文をここに書く。
```

## ハマったポイント

- `src/pages/` 以外に置いてもページにならない
- ファイル名がそのままURLになる（スペースは使えない）
- `index.astro` はそのディレクトリのトップページになる

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
