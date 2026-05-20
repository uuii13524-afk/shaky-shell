---
title: 'AstroでMarkdownのスタイルを設定する方法'
date: '2026-05-20'
category: 'Astro'
---

## やりたかったこと

AstroでMarkdownで書いた記事にスタイルを当てたかった。
デフォルトではMarkdownにスタイルが当たらないので見た目が素っ気ない。

## 環境

- Astro 5

## 方法1：グローバルCSSを使う

`src/styles/global.css` を作成してMarkdownの要素にスタイルを当てる。

```css
/* src/styles/global.css */
article h2 { font-size: 1.5rem; margin-top: 2rem; border-bottom: 2px solid #eee; }
article h3 { font-size: 1.2rem; margin-top: 1.5rem; }
article p { line-height: 1.8; margin-bottom: 1rem; }
article code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
article pre { background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 8px; overflow-x: auto; }
article ul, article ol { padding-left: 1.5rem; margin-bottom: 1rem; }
article li { margin-bottom: 0.5rem; }
article a { color: #0066cc; }
```

レイアウトファイルでインポートする。

```astro
---
import '../styles/global.css';
---
```

## 方法2：@tailwindcss/typographyを使う

Tailwind CSSを使っている場合は `@tailwindcss/typography` が便利。

```bash
npm install @tailwindcss/typography
```

```astro
<article class="prose">
  <slot />
</article>
```

## レイアウトファイルの設定

Markdownファイルにレイアウトを適用する。

```markdown
---
title: '記事タイトル'
layout: '../../layouts/PostLayout.astro'
---
```

```astro
---
// src/layouts/PostLayout.astro
const { frontmatter } = Astro.props;
---
<html>
  <head>
    <title>{frontmatter.title}</title>
  </head>
  <body>
    <article>
      <h1>{frontmatter.title}</h1>
      <slot />
    </article>
  </body>
</html>
```

## ハマったポイント

- Markdownから生成されたHTMLには自動でクラスが付かない。CSS設定は要素セレクタで行う
- `prose` クラスは `@tailwindcss/typography` が必要
- レイアウトファイルのパスはMarkdownファイルからの相対パスで書く

## 関連記事

- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
