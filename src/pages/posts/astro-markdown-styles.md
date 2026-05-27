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
