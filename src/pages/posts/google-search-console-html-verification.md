---
title: 'Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順'
date: '2026-05-04'
category: 'SEO'
layout: '../../layouts/PostLayout.astro'
description: 'Google Search ConsoleにAstro+Cloudflare Pagesのサイトを登録するHTMLファイル認証の手順を解説。ファイルの設置方法から確認まで紹介します。'
---

## やりたかったこと

Astro + Cloudflare Pagesで公開したブログをGoogle Search Consoleに登録しようとした。プロパティの追加画面でドメイン認証とHTMLファイル認証の2種類が出てきて、最初はドメイン認証（DNS TXTレコード方式）を試した。

CloudflareのDNS設定でTXTレコードを追加してSearch Consoleの「確認」ボタンを押したが、「所有権を確認できませんでした」が何度押しても出続けた。1時間試した末に諦めてHTMLファイル認証に切り替えた。

HTMLファイル認証はファイルを1個置くだけで手順が明確だった。認証ファイル（`googleXXXXXXXXXXXXXXXX.html`）をダウンロードしてAstroのプロジェクトに置こうとしたが、どこに置けば本番URLでアクセスできるのかがわからなかった。最初に`src/`の中に置いたら404になった。

「なぜ404なのか」を理解するまでに2回デプロイを無駄にした。Astroの`public/`と`src/pages/`の役割を理解していなかったのが根本原因で、`src/pages/`に`.html`ファイルを置くとAstroのレイアウトで囲まれてしまい、認証ファイルの内容が変わってしまうことを知らなかった。

Search Consoleの登録そのものは5分で終わる作業のはずが、ファイルの設置場所を3回間違えて合計3回デプロイし直すことになった。

さらに確認後の落とし穴もあった。認証ファイルを「もう不要」と思って削除したら、1ヶ月後に「所有権を確認できなくなりました」というメールが届いた。Googleは認証後も定期的に認証ファイルにアクセスして所有権を継続確認しているので、削除してはいけない。

## 環境

- Astro 5.2.3
- Cloudflare Pages（Freeプラン）
- Google Search Console（2026年5月時点）
- Windows 11
- Node.js 20.11.0

## 試したこと・うまくいかなかったこと

**認証ファイルを`src/pages/`に置いた → Astroのレイアウトが適用されてGSCが失敗**

認証ファイルを`src/pages/googleXXXXXXXXXXXXXXXX.html`に置いた。ローカルで`npm run dev`して確認したら404になった。「Astroのページは`.astro`拡張子じゃないといけないのかも」と思いながらとりあえずCloudflare Pagesにpushした。

デプロイ後にSearch Consoleの「確認」ボタンを押したら「所有権を確認できませんでした」と出た。ブラウザで認証ファイルのURLにアクセスしたら、Astroのナビゲーションが入った完全なHTMLページが表示されていた。Googleが期待するレスポンスは1行のシンプルなテキストだが、Astroのレイアウトが適用されてしまって全然違う内容になっていた。

```
google-site-verification: googleXXXXXXXXXXXXXXXX.html
```

これが返るはずのところに、ヘッダー・ナビ・フッター付きの完全なHTMLページが返っていた。

**`public/`に移したが、デプロイ前に確認ボタンを押してしまった → 失敗**

2回目は`public/`に移した。だがDeploymentsタブの「Success」を確認する前に焦って「確認」ボタンを押してしまった。まだCloudflareのCDNにファイルが届いていない状態でGoogleが確認に来たから当然失敗した。「デプロイ成功」→「少し待つ」→「確認ボタンを押す」という順番を守るだけで解決できた話だった。

**ブラウザでは正常なのにGSCだけ失敗し続けた → Cloudflareのキャッシュが原因**

3回目の試みでは手順は正しくできた。ブラウザで認証ファイルのURLを開いたら正しい1行のテキストが表示されていた。念のためcurlで確認しても正常だった。

```bash
curl https://yourdomain.com/googleXXXXXXXXXXXXXXXX.html
```

なのにSearch Consoleの「確認」ボタンを押しても失敗し続けた。ブラウザでもcurlでも正しい内容が返っているのに、なぜGSCだけ失敗するのか30分近く混乱した。

原因はCloudflareのCDNキャッシュだった。Googlebotが認証ファイルにアクセスした時、CDNキャッシュに以前の失敗バージョン（Astroレイアウト適用版または404レスポンス）が残っていた。ブラウザとcurlは最新版を取得できているが、Googlebotにはキャッシュが返されていた状態だった。

Cloudflareの「Purge Cache」→「Purge Everything」でキャッシュを全削除してから再度「確認」ボタンを押したら通った。

## 解決策

認証ファイルは`public/`フォルダに置く。`public/`に置いたファイルはAstroのビルド処理を通らずそのままコピーされるので、内容が変わらない。

### 1. Google Search Consoleで認証ファイルをダウンロード

1. `https://search.google.com/search-console` を開く
2. 「プロパティを追加」→「URLプレフィックス」にサイトのURL（`https://yourdomain.com`）を入力
3. 確認方法から「HTMLファイル」を選択
4. 認証用HTMLファイルをダウンロード（`googleXXXXXXXXXXXXXXXX.html`）

「URLプレフィックス」と「ドメイン」の2種類の登録方法がある。HTMLファイル認証はDNS操作が不要なので手順が明確。最初はHTMLファイル認証で登録して、慣れてからドメインプロパティに移行するのがわかりやすかった。

### 2. publicフォルダに配置する

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
ls dist/google*.html
```

ファイルが`dist/`に出ていれば正しい設置場所。出ない場合はファイルが`public/`以外に置かれている。

`npm run preview`で確認する方法もある。

```bash
npm run preview
# ブラウザで http://localhost:4321/googleXXXXXXXXXXXXXXXX.html を開く
```

1行のテキストが表示されればOK。完全なHTMLページが表示される場合は`public/`ではなく`src/pages/`に置いてしまっている。

```bash
git add public/googleXXXXXXXXXXXXXXXX.html
git commit -m "add google search console verification file"
git push
```

### 4. Cloudflare Pagesのデプロイ完了後に確認

Deploymentsタブで「Success」を確認してから「確認」ボタンを押す。ボタンを押す前にブラウザで直接URLにアクセスして内容を確認する。

`https://yourdomain.com/googleXXXXXXXXXXXXXXXX.html`にアクセスして以下の1行だけのテキストが表示されればOK。

```
google-site-verification: googleXXXXXXXXXXXXXXXX.html
```

curlでキャッシュ状態を確認するとより確実。

```bash
curl -I https://yourdomain.com/googleXXXXXXXXXXXXXXXX.html
```

レスポンスヘッダーの`cf-cache-status`が`HIT`の場合、Googlebotにもキャッシュが返される可能性がある。Search Consoleの確認前に「Purge Cache」でキャッシュを削除してから押すのが確実。

```
cf-cache-status: HIT   ← キャッシュが返されている状態
```

### 5. 認証が通らない場合の追加確認

「確認」ボタンを押しても失敗する場合、Search Consoleの「URL検査」ツールで認証ファイルのURLを直接テストする。「Googleでテスト」ボタンを押すとGooglebotが取得したレスポンスを確認できる。ここで「404」や「正しくない内容」が表示されている場合は設置場所か権限の問題。

`robots.txt`で`Disallow: /google*.html`のような設定になっていてGooglebotが認証ファイルにアクセスできていないケースも起きる。`robots.txt`に認証ファイルをブロックする設定が含まれていないか確認する。

### 6. 所有権確認後にサイトマップを送信する

左メニュー「サイトマップ」で`sitemap-index.xml`を入力して「送信」をクリックする。`sitemap.xml`ではなく`sitemap-index.xml`が正しいファイル名なので注意。

サイトマップを事前に設定していない場合は[Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)で設定してから送信する。

### 7. 認証ファイルを削除しない

所有権確認が完了した後も、`public/google*.html`ファイルを削除してはいけない。Googleは定期的に認証ファイルのURLにアクセスして所有権を継続確認している。削除すると数週間〜1ヶ月後に「所有権を確認できなくなりました」というメールが届いてプロパティが無効になる。

`.gitignore`に認証ファイルを誤って追加しないよう注意する。所有権が失効しても「再確認」の手順で元に戻せるが、失効期間中のデータは欠損するので早めに気づいて対処するのが重要。

## ハマったポイント

- HTMLファイルは必ず`public/`に置く。`src/pages/`に置くとAstroのレイアウトが適用されてファイルの内容が変わってしまい、Googleの所有権確認が失敗する。この間違いに気づくまでデプロイを2回無駄にした
- ブラウザとcurlで認証ファイルの内容が正常に見えているのにSearch Consoleの確認が失敗し続けた。Cloudflare CDNキャッシュに古いバージョンが残っていてGooglebotにはキャッシュが返されていたのが原因だった。「curl正常 → GSC失敗」という状態はキャッシュを真っ先に疑う
- デプロイ完了前に「確認」ボタンを押しても必ず失敗する。DeploymentsタブのSuccessを確認してから少なくとも1〜2分待ってから押す。焦って早押しすると余計な調査時間が発生する
- 確認後も認証HTMLファイルを削除してはいけない。「確認が完了したからもう不要」と思って削除したら1ヶ月後にプロパティが無効になるメールが届いた。一度この失敗をしてから「削除禁止リスト」を自分で作った
- サイトマップのURLをSearch Consoleに送信する時、`sitemap.xml`と入力したら「フェッチできませんでした」というエラーが出た。Astroが生成するのは`sitemap-index.xml`なのでこちらを入力する。この違いを知らずに何度か無駄に送信した

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
