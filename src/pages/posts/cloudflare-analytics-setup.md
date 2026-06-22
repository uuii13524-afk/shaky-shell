---
title: 'Cloudflare AnalyticsをAstroサイトに設定する方法'
date: '2026-05-19'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'Cloudflare AnalyticsをAstroサイトに設置する方法を解説。Cookieなし・無料で使えるアクセス解析ツールのスクリプト設置手順を紹介します。'
---

## やりたかったこと

Astroブログをcloudflare Pagesで公開して1ヶ月経った頃、「どのページが読まれているか」を確認したくなった。Google Analyticsを入れようとしたが、CookieのConsent設定が面倒で後回しにしていた。「Cloudflare PagesならCloudflareのAnalyticsが使えるらしい」という話を見かけて試してみた。

Cloudflareダッシュボードの「Analytics & Logs」を開いたが、「Traffic」「Security」「Workers」みたいなタブしかなくて「Web Analytics」がどこにあるかわからなかった。15分ほど探し回った。

## 環境

- Windows 11
- Astro 5.2.3
- Cloudflare Pages（Freeプラン）
- Node.js 20.11.0

## 試したこと・うまくいかなかったこと

「Cloudflare Pagesに自動でAnalyticsが有効になる」という情報を見て何も設定せずにダッシュボードを眺めていた。確かにページビューの数字は出ていたが、ページ別の詳細が見られなかった。後でわかったのだが、「Cloudflare PagesのAnalytics」と「Cloudflare Web Analytics」は別サービスで、Cloudflare Pagesに付いているのはページビュー数程度の簡易なもの。ページ別の詳細データを見たい場合は「Web Analytics」を別途設定してスクリプトを貼る必要があった。この違いに気づくまで「なぜページ別が見えないのか」と30分近く悩んだ。

スクリプトタグをAstroのコンポーネントに貼り付けようとして、`src/components/Analytics.astro`を作ってそこにscriptタグを書いた。でもそのコンポーネントをレイアウトにimportするのを忘れてデプロイした。2週間分のデータが一切取れていなかった。ローカルの`npm run dev`でもbeaconスクリプトは動かないので、import忘れに気づくにはデプロイ後にDevToolsで確認するしかなかった。

次にスクリプトタグをコピーしてレイアウトに直接貼ったが、データがダッシュボードに全く反映されなかった。DevToolsのNetworkタブで確認したら`beacon.min.js`のリクエストに`403`が返ってきていた。ダッシュボードからスクリプトタグをコピーするときに改行が混入して、`data-cf-beacon`のトークンが途中で切れていたのが原因だった。

## 解決策

### 1. Web Analyticsでサイトを登録する

Cloudflareダッシュボードの左サイドバーから「Analytics & Logs」→「Web Analytics」を選ぶ。

「Web Analytics」が左サイドバーの項目一覧に見当たらない場合は、「Analytics & Logs」の中に折りたたまれているか、アカウントレベルのメニューに入ってしまっている可能性がある。`dash.cloudflare.com/[アカウントID]/web-analytics`に直接アクセスするとすぐに開けた。

「Add a site」ボタンを押してドメインを入力するとスクリプトタグが発行される。

```html
<script defer src='https://static.cloudflareinsights.com/beacon.min.js'
  data-cf-beacon='{"token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}'></script>
```

`token`の部分は各サイト固有の32文字の値になる。スクリプトタグ全体をコピーボタンで一括コピーする。ドラッグ選択でコピーすると途中に改行が混入することがある。

### 2. Astroのレイアウトファイルに追加する

```astro
---
// src/layouts/BaseLayout.astro
---
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <slot name="head" />
  </head>
  <body>
    <slot />
    <script defer src='https://static.cloudflareinsights.com/beacon.min.js'
      data-cf-beacon='{"token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}'></script>
  </body>
</html>
```

全ページで計測したい場合は、全ページが使うベースレイアウトの`</body>`直前に追加する。特定ページだけ計測したい場合は、そのページのレイアウトファイルかページファイル（`.astro`）内に追加する。

Astroのコンポーネントとして切り出す場合はimportを忘れずに。

```astro
---
// src/layouts/BaseLayout.astro
import Analytics from '../components/Analytics.astro';
---
...
<Analytics />
```

### 3. デプロイして動作確認する

デプロイ後にブラウザのDevToolsを開き（F12）、「Network」タブで`beacon.min.js`のリクエストを確認する。

```
GET https://static.cloudflareinsights.com/beacon.min.js
Status: 200
```

200が返っていれば計測できている。`403`が返っている場合はトークンが正しくコピーできていないので、ダッシュボードで再確認してスクリプトタグを貼り直す。

データがダッシュボードに反映されるまで数時間かかることがある。設置直後は「データなし」が続くが、翌日以降に確認すると数字が入っている。

## 確認できるデータ

- ページビュー数・ユニーク訪問者数
- ページ別のアクセス数
- 参照元（どこからリンクを辿ってきたか）
- 国別アクセス

Googleアナリティクスと違い、セッション単位の行動フローや滞在時間の詳細は見られない。「どのページが読まれているか」を確認する程度の用途には十分だった。

## ハマったポイント

- 「Cloudflare Pages Analytics」と「Cloudflare Web Analytics」は別サービス。Cloudflare PagesのDeploymentsタブで見える数字は簡易なもので、ページ別の詳細は見れない。詳細を見るには「Web Analytics」を別途設定してスクリプトを貼る必要があった
- スクリプトタグを別コンポーネントに切り出してからレイアウトへのimportを忘れた。`npm run dev`ではbeaconスクリプトが動かないのでローカルでは気づけない。デプロイ後にDevToolsの「Network」タブで`beacon.min.js`のリクエストが出ているか確認するのが唯一の確認方法だった
- スクリプトタグをダッシュボードからドラッグコピーしたら途中に改行が入ってトークンが切れた。`403`が返ってきてデータが入らなかった。コピーボタンでの一括コピーが確実。ペースト後にトークンの文字列が途切れていないかを確認する習慣が必要だった
- データ反映に数時間かかることがある。設置直後に「0のまま」でパニックになったが、翌日に確認したら普通にデータが入っていた。即時反映ではないので1日待ってから確認するのが正しい手順だった
- Cloudflare Web AnalyticsはCookieを使わないのでGDPRやePrivacy対応のCookieバナーが不要だった。Google Analyticsを使う場合のConsent管理の手間がなくてシンプルだった

Analyticsを設置したついでに、[AstroでSEOに必要なmetaタグを設定する方法](/posts/astro-seo-meta-tags)も合わせて対応しておくとサイトの計測基盤が一通り整う。

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
