---
title: 'Astroでrobots.txtとsitemapを自動生成する方法'
date: '2026-05-05'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'Astroサイトに@astrojs/sitemapプラグインでsitemap.xmlを自動生成し、robots.txtを手動で設置する方法を解説します。'
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

### 3. 動作確認

```
https://あなたのドメイン.com/sitemap-index.xml
```

## robots.txtの設置

`public/robots.txt` として保存する。

```
User-agent: *
Allow: /

Sitemap: https://あなたのドメイン.com/sitemap-index.xml
```

## ハマったポイント

- `site` を設定しないとsitemapが生成されない
- robots.txtは `public/` に置く
- Cloudflareがrobots.txtを上書きすることがあるが問題ない

sitemapの設置が完了したら、[AstroでSEOに必要なmetaタグを設定する方法](/posts/astro-seo-meta-tags)も一緒に対応しておくとSEO対策が一通り揃う。

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
