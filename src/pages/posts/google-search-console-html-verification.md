---
title: 'Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順'
date: '2026-05-20'
category: 'SEO'
---

## やりたかったこと

Astro + Cloudflare Pagesで公開しているサイトをGoogle Search Consoleに登録したかった。

## 環境

- Astro
- Cloudflare Pages
- Google Search Console

## 手順

### 1. Google Search Consoleで所有権確認を開始

1. https://search.google.com/search-console を開く
2. 「URLプレフィックス」にサイトのURLを入力
3. 「続行」→「HTMLファイル」の認証方法が表示される
4. 認証用HTMLファイルをダウンロード

### 2. HTMLファイルをpublicフォルダに配置

```
プロジェクト名/public/googleXXXXXXXXXXXXXXXX.html
```

`src/` ではなく `public/` フォルダに置く。

### 3. pushしてデプロイ

```
git add .
git commit -m "add google search console verification"
git push
```

### 4. Google Search Consoleで確認

デプロイ完了後に「確認」ボタンを押す。

### 5. サイトマップを送信

左メニュー「サイトマップ」→ `sitemap-index.xml` と入力して「送信」。

## ハマったポイント

- HTMLファイルは `public/` に置く（`src/` では動かない）
- デプロイ完了前に「確認」を押しても失敗する
- 確認後もHTMLファイルを削除しないこと

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
