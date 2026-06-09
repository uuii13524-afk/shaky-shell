---
title: 'Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順'
date: '2026-05-04'
category: 'SEO'
layout: '../../layouts/PostLayout.astro'
description: 'Google Search ConsoleにAstro+Cloudflare Pagesのサイトを登録するHTMLファイル認証の手順を解説。ファイルの設置方法から確認まで紹介します。'
---

## やりたかったこと

Astro + Cloudflare Pagesで公開したブログをGoogle Search Consoleに登録しようとした。ドメイン認証とHTMLファイル認証の2種類が出てきて、HTMLファイル認証を選んだはいいが、Astroのどこにファイルを置けば本番URLでアクセスできるのかわからなかった。`src/`に置いたら404になって詰まった。

## 環境

- Astro 5.2.3
- Cloudflare Pages（Freeプラン）
- Google Search Console（2026年5月時点）
- Windows 11
- Node.js 20.11.0

## 試したこと・うまくいかなかったこと

最初、認証ファイル（`googleXXXXXXXXXXXXXXXX.html`）をAstroの`src/pages/`に置いてみた。ローカルで`npm run dev`してURLにアクセスしたら「404 Not Found」が返ってきた。Astroのページは`.astro`拡張子じゃないといけないのかと思って、`.html`ファイルをそのまま置くのが正しいのかどうかわからなかった。

次に`src/pages/`に置いたまま`npm run build`してdistフォルダの中を確認した。認証ファイルが含まれていなかったので、そもそも`src/pages/`でも`.html`は通らないのかと思って調べた。実は`src/pages/`にHTMLファイルを置けばビルドに含まれるが、Astroのページとして処理されてしまうことが後でわかった。

「デプロイしてから確認ボタンを押せばいい」と思ってファイルを`src/pages/`に置いたままCloudflare Pagesにデプロイし、Search Consoleで確認ボタンを押したら「所有権を確認できませんでした」と出た。アクセスしてみたらAstroによって変換されたHTMLになっていて、Googleが期待するファイルの内容と変わっていたのが原因だった。

## 解決策

認証ファイルは`public/`フォルダに置く。`public/`に置いたファイルはAstroのビルド処理を通らずそのまま`dist/`にコピーされるので、ファイルの内容が変更されない。

### 1. Google Search Consoleで認証ファイルをダウンロード

1. `https://search.google.com/search-console` を開く
2. 「URLプレフィックス」にサイトのURL（`https://yourdomain.com`）を入力して「続行」
3. 「HTMLファイル」のタブを選択
4. 認証用HTMLファイルをダウンロード（`googleXXXXXXXXXXXXXXXX.html` という名前）

### 2. publicフォルダに配置する

```
my-astro-site/
├── public/
│   └── googleXXXXXXXXXXXXXXXX.html  ← ここに置く
├── src/
│   └── pages/
└── astro.config.mjs
```

`src/pages/`ではなく`public/`に置くのがポイント。

### 3. ローカルで動作確認してからpush

```bash
npm run build
ls dist/googleXXXXXXXXXXXXXXXX.html  # distに含まれているか確認
```

確認できたらpush。

```bash
git add public/googleXXXXXXXXXXXXXXXX.html
git commit -m "add google search console verification"
git push
```

### 4. Cloudflare Pagesのデプロイ完了後に確認

Deploymentsタブでビルドが完了したことを確認してから、Search Consoleの「確認」ボタンを押す。

ブラウザで`https://yourdomain.com/googleXXXXXXXXXXXXXXXX.html`にアクセスして、認証コードが書かれた内容が表示されれば設置OK。

### 5. サイトマップを送信する

所有権確認が完了したら、左メニュー「サイトマップ」で `sitemap-index.xml` を送信する。AstroのサイトマップはデフォルトでこのURLで生成される。

サイトマップを事前に設定していない場合は[Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)で設定してから送信する。

## ハマったポイント

- HTMLファイルは`public/`に置く。`src/pages/`に置くとAstroが内容を変換してしまい、Googleの所有権確認に失敗する。これに気づくまで2回デプロイを無駄にした
- デプロイ完了前に「確認」ボタンを押しても必ず失敗する。Cloudflare PagesのDeploymentsタブで「Success」になるまで待ってから押す必要がある
- 確認後も認証HTMLファイルを削除してはいけない。Search ConsoleはURLにアクセスできるかを定期的に確認しているので、消すと「所有権を失効しました」という通知が来ることがある
- 「URLプレフィックス」と「ドメイン」の2種類の登録方法があって、ドメイン認証の方がサブドメインも一括で管理できるが、DNS設定が必要で難しい。HTMLファイル認証は手順が明確で確実
- サイトマップのURLを送信するとき、`sitemap.xml`と入力したら「読み取れませんでした」と出た。Astroが生成するのは`sitemap-index.xml`なのでそちらを入力する必要があった

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
