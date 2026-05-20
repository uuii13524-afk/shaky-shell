---
title: 'Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順'
date: '2026-05-20'
category: 'SEO'
---

## やりたかったこと

Astro + Cloudflare Pagesで公開しているサイトをGoogle Search Consoleに登録したかった。
HTMLファイル認証の手順が少しわかりにくかったのでまとめる。

## 環境

- Astro
- Cloudflare Pages
- Google Search Console

## 手順

### 1. Google Search Consoleで所有権確認を開始

1. https://search.google.com/search-console を開く
2. 「今すぐ開始」をクリック
3. 「URLプレフィックス」にサイトのURLを入力（例：https://errsolved.com）
4. 「続行」を押す
5. 「HTMLファイル」の認証方法が表示される
6. 認証用HTMLファイル（例：googleb23d6b96de3576b8.html）をダウンロード

### 2. HTMLファイルをAstroプロジェクトに配置

ダウンロードしたHTMLファイルを以下のフォルダに置く。

```
プロジェクト名/public/googleXXXXXXXXXXXXXXXX.html
```

`public/` フォルダに置くことで、ビルド後のサイトのルートに配置される。
例：https://errsolved.com/googleXXXXXXXXXXXXXXXX.html でアクセスできるようになる。

### 3. GitHubにpushしてデプロイ

```
git add .
git commit -m "add google search console verification"
git push
```

Cloudflare Pagesが自動デプロイするまで1〜2分待つ。

### 4. Google Search Consoleで確認

1. Google Search Consoleに戻る
2. 「確認」ボタンを押す
3. 「所有権を確認しました」と表示されれば完了

### 5. サイトマップを送信

1. 左メニュー「サイトマップ」をクリック
2. 入力欄に `sitemap-index.xml` と入力
3. 「送信」を押す

## ハマったポイント

- HTMLファイルは `src/` ではなく `public/` フォルダに置く必要がある
- `src/` に置いてもビルド後のサイトに反映されない
- デプロイ完了前に「確認」を押しても失敗する。デプロイ完了を待ってから押す
- 確認後もHTMLファイルを削除しないこと。削除すると所有権確認が無効になる

## 補足

サイトマップのURLはAstroのsitemapプラグインを使っている場合は `sitemap-index.xml` になる。
Google Search Consoleへのインデックス反映には数日〜2週間程度かかる場合がある。
