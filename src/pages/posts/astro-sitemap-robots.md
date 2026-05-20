---
title: 'Astroでrobots.txtとsitemapを自動生成する方法'
date: '2026-05-20'
category: 'Astro'
---

## やりたかったこと

AstroサイトにSEOに必要なrobots.txtとsitemap.xmlを設置したかった。

## 環境

- Astro 5
- Cloudflare Pages

## sitemapの自動生成

### 1. プラグインをインストール

```
npm install @astrojs/sitemap
```

### 2. astro.config.mjsを編集

```js
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://あなたのドメイン.com',
  integrations: [sitemap()],
});
```

`site` にサイトのURLを必ず設定する。

### 3. 動作確認

```
https://あなたのドメイン.com/sitemap-index.xml
```

## robots.txtの設置

`public/robots.txt` として以下の内容で保存する。

```
User-agent: *
Allow: /

Sitemap: https://あなたのドメイン.com/sitemap-index.xml
```

## Google Search Consoleにサイトマップを送信

1. Google Search Console→「サイトマップ」
2. `sitemap-index.xml` と入力して「送信」

## ハマったポイント

- `site` を設定しないとsitemapが生成されない
- robots.txtは `public/` に置く（`src/` ではない）
- Cloudflareがrobots.txtを上書きすることがあるが問題ない

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
