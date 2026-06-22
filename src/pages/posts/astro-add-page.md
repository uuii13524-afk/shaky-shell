---
title: 'Astroで新しいページを追加する基本的な方法'
date: '2026-05-08'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'AstroでHTMLやMarkdownを使って新しいページを追加する方法を解説。ファイルの配置場所・ルーティングの仕組み・リンクの貼り方もわかりやすく紹介します。'
---

## やりたかったこと

Astroでブログサイトを作り始めて、トップページ（`index.astro`）は動いたので次に「Aboutページ」と記事ページを追加しようとした。試しに`src/about.html`を作ってローカルで`http://localhost:4321/about`にアクセスしたら、404が返ってきた。「どこにファイルを置けばページになるのか」がまったくわからなかった。

「AstroはReactみたいにルーターの設定が必要なのかも」と思ってドキュメントを探し始めたが、ルーティングの設定ページを見つけてしまって余計に混乱した。実際にはルーターの設定は要らなかった。

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3

## 試したこと・うまくいかなかったこと

最初に`src/about.html`を作った。`http://localhost:4321/about`にアクセスしたが404のまま。`src/`直下に置いても`src/pages/`以外はAstroがページとして認識しないとわかったのはしばらく後だった。

次に`public/about.html`に置いてみた。今度はアクセスできたが、Astroのレイアウトが一切適用されない生のHTMLがそのまま表示されただけだった。`public/`フォルダはAstroが処理しない静的ファイルの置き場で、ページとして扱うためのルーティングには使えない。

「Markdownファイルでもページを作れる」とドキュメントに書いてあったので`src/pages/posts/first-post.md`を作ってアクセスしてみた。Markdownの内容はHTMLに変換されていたが、スタイルが全くない状態で表示された。frontmatterに`layout`を指定していなかったのが原因だった。

## 解決策

Astroのページファイルは全部`src/pages/`に置く。それ以外の場所に置いてもページにならない。

```
src/
  pages/
    index.astro        → https://ドメイン/
    about.astro        → https://ドメイン/about
    posts/
      first-post.md    → https://ドメイン/posts/first-post
      second-post.md   → https://ドメイン/posts/second-post
```

ファイル名がそのままURLのパスになる。拡張子（`.astro`や`.md`）はURLに含まれない。

### .astroファイルでページを作る

```astro
---
// src/pages/about.astro
---
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <title>About</title>
  </head>
  <body>
    <h1>About</h1>
    <p>このサイトについて</p>
  </body>
</html>
```

既存のレイアウトを使う場合はimportして`<Layout>`コンポーネントで囲む。

```astro
---
import Layout from '../layouts/BaseLayout.astro';
---
<Layout title="About">
  <h1>About</h1>
  <p>このサイトについて</p>
</Layout>
```

### Markdownファイルでページを作る

記事はMarkdownで書くと楽だった。frontmatterに`layout`を指定するとレイアウトが適用される。

```markdown
---
title: '初めての記事'
date: '2026-05-08'
layout: '../../layouts/PostLayout.astro'
---

## 見出し

本文をここに書く。
```

`layout`のパスはMarkdownファイルからの**相対パス**で書く。`src/pages/posts/`にMarkdownがある場合、`src/layouts/`のレイアウトは`../../layouts/PostLayout.astro`になる。絶対パスで書くと動かなかった。

### ページ間のリンクを貼る

```astro
<a href="/about">Aboutページ</a>
<a href="/posts/first-post">最初の記事</a>
```

Astroではルートからの絶対パスで書くのが確実だった。相対パスで書くとネストが深いページでリンクが壊れることがあった。

## ハマったポイント

- `src/pages/`以外に置いてもページにならない。`src/about.html`も`public/about.html`も「ページ」として機能しなかった。Astroはファイルベースルーティングで、`src/pages/`の中だけが対象になっている
- Markdownのfrontmatterに`layout`を指定しないとスタイルが全く当たらないプレーンなHTMLで表示される。「Markdownが反映されていない」と思ったが`layout`の指定が抜けていただけだった
- レイアウトファイルのパスはMarkdownファイルからの相対パスで書く。`src/pages/posts/article.md`から`src/layouts/PostLayout.astro`を指定するには`../../layouts/PostLayout.astro`になる。最初に`./layouts/PostLayout.astro`と書いて404になって1時間悩んだ
- ファイル名に`.md`の拡張子はURLに含まれない。`first-post.md`を置いたら`/posts/first-post`がURLになる。`.md`のまま`/posts/first-post.md`にアクセスしようとして404になって混乱した
- 「Astroのルーター設定が必要」と思い込んでドキュメントを読み漁ったが、そもそもファイルを置く場所が間違っていた。ファイルの置き場所を疑うのが先だった

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
