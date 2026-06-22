---
title: 'Cloudflare Pagesのビルドログの見方とエラーの対処法'
date: '2026-05-09'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'Cloudflare Pagesのビルドログの確認方法とよくあるビルドエラーの原因・解決策を解説。ダッシュボードからログを開く手順も紹介します。'
---

## やりたかったこと

AstroサイトをCloudflare Pagesにデプロイしたらビルドが失敗した。Deploymentsタブに「Failed」と表示されているが、何が原因なのかわからなかった。「View build logs」を押したら大量のログが出てきて、どこを見ればいいかわからないまま5分以上スクロールし続けた。

```
✘ [ERROR] Could not resolve "@astrojs/sitemap"
```

というエラーが出ていたが、ローカルでは正常にビルドが通っていた。「ローカルで動くのになぜCloudflareで失敗するのか」という状況が何度も続いて、毎回ビルドログの読み方に迷っていた。

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3
- Cloudflare Pages（Freeプラン）

## 試したこと・うまくいかなかったこと

最初、ビルドログのページを開いてからスクロールバーを手で動かしながらエラーを探していた。ログが1000行以上あって、どこにエラーがあるかわからないまま何分もスクロールしていた。

ブラウザのCtrl+Fで「Error」を検索しようとしたが、Cloudflareのビルドログビューアはリアルタイムで行が追加される仕組みのためか、ブラウザの検索機能が正常に機能しなかった。

`npm warn deprecated`が大量に出ていて、最初はそのWARNINGが原因だと思ってパッケージを調べ始めた。30分ほど調べてから「WARNINGはビルド失敗に直接関係ない」とわかった。`npm warn deprecated react@17.0.2`のような警告は単にパッケージのバージョンが非推奨になっているという通知で、これだけが原因でビルドが止まることはない。ERRORとWARNINGの違いを意識せずにいたせいで、見るべきものを見逃していた。

## 解決策

### ビルドログの開き方

1. Cloudflareダッシュボード → 「Workers & Pages」
2. 対象プロジェクト → 「Deployments」タブ
3. 「Failed」になっているビルドのリンクをクリック
4. 「Build log」タブを開く

「Failed」の文字はリンクになっていない場合がある。ビルドのタイムスタンプかビルド番号のリンクをクリックすると詳細ページに入れる。

### 効率的なエラーの見つけ方

**「Download logs」でテキストとして保存してから検索するのが圧倒的に速かった。**

ビルドログページ右上の「Download logs」ボタンを押すとテキストファイルがダウンロードされる。VSCodeで開いてCtrl+FでERRORを検索する。

```
# ダウンロードしたログをVSCodeで検索
Error: Cannot find module
✘ [ERROR]
Build failed
```

ログは大きく3フェーズに分かれている。エラーがどのフェーズで出ているかで原因が変わる。

```
Installing dependencies...      ← ここのエラー = package.jsonの依存問題
Building Astro site...          ← ここのエラー = ビルド設定やコードの問題
  → rendering pages...          ← ここのエラー = ページコンテンツの問題
```

依存関係のエラーはログの前半、レンダリングエラーはログの後半に出る。「ログの最後を見ればいい」という思い込みで前半を読み飛ばすと本当のエラーを見逃す。

### 成功時のログの流れ

```
11:23:04.123 Cloning repository...
11:23:06.204 Installing project dependencies
11:24:02.891 npm install completed in 56.7s
11:24:03.012 Building with Astro
11:24:04.445   ✓ 26 pages built in 3.21s
11:24:04.446 Build complete
11:24:05.001 Uploading...
11:24:11.232 Success: Your site was deployed
```

このフローで最後に「Success」が出れば正常完了。

### よくあるエラーと対処法

```
✘ [ERROR] Could not resolve "@astrojs/sitemap"
```
→ `@astrojs/sitemap`が`devDependencies`に入っている。本番ビルドでは`devDependencies`はインストールされない。`npm install @astrojs/sitemap --save`で`dependencies`に移す。

```
error TS2339: Property 'xxx' does not exist on type 'ImportMeta'
```
→ CloudflareのデフォルトNode.jsバージョンがローカルより古い。Settings → Environment variables で`NODE_VERSION=20`を追加して再デプロイする。

```
Astro.glob is not a function
```
→ Astro 5以降で`Astro.glob()`が廃止された。`import.meta.glob()`に書き換える。

```
[@astrojs/sitemap] No `site` option is set in your Astro config.
```
→ `astro.config.mjs`に`site: 'https://yourdomain.com'`を追加する。ローカルのdevモードではこのエラーが出ないのにビルド時だけ出る。

```
Build exceeded the time limit of 20 minutes
```
→ ビルド時間超過。`sharp`による画像最適化が重い場合に起きやすい。

```
✘ [ERROR] rendering /posts/xxx...
  Error: Cannot read properties of undefined
```
→ 記事のfrontmatterに必須プロパティが抜けているか、レイアウト側で`undefined`チェックをしていない。ローカルで`npm run build`を実行して同じエラーが出るか確認する。

### 古いコミットがデプロイされているとき

ビルドは成功しているのに古い内容が表示される場合、空コミットで強制的にデプロイをトリガーする。

```bash
git commit --allow-empty -m "force deploy"
git push
```

## ハマったポイント

- `npm warn deprecated`が大量に出ていてWARNINGを原因だと思って調べ続けた。WARNINGはビルド失敗に直接関係しない。`Error:`や`✘ [ERROR]`が出ている行だけを見ればよく、WARNINGは無視していい
- ブラウザのビルドログビューアでスクロールしながらエラーを探すのは1000行超えのログでは現実的でない。「Download logs」でテキスト保存してVSCodeで`ERROR`を全文検索するのが圧倒的に速かった
- ローカルで`npm run build`が通るのにCloudflareで失敗するのは、ほぼNode.jsのバージョン差異か`devDependencies`の問題。この2点を最初に確認するだけで大半のケースが解決できた
- ログの依存インストールフェーズのエラーは前半に出る。「最後にエラーがある」と思い込んでログの後半だけ見ていたら、前半で起きているnpm installの失敗を見落とした
- Deploymentsタブで「Failed」のビルドをクリックしてから「Build log」タブを探す必要がある。「View build logs」というリンクやボタンが見当たらないときは、ビルドのタイムスタンプのリンクをクリックしてから「Build log」タブに入る手順で見つかった

デプロイが全く来ない場合はビルドエラーではなくGitHubとの接続切れが原因のこともある。その場合は[Cloudflare PagesがGitHubと切断された時の対処法](/posts/cloudflare-github-disconnect)を確認してほしい。

## 関連記事

- [Cloudflare PagesがGitHubと切断された時の対処法](/posts/cloudflare-github-disconnect)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
