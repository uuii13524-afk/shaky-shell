---
title: 'Astroでrobots.txtとsitemapを自動生成する方法'
date: '2026-05-20'
category: 'Astro'
---

## やりたかったこと

AstroサイトにSEOに必要なrobots.txtとsitemap.xmlを設置したかった。
記事が増えるたびに手動でsitemapを更新するのは現実的ではないので自動生成にした。

## 環境

- Astro 5
- Cloudflare Pages

## sitemapの自動生成

### 1. sitemapプラグインをインストール

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

`site` にサイトのURLを必ず設定する。これがないとsitemapが正しく生成されない。

### 3. 動作確認

ビルドしてから以下のURLにアクセスして確認する。

```
https://あなたのドメイン.com/sitemap-index.xml
```

以下のようなXMLが表示されれば成功。

```xml
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://あなたのドメイン.com/sitemap-0.xml</loc>
  </sitemap>
</sitemapindex>
```

## robots.txtの設置

sitemapと違い、robots.txtは手動で作成する。

### 1. publicフォルダにrobots.txtを作成

`public/robots.txt` として以下の内容で保存する。

```
User-agent: *
Allow: /

Sitemap: https://あなたのドメイン.com/sitemap-index.xml
```

### 2. 動作確認

以下のURLにアクセスして内容が表示されれば成功。

```
https://あなたのドメイン.com/robots.txt
```

## Google Search Consoleにサイトマップを送信

1. Google Search Consoleにログイン
2. 左メニュー「サイトマップ」をクリック
3. 入力欄に `sitemap-index.xml` と入力
4. 「送信」を押す

## ハマったポイント

- `astro.config.mjs` に `site` を設定しないとsitemapが生成されない
- robots.txtは `src/` ではなく `public/` に置く
- `public/` に置いたファイルはビルド後のサイトのルートに配置される
- Cloudflareがrobots.txtを上書きすることがある。その場合でも `sitemap-index.xml` のURLは末尾に追加される

## 補足

Cloudflare管理のrobots.txtが追加される場合があるが、自分で設定した内容も末尾に追加されるので問題ない。
