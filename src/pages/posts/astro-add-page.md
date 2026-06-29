---
title: 'Astroで新しいページを追加する基本的な方法'
date: '2026-05-08'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Astro', 'ページ追加', 'ルーティング', 'Markdown', 'レイアウト']
description: 'AstroでHTMLやMarkdownを使って新しいページを追加する方法を解説。ファイルの配置場所・ルーティングの仕組み・リンクの貼り方もわかりやすく紹介します。'
---

## ひとことで言うと

```
新しいページは src/pages/ に置くだけ。
Markdownなら frontmatter に layout を書く。
```

```markdown
---
title: 'ページタイトル'
layout: '../../layouts/PostLayout.astro'
---
```

`src/pages/` 以外に置いてもページにならない。`layout` を書かないとスタイルが当たらない。この2点だけ抑えれば詰まらない。

---

## やりたかったこと

Astroでブログサイトを作り始めて、トップページ（`index.astro`）は動いたので次に「Aboutページ」と記事ページを追加しようとした。試しに `src/about.html` を作ってローカルで `http://localhost:4321/about` にアクセスしたら、案の定404が返ってきた。

```
Page not found
Couldn't find the page you're looking for!
```

「どこにファイルを置けばページになるのか」がまったくわからなかった。「AstroはReactみたいにルーターの設定が必要なのかも」と思ってドキュメントを探し始めたが、routing のページを見つけてしまって余計に混乱した。実際にはルーターの設定は要らなかった。最初の1時間は完全に方向違いのことを調べていた。

---

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3

---

## 試したこと・うまくいかなかったこと

**`src/about.html` を作った → 404のまま**

最初に `src/about.html` を作った。`http://localhost:4321/about` にアクセスしたが `Page not found` のまま。`src/` 直下に置いても `src/pages/` 以外はAstroがページとして認識しないとわかったのはしばらく後だった。ターミナルに何かエラーが出るわけでもなく、ただ404が返るだけなので原因がわからなかった。

**`public/about.html` に置いてみた → スタイルなしで表示**

次に `public/about.html` に置いてみた。今度はアクセスできたが、Astroのレイアウトが一切適用されない生のHTMLがそのまま表示されただけだった。

```
# こんな感じで何も装飾されていない
About
このサイトについて
```

`public/` フォルダはAstroが処理しない静的ファイルの置き場で、ページとして扱うためのルーティングには使えない。「静的に置けるならHTMLそのまま置ける」と思っていたが、レイアウトとの統合ができない場所だった。

**Markdownで `src/pages/posts/first-post.md` を作った → スタイルなし**

「Markdownファイルでもページを作れる」とドキュメントに書いてあったので `src/pages/posts/first-post.md` を作ってアクセスしてみた。Markdownの内容はHTMLに変換されていたが、スタイルが全くない状態で表示された。

```
# 全部同じ大きさで表示される
ページタイトル
見出し
本文テキスト
```

frontmatterに `layout` を指定していなかったのが原因だった。`layout` なしのMarkdownはAstroがコンテンツをHTMLに変換するだけで、レイアウトコンポーネントとは繋がらない。これに気づくまで「Markdownのレンダリングが壊れている」と勘違いして30分調べ続けた。

---

## 解決策

Astroのページファイルは全部 `src/pages/` に置く。それ以外の場所に置いてもページにならない。

```
src/
  pages/
    index.astro        → https://ドメイン/
    about.astro        → https://ドメイン/about
    posts/
      first-post.md    → https://ドメイン/posts/first-post
      second-post.md   → https://ドメイン/posts/second-post
```

ファイル名がそのままURLのパスになる。拡張子（`.astro` や `.md`）はURLに含まれない。

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

既存のレイアウトを使う場合はimportして `<Layout>` コンポーネントで囲む。

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

記事はMarkdownで書くと楽だった。frontmatterに `layout` を指定するとレイアウトが適用される。

```markdown
---
title: '初めての記事'
date: '2026-05-08'
layout: '../../layouts/PostLayout.astro'
---

## 見出し

本文をここに書く。
```

`layout` のパスはMarkdownファイルからの**相対パス**で書く。`src/pages/posts/` にMarkdownがある場合、`src/layouts/` のレイアウトは `../../layouts/PostLayout.astro` になる。絶対パスで書くと動かなかった。

### ページ間のリンクを貼る

```astro
<a href="/about">Aboutページ</a>
<a href="/posts/first-post">最初の記事</a>
```

Astroではルートからの絶対パスで書くのが確実だった。相対パスで書くとネストが深いページでリンクが壊れることがあった。

### ページが増えてきたときのディレクトリ整理

記事が増えてきたら `src/pages/` の直下が散らかる。カテゴリごとにサブディレクトリを切るとURLも整理できた。

```
src/
  pages/
    posts/
      docker-exec.md      → /posts/docker-exec
    en/
      docker-exec.md      → /en/docker-exec
```

日本語記事と英語記事を分けて運用する場合はこのように `/posts/` と `/en/` で分けた。

---

## ハマったポイント

- `src/pages/` 以外に置いてもページにならない。`src/about.html` も `public/about.html` も「ページ」として機能しなかった。Astroはファイルベースルーティングで、`src/pages/` の中だけが対象になっている。ターミナルにエラーが出ないので気づきにくい
- Markdownのfrontmatterに `layout` を指定しないとスタイルが全く当たらないプレーンなHTMLで表示される。「Markdownが反映されていない」と思ったが `layout` の指定が抜けていただけだった。devサーバーを再起動しても直らなくて焦った
- レイアウトファイルのパスはMarkdownファイルからの相対パスで書く。`src/pages/posts/article.md` から `src/layouts/PostLayout.astro` を指定するには `../../layouts/PostLayout.astro` になる。最初に `./layouts/PostLayout.astro` と書いて404になって1時間悩んだ
- ファイル名に `.md` の拡張子はURLに含まれない。`first-post.md` を置いたら `/posts/first-post` がURLになる。`.md` のまま `/posts/first-post.md` にアクセスしようとして404になって混乱した
- 「Astroのルーター設定が必要」と思い込んでドキュメントを読み漁ったが、そもそもファイルを置く場所が間違っていた。ファイルの置き場所を疑うのが先だった。ルーター設定のページを読み込んでいた時間が一番の無駄だった

---

## よくある質問

**Q: `src/pages/` に `.html` ファイルを置いてもページになりますか？**
なる。`src/pages/about.html` を置くと `/about` にアクセスできる。ただしAstroのレイアウトやコンポーネントとの統合はできないので、Astroで管理するページには `.astro` か `.md` を使った方がいい。

**Q: `src/pages/` の中にサブディレクトリを作れますか？**
作れる。`src/pages/posts/first.md` を置くと `/posts/first` がURLになる。階層は何段でも作れる。

**Q: Markdownのfrontmatterに書く `layout` のパスが正しいか確認する方法は？**
ブラウザのコンソールを開いてエラーが出ているか確認するか、devサーバーのターミナルを見る。パスが間違っていると `Cannot find module` のようなエラーが出る。`../../layouts/PostLayout.astro` と書いているつもりで `../layouts/PostLayout.astro` になっているケースが多かった。

**Q: ページのURLに大文字を含めることはできますか？**
Astroはファイル名をそのままURLに使うが、URLに大文字は使わない方がいい。`About.astro` を置いても大文字のURLになってしまうので `about.astro` とスラッグ形式（英小文字・ハイフン区切り）でファイル名をつけるのが無難だった。

**Q: Markdownファイルとfrontmatterのlayoutを全記事で共通にしたい。**
Markdownファイルごとに `layout` を書く必要がある。共通化はできない。Astroの `.astro` でラッパーページを作ってそこからMarkdownを読み込む方法もあるが、シンプルに各ファイルに `layout` を書く方が管理しやすかった。

---

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
