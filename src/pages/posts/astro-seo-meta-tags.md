---
title: 'AstroでSEOに必要なmetaタグを設定する方法'
date: '2026-05-18'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Astro', 'SEO', 'metaタグ', 'OGP', 'description']
description: 'AstroサイトにSEOに必要なtitle・description・OGPなどのmetaタグを設定する方法を解説。BaseHeadコンポーネントを使った管理方法も紹介します。'
---

## ひとことで言うと

```astro
---
// src/layouts/PostLayout.astro
const { title, description } = Astro.props;
const canonicalURL = new URL(Astro.url.pathname, Astro.site);
---
<head>
  <title>{title} | サイト名</title>
  <meta name="description" content={description} />
  <link rel="canonical" href={canonicalURL} />
  <meta property="og:title" content={title} />
  <meta property="og:description" content={description} />
  <meta property="og:image" content={new URL('/og-image.png', Astro.site)} />
</head>
```

Astro 5では `Astro.props.frontmatter.title` ではなく `Astro.props.title` と書く。`og:image` は絶対URLでないとSNSカードに画像が出ない。

---

## やりたかったこと

AstroブログをCloudflare Pagesで公開した後、Google Search Consoleにサイトを登録したら「descriptionが設定されていないページが多い」という警告が出た。

```
問題が検出されました
メタデスクリプションが欠けています (xx ページ)
```

記事ごとにtitleとdescriptionを設定する必要があるのはわかったが、Astroの各Markdownファイルに毎回metaタグをベタ書きするのは無理だった。「レイアウトコンポーネントに書けば共通化できるはず」と思って試し始めたが、OGPタグの種類が多くてどれを設定すればいいかもわからなかった。

最初に適当にtitleとdescriptionだけ入れたら、LINEでURLを共有したときにサムネイルが出なくて困った。Twitterでも同様で、URLを貼っても記事タイトルだけが小さく出るカードになった。「OGPタグが足りない」とわかってから設定し直した。

---

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3

---

## 試したこと・うまくいかなかったこと

**全記事で同じmeta descriptionを使ってしまった**

最初、レイアウトファイルにハードコードで `content="AstroとCloudflareで作ったブログです"` と書いたら全ページで同じdescriptionが出てしまった。Search Consoleで「重複したメタ説明」の警告が出た。

```
警告: 重複するメタ説明 (3 ページ)
```

各ページの `Astro.props` から `description` を受け取る形に変えようとしたが、最初は `const description = Astro.props.description` と書いて `undefined` になった。Astro 4まではMarkdownのfrontmatterを `Astro.props.frontmatter.description` で受け取っていたが、Astro 5では `Astro.props.description` に変わっていた。バージョンによって書き方が違うことに気づくまで30分かかった。

**OGPタグを設定してもTwitterカードに画像が表示されなかった**

`og:image` に `/og-image.png` と相対パスで書いていたのが原因だった。Twitterはページのベースではなく外部から絶対URLでリソースをフェッチするので、`https://` から始まる絶対URLで書く必要があった。

[Twitter Card Validator](https://cards-dev.twitter.com/validator) でURLを検証したら「画像が取得できない」というエラーが出た。それで絶対URLの問題だとわかった。

**`canonical` タグを設定していなかったら重複コンテンツ扱いになった**

`?utm_source=twitter` のようなクエリパラメータ付きのURLと通常URLが別ページとして認識されてしまった。`canonical` タグを設定してから数日後に Search Console の重複コンテンツの警告が消えた。

**`Astro.site` が `undefined` でビルドエラー**

```
Error: Cannot read properties of undefined (reading 'origin')
```

`new URL('/og-image.png', Astro.site)` を書いたところ、`Astro.site` が `undefined` でエラーになった。`astro.config.mjs` に `site:` を設定していなかったのが原因だった。

---

## 解決策

### レイアウトにmetaタグをまとめる

`src/layouts/PostLayout.astro` でfrontmatterからtitleとdescriptionを受け取って動的に設定する。

```astro
---
// src/layouts/PostLayout.astro
const { title, description } = Astro.props;
const canonicalURL = new URL(Astro.url.pathname, Astro.site);
---
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title} | errsolved.com</title>
    <meta name="description" content={description} />
    <link rel="canonical" href={canonicalURL} />

    <!-- OGP -->
    <meta property="og:title" content={title} />
    <meta property="og:description" content={description} />
    <meta property="og:url" content={canonicalURL} />
    <meta property="og:type" content="article" />
    <meta property="og:image" content={new URL('/og-image.png', Astro.site)} />

    <!-- Twitterカード -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content={title} />
    <meta name="twitter:description" content={description} />
  </head>
  <body>
    <slot />
  </body>
</html>
```

`Astro.site` を使うために `astro.config.mjs` に `site` プロパティが必要。

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://yourdomain.com',
});
```

### Markdownのfrontmatterで各記事に設定する

```markdown
---
title: '記事タイトル'
description: 'この記事の概要（120〜160文字程度が推奨）'
date: '2026-05-18'
layout: '../../layouts/PostLayout.astro'
---
```

Astro 5ではfrontmatterの値が `Astro.props` に直接入ってくる。

```astro
---
// PostLayout.astro のfrontmatter部分
const { title, description } = Astro.props;
---
```

Astro 4以前では `Astro.props.frontmatter.title` と書く必要があった。バージョンを確認してから書き方を合わせる。

### descriptionの長さの目安

- 短すぎる（60文字以下）：Googleが自動で別のテキストに置き換えることがある
- 適正（120〜160文字）：検索結果のスニペットとして表示されやすい
- 長すぎる（200文字超）：検索結果では途中で切れる

日本語は1文字が英語より情報量が多いため、120〜160文字でも十分な説明になる。

### OGP画像を用意する

`public/og-image.png` として 1200×630px の画像を用意するのが推奨サイズ。作り方は：

- CanvaやFigmaで 1200×630px のデザインを作ってPNGでエクスポートする
- 記事ごとに動的に生成する方法もあるが最初は固定画像で十分だった

画像が重いと読み込みが遅いので 200KB 以下に圧縮しておくとよかった。

---

## ハマったポイント

- 全ページで同じmeta descriptionを使ってしまいSearch Consoleの「重複したメタ説明」警告が出た。レイアウトにハードコードで書かず、frontmatterから受け取る形にするのが正しかった。最初に全記事の description を書くのが面倒で後回しにしていたのも反省点だった
- `canonical` タグを設定していないページで、クエリパラメータ付きURLが別ページとして認識されてしまった。`new URL(Astro.url.pathname, Astro.site)` で生成した絶対URLを使うのが確実だった。`Astro.site` が設定されていないと `undefined` になるので `astro.config.mjs` への `site` 設定が前提になる
- `og:image` を相対パスで書いたらTwitterカードに画像が表示されなかった。SNSのクローラーは相対パスを解釈しないので必ず `https://` から始まる絶対URLで書く必要があった。`new URL('/og-image.png', Astro.site)` のようにAstro.siteと組み合わせると動的に生成できた
- Astro 4と5でfrontmatterの受け取り方が違う。4では `Astro.props.frontmatter.title`、5では `Astro.props.title`。バージョンアップ後に `title` が `undefined` になって「なぜ急に動かなくなったのか」と30分悩んだ
- `description` をfrontmatterに書いていない記事があると `content` が空文字になる。全記事にdescriptionを書く運用にするか、`{description || 'デフォルトの説明'}` でフォールバックを用意しておくかを最初に決めておくとよかった

---

## よくある質問

**Q: descriptionを設定しないとどうなりますか？**
Googleが自動的にページ本文から抜粋してスニペットを生成する。生成されたスニペットが適切でない場合が多く、クリック率が下がることがある。全記事にdescriptionを書く方がいい。

**Q: OGP画像は必須ですか？**
必須ではないが、SNSでURLを共有したときにサムネイルが表示される方がクリック率は上がる。最低でも固定の1枚を `/public/og-image.png` に置くだけで効果があった。

**Q: Twitter Cardのタグと OGP タグは両方必要ですか？**
Twitterは `og:` タグを読んでくれるので、OGPタグだけ設定すればTwitterカードも動く。ただし `twitter:card` の指定（`summary` か `summary_large_image`）だけはTwitter独自タグで指定する必要があった。指定しないと小さい画像サイズのカードになった。

**Q: canonicalタグを入れると検索順位が上がりますか？**
直接上がるわけではないが、同じコンテンツが複数URLで重複して評価されるリスクを防ぐ効果がある。特にSNSのクエリパラメータ付きURLや `www` あり/なしの重複が多いサイトでは重要だった。

**Q: 記事ごとにOGP画像を変えるには？**
frontmatterに `ogImage` フィールドを追加して `<meta property="og:image" content={ogImage || new URL('/og-image.png', Astro.site)} />` のように書くとフォールバック付きで記事ごとに設定できた。

---

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
