---
title: 'AstroでMarkdownのスタイルを設定する方法'
date: '2026-05-15'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
---

## 方法1：グローバルCSSを使う

`src/styles/global.css` を作成する。

```css
article h2 { font-size: 1.5rem; margin-top: 2rem; }
article p { line-height: 1.8; margin-bottom: 1rem; }
article code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }
article pre { background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 8px; overflow-x: auto; }
```

レイアウトファイルでインポートする。

```astro
---
import '../styles/global.css';
---
```

## レイアウトファイルの設定

```markdown
---
title: '記事タイトル'
layout: '../../layouts/PostLayout.astro'
---
```

## ハマったポイント

- Markdownから生成されたHTMLには自動でクラスが付かない
- レイアウトファイルのパスはMarkdownファイルからの相対パス

## 関連記事

- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [AstroでSEOに必要なmetaタグを設定する方法](/posts/astro-seo-meta-tags)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
