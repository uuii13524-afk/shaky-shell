---
title: 'Astroでrobots.txtとsitemapを自動生成する方法'
date: '2026-05-05'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'Astroサイトに@astrojs/sitemapプラグインでsitemap.xmlを自動生成し、robots.txtを手動で設置する方法を解説します。'
---

## やりたかったこと

AstroサイトをCloudflare Pagesで公開してGoogle Search Consoleに登録したら、サイトマップを送信するよう促された。`sitemap.xml`を手動で作るものだと思っていたが、Astroにはプラグインで自動生成できる仕組みがあるとわかって設定した。robots.txtはどこに置けばいいのかも最初わからなかった。

## 環境

- Astro 5.2.3
- Cloudflare Pages（Freeプラン）
- Node.js 20.11.0
- npm 10.2.4

## 試したこと・うまくいかなかったこと

最初、`public/sitemap.xml`にXML形式のファイルを手動で作った。記事を追加するたびに手動でURLを追記しないといけないので、10記事くらいで面倒になって別の方法を探した。

`@astrojs/sitemap`というプラグインがあると知ってインストールしたが、`astro.config.mjs`に`site`プロパティを書かずに追加したらビルドエラーになった。

```
[@astrojs/sitemap] No `site` option is set in your Astro config. A site URL is required to generate a sitemap.
```

`site`を書けばいいとわかったが、最初はローカルの`http://localhost:4321`を書いてしまった。本番環境のURLを書かないとサイトマップのURLがlocalhostになってしまい、Search Consoleに送信しても意味がない。

## 解決策

### 1. sitemapプラグインをインストール

```bash
npm install @astrojs/sitemap
```

### 2. astro.config.mjsに追記する

```js
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://yourdomain.com',  // 本番のURLを書く
  integrations: [sitemap()],
});
```

`site`には本番環境のURL（`https://`付き）を書く。末尾のスラッシュはあってもなくてもOK。

### 3. ビルドして動作確認

```bash
npm run build
ls dist/sitemap*.xml
```

`sitemap-index.xml`と`sitemap-0.xml`の2ファイルが生成されていれば成功。デプロイ後に`https://yourdomain.com/sitemap-index.xml`にアクセスして内容を確認する。

### 4. robots.txtをpublicフォルダに設置

`public/robots.txt`として以下の内容で保存する。

```
User-agent: *
Allow: /

Sitemap: https://yourdomain.com/sitemap-index.xml
```

`public/`に置くことでビルド後に`dist/robots.txt`にそのままコピーされる。

### 5. 両方をpushしてデプロイ

```bash
git add astro.config.mjs public/robots.txt
git commit -m "add sitemap and robots.txt"
git push
```

デプロイ後、以下のURLで確認する。

- `https://yourdomain.com/sitemap-index.xml` → 全ページのURLが含まれているか確認
- `https://yourdomain.com/robots.txt` → Sitemapの行にURLが入っているか確認

### 6. Google Search Consoleでサイトマップを送信

左メニュー「サイトマップ」→ `sitemap-index.xml` と入力して「送信」。「ステータス：成功」と表示されれば完了。

Search Consoleへの登録がまだの場合は[Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)から先に設定する。

## ハマったポイント

- `site`を設定しないとプラグインがエラーを出して`npm run build`が失敗する。`site`がない状態ではサイトマップを生成できないので必須のプロパティだった
- `site`にlocalhostを書いてしまうとサイトマップのURLが全部`http://localhost:4321/...`になる。本番のドメインを書き忘れやすいので注意
- サイトマップのファイル名が`sitemap.xml`ではなく`sitemap-index.xml`だった。Search Consoleで`sitemap.xml`を入力したら「読み取れませんでした」というエラーが出て、`sitemap-index.xml`と書き直したら通った
- Cloudflareがrobots.txtを上書きする、という情報を見かけて心配したが、実際には`public/robots.txt`に置いたものが優先されて問題なかった
- 記事ページ（`src/pages/posts/*.md`）も自動でサイトマップに含まれた。`astro.config.mjs`でカスタマイズしなくても全ページが対象になるのは便利だった

SEOのmeta情報も一緒に設定したい場合は[AstroでSEOに必要なmetaタグを設定する方法](/posts/astro-seo-meta-tags)も合わせて対応しておくとSEO対策が一通り揃う。

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
