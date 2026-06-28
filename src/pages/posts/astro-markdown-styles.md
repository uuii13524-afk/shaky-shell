---
title: 'AstroでMarkdownのスタイルを設定する方法'
date: '2026-05-15'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Astro', 'Markdown', 'CSS', 'スタイル', 'レイアウト']
description: 'AstroでMarkdownコンテンツにCSSスタイルを適用する方法を解説。グローバルCSSを使う方法とTailwindのtypographyプラグインを使う方法を紹介します。'
---

## ひとことで言うと

```css
/* src/styles/global.css */
article h2 { font-size: 1.5rem; margin-top: 2rem; }
article p  { line-height: 1.8; margin-bottom: 1rem; }
article pre { background: #1e1e1e; color: #d4d4d4; padding: 1.25rem; border-radius: 8px; }
article pre code { background: none; padding: 0; }
```

```astro
---
// src/layouts/PostLayout.astro
import '../styles/global.css';
---
<html>
  <body>
    <article>
      <slot />
    </article>
  </body>
</html>
```

Markdownから生成されたHTMLにはクラスが付かない。`<slot />` を `<article>` で包んで `article h2` セレクタで絞るのが一番シンプルな解決策だった。

---

## やりたかったこと

Astroで記事ページを作ったが、Markdownの内容がスタイルなしの素のHTMLで表示されていた。見出しの `h2` も `p` タグも全部同じフォントサイズで、コードブロックも背景色も枠もなく読めたものじゃなかった。

```
# こんな感じで全部ベタテキスト
見出し
本文。コードブロックもこのまま。
npm install something
```

「CSSを書けばいいのはわかるが、どこに書けば記事の中身だけに効くのか」がわからなかった。`<style>` タグをAstroコンポーネントに書けばいいのはわかったが、Markdownから生成されたHTMLには自動でクラスが付かない。何のセレクタを書けばいいのかわからなかった。

---

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3

---

## 試したこと・うまくいかなかったこと

**レイアウトファイルの `<style>` タグにセレクタを書いた → 全く効かなかった**

最初、レイアウトファイル（`PostLayout.astro`）の `<style>` タグにセレクタを書いてみた。

```astro
<style>
  h2 { font-size: 1.5rem; }
  p { line-height: 1.8; }
</style>
```

スタイルが全く効かなかった。Astroの `<style>` タグはデフォルトでscoped CSSになっていて、コンポーネント固有のハッシュが自動で付く。ブラウザのDevToolsでDOMを確認したら

```html
<h2 data-astro-cid-j3ewsqit>見出し</h2>
```

というようにCIDが付いていたが、CSSの方は `h2[data-astro-cid-j3ewsqit]` のようにコンポーネント自身のCIDを前提にしたセレクタになっていた。Markdownから生成されたHTMLには同じCIDが付かないので、scoped styleは記事コンテンツに効かない仕組みだった。

**`<style is:global>` にした → サイト全体に効いた**

次に `<style is:global>` にして試した。

```astro
<style is:global>
  h2 { font-size: 1.5rem; }
</style>
```

今度は効いた。でもサイト全体の `h2` に効いてしまって、ナビゲーションのタイトルやサイドバーの見出しまで変わってしまった。ナビゲーションバーのロゴテキストが突然大きくなって全体のレイアウトが崩れた。記事の中身だけに絞れていなかった。

**`.prose` クラスを直接 `<slot />` に付けようとした → エラー**

Tailwindのtypographyプラグインを使おうと思って `<slot class="prose" />` と書いてみた。Astroのビルドエラーになった。

```
Error: The "slot" element doesn't accept a "class" attribute.
```

`<slot />` は直接クラスを付けられない。ラッパーの `<div>` で囲む必要があると気づいた。

**セレクタを `article h2` にして `<slot />` を `<article>` で包んだ → 解決**

セレクタを `article h2` に変えて、レイアウトで `<slot />` を `<article>` タグで包む形にしてみた。

```astro
<article>
  <slot />
</article>
```

これでようやく記事の中身だけにスタイルが効くようになった。コードブロックのスタイルも `pre` だけに書いたらインラインコードの `code` と干渉してしまい、`pre code { background: none; }` を別途書く必要があると気づくまでにまた時間がかかった。

---

## 解決策

### 方法：グローバルCSSファイルを使う

`src/styles/global.css` を作成してレイアウトファイルでimportする。

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
article table { border-collapse: collapse; width: 100%; margin-bottom: 1rem; }
article th, article td { border: 1px solid #e5e7eb; padding: 0.5rem 0.75rem; }
article th { background: #f9fafb; }
```

レイアウトファイルでimportして、`<slot />` を `<article>` タグで囲む。

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

`<slot />` がMarkdownの内容に展開される。`article` タグで囲むことで `article h2` などのセレクタが記事の中身だけに効く。

### Tailwindを使っている場合

`@tailwindcss/typography` プラグインを使うと `prose` クラス一発でMarkdown向けのスタイルが揃う。

```bash
npm install @tailwindcss/typography
```

```js
// tailwind.config.mjs
export default {
  plugins: [require('@tailwindcss/typography')],
};
```

```astro
<div class="prose prose-lg max-w-none">
  <slot />
</div>
```

Tailwindを使っていないなら前述のグローバルCSS方式の方がシンプルだった。Tailwindを導入するだけでビルド設定がかなり増えるので、スタイルのためだけに入れるのはコスパが悪かった。

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

frontmatterの `layout` パスはMarkdownファイルからの相対パスで書く。`src/pages/posts/` に記事がある場合、`src/layouts/` のレイアウトへのパスは `../../layouts/PostLayout.astro` になる。

---

## ハマったポイント

- Astroの `<style>` タグはデフォルトでscoped CSSになっている。Markdownから生成されたHTMLにはコンポーネントのCIDハッシュが付かないので、scoped styleは効かない。DevToolsでCSSを確認したら `h2[data-astro-cid-xxxxxx]` という形になっていて、Markdownには同じCIDがないとわかって初めて理由が理解できた
- `<style is:global>` で書いたらサイト全体の要素に効いてしまった。ナビゲーションの見出しまで変わってレイアウト崩壊した。セレクタを `article h2` のように `article` で限定することで記事内だけに絞れた。さらに `<slot />` を `<article>` タグで囲む構造にすることで完結した
- Markdownの `<slot />` には直接クラスを付けられない。`<slot class="prose" />` と書いたらAstroのビルドエラーになった。`<div class="prose"><slot /></div>` のようにラッパーで囲む形にすると対応できる
- コードブロックのスタイルは `pre` だけでなく `pre code` にも書く必要があった。`article code { background: #f3f4f6; }` と書くとインラインコードに背景色が付くが、コードブロックの中の `code` にも同じ背景色が入ってしまう。`article pre code { background: none; }` を追加してリセットする対応が必要だったと気づくまでに30分かかった
- レイアウトファイルのパスをfrontmatterで指定するとき、相対パスで書かないと動かない。`/layouts/PostLayout.astro` と書いたら404になった。`../../layouts/PostLayout.astro` のように相対パスで書くのが正しかった。`src/pages/posts/` から見て2段上が `src/` で、そこから `layouts/` に入ると覚えた

---

## よくある質問

**Q: シンタックスハイライトを付ける方法は？**
Astroはデフォルトでシンタックスハイライトが有効。`npm run build` したビルド結果や `npm run dev` のページで確認すると色が付いているはず。テーマを変えたい場合は `astro.config.mjs` の `markdown.shikiConfig.theme` で変更できる。ダークテーマなら `'github-dark'` や `'one-dark-pro'` が見やすかった。

**Q: Markdownの画像にスタイルを当てるには？**
`article img { max-width: 100%; height: auto; }` をglobal.cssに追加する。これで画像がはみ出さなくなる。さらに `border-radius: 8px; margin: 1.5rem 0;` を足すとブログらしい見た目になった。

**Q: コードブロックにファイル名を表示できますか？**
Astroのデフォルトのシンタックスハイライト（Shiki）では直接は表示できない。remark/rehypeプラグインを使う方法もあるが、設定が複雑だった。代わりにコメントでファイル名を書く方法が一番手軽だった：` ```js\n// src/config.js` のように先頭行にコメントで書くと見てわかりやすかった。

**Q: Tailwindのtypographyプラグインは必要ですか？**
不要。global.cssで自分でスタイルを書けば同じ結果になる。ただしTypographyプラグインは見出しの余白・フォントサイズ・コードブロックのスタイルまでまとめて設定してくれるので、Tailwindを既に使っているならプラグインを使う方が早かった。Tailwindを使っていないならグローバルCSS方式の方がシンプルだった。

---

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
