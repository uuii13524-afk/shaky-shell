---
title: 'AstroでMarkdownのスタイルを設定する方法'
date: '2026-05-15'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'AstroでMarkdownコンテンツにCSSスタイルを適用する方法を解説。グローバルCSSを使う方法とTailwindのtypographyプラグインを使う方法を紹介します。'
---

## やりたかったこと

Astroで記事ページを作ったが、Markdownの内容がスタイルなしの素のHTMLで表示されていた。見出しの`h2`も`p`タグも全部同じフォントサイズで、コードブロックも背景色も枠もなく読めたものじゃなかった。「CSSを書けばいいのはわかるが、どこに書けば記事の中身だけに効くのか」がわからなかった。

`<style>`タグをAstroコンポーネントに書けばいいのはわかったが、Markdownから生成されたHTMLには自動でクラスが付かない。何のセレクタを書けばいいのかわからなかった。

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3

## 試したこと・うまくいかなかったこと

最初、レイアウトファイル（`PostLayout.astro`）の`<style>`タグにセレクタを書いてみた。

```astro
<style>
  h2 { font-size: 1.5rem; }
  p { line-height: 1.8; }
</style>
```

スタイルが全く効かなかった。Astroの`<style>`タグはデフォルトでscoped CSSになっていて、コンポーネント固有のハッシュが自動で付く。Markdownから生成されたHTMLには同じハッシュが付かないので、scoped styleは記事コンテンツに効かない仕組みだった。

次に`<style is:global>`にして試した。

```astro
<style is:global>
  h2 { font-size: 1.5rem; }
</style>
```

今度は効いた。でもサイト全体の`h2`に効いてしまって、ナビゲーションのタイトルやサイドバーの見出しまで変わってしまった。記事の中身だけに絞れていなかった。

セレクタを`article h2`に変えて、レイアウトで`<slot />`を`<article>`タグで包む形にしてみた。これでようやく記事の中身だけにスタイルが効くようになった。コードブロックのスタイルも`pre`だけに書いたらインラインコードの`code`と干渉してしまい、`pre code { background: none; }`を別途書く必要があると気づくまでに時間がかかった。

## 解決策

### 方法：グローバルCSSファイルを使う

`src/styles/global.css`を作成してレイアウトファイルでimportする。

```css
/* src/styles/global.css */
article h2 { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 0.5rem; }
article h3 { font-size: 1.25rem; margin-top: 1.5rem; margin-bottom: 0.5rem; }
article p { line-height: 1.8; margin-bottom: 1rem; }
article ul { padding-left: 1.5rem; margin-bottom: 1rem; }
article li { line-height: 1.8; margin-bottom: 0.25rem; }
article code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-size: 0.875em; }
article pre { background: #1e1e1e; color: #d4d4d4; padding: 1.25rem; border-radius: 8px; overflow-x: auto; margin-bottom: 1.5rem; }
article pre code { background: none; padding: 0; font-size: 0.875em; }
article blockquote { border-left: 4px solid #e5e7eb; padding-left: 1rem; color: #6b7280; margin: 1.5rem 0; }
article a { color: #3b82f6; text-decoration: underline; }
```

レイアウトファイルでimportして、`<slot />`を`<article>`タグで囲む。

```astro
---
// src/layouts/PostLayout.astro
import '../styles/global.css';
const { title } = Astro.props;
---
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <title>{title}</title>
  </head>
  <body>
    <article>
      <slot />
    </article>
  </body>
</html>
```

`<slot />`がMarkdownの内容に展開される。`article`タグで囲むことで`article h2`などのセレクタが記事の中身だけに効く。

### レイアウトファイルをMarkdownに適用する

```markdown
---
title: '記事タイトル'
date: '2026-05-15'
layout: '../../layouts/PostLayout.astro'
---

## 見出し

本文。`インラインコード`もスタイルが効く。

```bash
echo "コードブロックにも背景色が付く"
```
```

frontmatterの`layout`パスはMarkdownファイルからの相対パスで書く。`src/pages/posts/`に記事がある場合、`src/layouts/`のレイアウトへのパスは`../../layouts/PostLayout.astro`になる。

## ハマったポイント

- Astroの`<style>`タグはデフォルトでscoped CSSになっている。Markdownから生成されたHTMLにはコンポーネントのハッシュが付かないので、scoped styleは効かない。`is:global`にするかCSSファイルをimportする方法が必要だった
- `<style is:global>`で書いたらサイト全体の要素に効いてしまった。セレクタを`article h2`のように`article`で限定することで記事内だけに絞れた。さらに`<slot />`を`<article>`タグで囲む構造にすることで完結した
- Markdownの`<slot />`には直接クラスを付けられない。「`.prose`クラスを付けたい」と思ったときは、レイアウトファイルで`<slot />`を`<div class="prose">`で囲む形にすると対応できる
- コードブロックのスタイルは`pre`だけでなく`pre code`にも書く必要があった。`article code { background: #f3f4f6; }`と書くとインラインコードに背景色が付くが、コードブロックの中の`code`にも同じ背景色が入ってしまう。`article pre code { background: none; }`を追加してリセットする対応が必要だった
- レイアウトファイルのパスをfrontmatterで指定するとき、相対パスで書かないと動かない。`/layouts/PostLayout.astro`と書いたら404になった。`../../layouts/PostLayout.astro`のように相対パスで書くのが正しかった

スタイルを整えたら、[AstroでSEOに必要なmetaタグを設定する方法](/posts/astro-seo-meta-tags)も設定しておくとSEO対策が一通り揃う。

## 関連記事

- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [AstroでSEOに必要なmetaタグを設定する方法](/posts/astro-seo-meta-tags)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
