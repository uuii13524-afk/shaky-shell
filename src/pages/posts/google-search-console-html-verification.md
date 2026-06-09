---
title: 'Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順'
date: '2026-05-04'
category: 'SEO'
layout: '../../layouts/PostLayout.astro'
description: 'Google Search ConsoleにAstro+Cloudflare Pagesのサイトを登録するHTMLファイル認証の手順を解説。ファイルの設置方法から確認まで紹介します。'
---

## やりたかったこと

Astro + Cloudflare Pagesで公開したブログをGoogle Search Consoleに登録しようとした。プロパティの追加画面でドメイン認証とHTMLファイル認証の2種類が出てきて、DNS設定が不要なHTMLファイル認証を選んだ。認証ファイル（`googleXXXXXXXXXXXXXXXX.html`）をダウンロードしてAstroのプロジェクトに置こうとしたが、どこに置けば本番URLでアクセスできるのかわからなかった。`src/`の中に置いたら404になった。

## 環境

- Astro 5.2.3
- Cloudflare Pages（Freeプラン）
- Google Search Console（2026年5月時点）
- Windows 11
- Node.js 20.11.0

## 試したこと・うまくいかなかったこと

最初、認証ファイル（`googleXXXXXXXXXXXXXXXX.html`）をAstroの`src/pages/`に置いてみた。ローカルで`npm run dev`して`http://localhost:4321/googleXXXXXXXXXXXXXXXX.html`にアクセスしたら「404 Page not found」が返ってきた。Astroのページは`.astro`拡張子じゃないといけないのかと思って、`.html`ファイルをそのまま置けるのかどうか調べ始めた。

実は`src/pages/`に`.html`ファイルを置いてもビルドには含まれる。ただし**Astroがそのファイルを自分のレイアウトやコンポーネントで処理してしまう**ので、Google が期待するファイルの内容と変わってしまう。Search Consoleの認証ファイルには`google-site-verification`のmetaタグが含まれているが、Astroのレイアウトで囲まれると認証コードの判定が狂う。

「とりあえずデプロイしてから確認してみよう」と`src/pages/`に置いたままCloudflare Pagesにpushした。デプロイ完了後にSearch Consoleの「確認」ボタンを押したら「所有権を確認できませんでした」と出た。ブラウザで認証ファイルのURLにアクセスしたら、完全なHTMLページになっていて（Astroのレイアウトが適用された状態）、ファイルの内容が変わっていたのが原因だった。

2回デプロイしてようやく「public/」フォルダが正解だとわかった。

## 解決策

認証ファイルは`public/`フォルダに置く。`public/`に置いたファイルはAstroのビルド処理を通らずそのまま`dist/`にコピーされるので、ファイルの内容が一切変更されない。

### 1. Google Search Consoleで認証ファイルをダウンロード

1. `https://search.google.com/search-console` を開く
2. 左上の「プロパティを選択」→「プロパティを追加」
3. 「URLプレフィックス」にサイトのURL（`https://yourdomain.com`、末尾スラッシュなし）を入力して「続行」
4. 確認方法の一覧から「HTMLファイル」を選択
5. 認証用HTMLファイルをダウンロード（`googleXXXXXXXXXXXXXXXX.html` という名前）

### 2. publicフォルダに配置する

プロジェクトのルートにある`public/`フォルダにダウンロードしたファイルをそのまま置く。

```
my-astro-site/
├── public/
│   └── googleXXXXXXXXXXXXXXXX.html  ← ここに置く
├── src/
│   └── pages/
└── astro.config.mjs
```

`src/pages/`ではなく`public/`に置くのが唯一の正解。

### 3. ローカルで動作確認してからpush

ビルドして`dist/`に認証ファイルが含まれているか確認してからpushする。

```bash
npm run build
ls dist/google*.html  # distに含まれているか確認
```

`dist/`に認証ファイルが出ていれば正しい設置場所。

```bash
git add public/googleXXXXXXXXXXXXXXXX.html
git commit -m "add google search console verification file"
git push
```

### 4. Cloudflare Pagesのデプロイ完了後に確認

Deploymentsタブでビルドの「Success」を確認してからSearch Consoleの「確認」ボタンを押す。まだデプロイ中にボタンを押すと確認に失敗する。

ボタンを押す前に、ブラウザで直接認証ファイルのURLにアクセスして内容を確認する。

`https://yourdomain.com/googleXXXXXXXXXXXXXXXX.html` にアクセスして、以下のような1行だけのテキストが表示されればOK。

```
google-site-verification: googleXXXXXXXXXXXXXXXX.html
```

完全なHTMLページが表示されてしまう場合は`public/`ではなく`src/pages/`に置いてしまっている。

### 5. 所有権確認後にサイトマップを送信する

所有権確認が完了したら、左メニュー「サイトマップ」で`sitemap-index.xml`を入力して「送信」をクリックする。AstroにサイトマッププラグインとサイトマップはデフォルトでこのURLで生成される。

サイトマップを事前に設定していない場合は[Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)で設定してから送信する。

## ハマったポイント

- HTMLファイルは必ず`public/`に置く。`src/pages/`に置くとAstroが内容をレイアウトやコンポーネントで囲んでしまい、Googleの所有権確認が失敗する。この間違いに気づくまで2回デプロイを無駄にした
- デプロイ完了前に「確認」ボタンを押しても必ず失敗する。Cloudflare PagesのDeploymentsタブで「Success」になってから少なくとも1分待ってから押す
- 確認後も認証HTMLファイルを削除してはいけない。Search ConsoleはURLにアクセスできるかを定期的に確認しているので、削除すると後日「所有権を確認できなくなりました」というメールが届いて確認が無効になる
- 「URLプレフィックス」と「ドメイン」の2種類の登録方法があって、ドメイン認証はwwwあり・なし両方をまとめて管理できるが、CloudflareのDNS設定でTXTレコードを追加する手順が必要。HTMLファイル認証はDNS操作が不要なので手順が明確だった
- サイトマップのURLをSearch Consoleに送信する時、`sitemap.xml`と入力したら「フェッチできませんでした」というエラーが出た。Astroが生成するのは`sitemap-index.xml`なのでこちらを入力する必要があった
- `dist/`の中身を確認せずにpushして「何度ボタンを押しても失敗する」と悩むくらいなら、先に`npm run build && ls dist/google*.html`で確認するのが正解。ビルド後に`dist/`にファイルが存在しなければ設置場所が間違っている

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
