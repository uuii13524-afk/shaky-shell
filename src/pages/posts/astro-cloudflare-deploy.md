---
title: 'AstroをCloudflare Pagesにデプロイする手順'
date: '2026-05-03'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'AstroサイトをCloudflare Pagesにデプロイする手順を解説。GitHubとの連携設定・ビルドコマンドの指定・カスタムドメインの設定方法までわかりやすく紹介します。'
---

## やりたかったこと

Astroで作ったブログをCloudflare Pagesで公開しようとした。VercelからCloudflareに移行する目的だったが、Cloudflare PagesのUIがVercelと全然違って、最初どこから設定を始めればいいかわからなかった。

MediumでAstro+Cloudflareのデプロイ記事を見つけて読んでいたのだが、2年前の記事だった。スクリーンショットのUIが現在のCloudflareと全然違って「Pages」という独立したメニューが左サイドバーにあるように見えていた。今は「Workers & Pages」という項目にまとまっていて、記事の通りに操作しても「その画面がない」という状態になった。記事の日付を確認せずに参考にしたのが最初のミスだった。

「Create application」を押したらWorkers用の画面が出てきて、Pagesの設定入口がどこにあるかわからなくなった。Vercelなら「New Project」→GitHubリポジトリを選ぶだけで繋がるのに、Cloudflareは全然違う流れになっていた。

最終的に初回デプロイ完了まで3時間かかった。2回目以降は5分でできるようになった。

3時間のトラブルは大きく3段階に分かれていた。「UI上でPagesの設定に入れない」「ビルドコマンドの設定ミス」「環境依存のビルドエラー」の3つだった。最初にこの3段階を知っていれば1時間以下で終わっていたと思う。

VercelのFreeプランはTeamメンバー数や帯域に制限があるが、Cloudflare PagesのFreeプランは月500回のビルドと月500GBの転送量が上限で、個人ブログの規模ではまず引っかからない。コスト面での移行メリットはあった。

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3
- GitHub（リポジトリ作成済み）
- Cloudflare Pages（Freeプラン）

## 試したこと・うまくいかなかったこと

**「Create application」でWorkers画面が出た → Pages入口が見つからない**

Cloudflareの「Workers & Pages」→「Create application」を押したら「Create a Worker」という画面になった。「Connect to Git」のようなボタンがなく、PagesへのGitHub接続がどこにあるか全くわからなかった。左サイドバーに「Pages」という独立したメニューはない。「Workers & Pages」が両方を兼ねているとわかるまで10分以上右往左往した。

「Create application」を押した後の画面の**下の方**に「Looking to deploy Pages? Get started here」という小さいリンクがあった。上部だけ見ていると気づかない。このリンクを見つけてから先に進めた。

**Framework presetを手動入力した → Node.jsバージョン不一致でビルド失敗**

ビルドコマンドを「`npm run build`」、出力ディレクトリを「`dist`」と手動で入力した。ビルドは失敗した。

```
error TS2339: Property 'xxx' does not exist on type 'ImportMeta'
```

ローカルのNode.js 20でコンパイルできるコードが、CloudflareのデフォルトNode.js 18環境でTypeScriptエラーになっていた。Framework presetで「Astro」を選べばNode.jsの推奨バージョンも適用されるのに、手動入力したせいで環境変数の設定漏れが起きた。この時点で2回ビルドを無駄にした。

**`devDependencies`に入れたパッケージが本番ビルドでエラー**

```
Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'sharp'
```

`sharp`を`devDependencies`に入れていたのが原因。Cloudflareの本番ビルドは`dependencies`のみをインストールする。ローカルでは`npm install`で全部入っているから気づかなかった。

`@astrojs/sitemap`プラグインで`site`オプション未設定のエラーも出た。

```
[@astrojs/sitemap] No `site` option is set in your Astro config.
```

ローカルのdevモードではスキップされてもCloudflareのproductionビルドでは必須になる設定がいくつかあった。ローカルテストだけでは発見できないバグがこの段階で2件出た。

## 解決策

### 1. Astroをインストールして動作確認

```bash
npm create astro@latest
cd プロジェクト名
npm run dev
```

`http://localhost:4321` でAstroの画面が出れば成功。

### 2. GitHubにpush

```bash
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
```

pushする前に`.gitignore`に`node_modules/`と`.env`が含まれているか確認する。`node_modules`をpushしてしまうとリポジトリサイズが膨大になってpushに数分かかるようになる。

```bash
cat .gitignore
# node_modules/、.env、dist/ が含まれていればOK
```

### 3. Cloudflare PagesにGitHubリポジトリを接続する

1. 「Workers & Pages」→「Create application」を押す
2. **画面下部**の「Looking to deploy Pages? Get started here」をクリック（見落としやすい）
3. 「Import an existing Git repository」→「Get started」
4. GitHubアカウントを認証してリポジトリを選択
5. ビルド設定でFramework presetを**「Astro」**に変更する

Framework presetでAstroを選ぶと以下が自動入力され、推奨Node.jsバージョンも適用される。

```
Build command: npm run build
Build output directory: dist
```

6. 「Save and Deploy」でデプロイ開始

初回ビルドは2〜3分かかる。Deploymentsタブでビルドログをリアルタイムで確認できる。

### 4. ビルドが失敗した時の対処

よくあるエラーと対処法：

```
Error: Cannot find module 'sharp'
```
→ `package.json`の`dependencies`（`devDependencies`ではない）に`sharp`があるか確認する。

```
error: No matching version found for node@xx.x.x
```
→ Settings → Environment variablesで`NODE_VERSION=20`を追加する。

```
[@astrojs/sitemap] No `site` option is set in your Astro config.
```
→ `astro.config.mjs`に`site: 'https://yourdomain.com'`を追加する。

ビルドログは「Download logs」でテキストとして保存してから`Error:`で検索すると原因が一発で見つかる。ブラウザのログビューアをスクロールしながら探すより圧倒的に速い。

```
Installing dependencies...   ← ここでエラーが出れば依存問題
Building Astro site...       ← ここでエラーが出ればビルド設定問題
  → rendering pages...       ← ここでエラーが出ればページ内容の問題
```

### 5. 環境変数の設定

Settings → Environment variablesで追加する。`NODE_VERSION=20`は最初から設定しておくと安定する。

```
NODE_VERSION = 20
```

TypeScriptエラーがローカルでは出ないのにCloudflareで出る場合、ほぼ確実にNode.jsバージョン差異が原因。`NODE_VERSION`を揃えるだけで解消するエラーが多かった。

### 6. デプロイ完了後の確認

Deploymentsタブで「Success」になったら`*.pages.dev`のURLが発行される。デプロイ直後は「522 Connection Timed Out」が出ることがある。CloudflareのエッジへのDNS伝播中で、5分待ってからリロードすると正常に表示された。

### 7. プレビューデプロイの活用

`main`以外のブランチへのpushに対しても自動でプレビューURLが発行される。

```bash
git checkout -b feature/add-new-section
# 変更を加えた後
git push origin feature/add-new-section
```

プレビューURLはDeploymentsタブの該当ビルドから確認できる。本番環境変数は引き継がれないので注意。

### 8. 以降のpushの流れ

一度設定が完了すれば、`git push`するだけで自動デプロイが走る。

```bash
git add src/pages/posts/new-post.md
git commit -m "add new post"
git push
```

pushから1〜2分でDeploymentsタブに新しいビルドが来て、2〜3分でデプロイ完了する。

### 9. 直前のデプロイに戻したい場合

DeploymentsタブのビルドエントリにあるRollback機能で以前のデプロイに戻せる。

1. Deploymentsタブを開く
2. 戻したいビルドの「…」→「Rollback to this deployment」
3. 1〜2分で以前のビルドが本番に反映される

Rollbackはデプロイ先を変えるだけでGitのコミット履歴には影響しない。Rollback後に`git push`すれば最新コミットの内容で再びビルドが走る。

## ハマったポイント

- 「Create application」を押すとWorkers用の画面になる。Pages用は画面**下部**の「Looking to deploy Pages? Get started here」という目立たないリンクから入る。上部だけ見ていると絶対に見つからない。Vercelとは全く違うUI設計で、最初にここで10分以上時間を取られた
- Framework presetで「Astro」を選ばずに手動でビルドコマンドを入力すると、推奨Node.jsバージョンの環境変数が設定されない。ローカルはNode.js 20でもCloudflareのデフォルトが古くて、TypeScriptのエラーがCloudflareのビルドでだけ出る状態になった。最初からFramework presetを「Astro」に設定するだけで避けられる失敗だった
- `devDependencies`に入れたパッケージはCloudflareの本番ビルドでインストールされない。ローカルでは`npm install`で全部入っているから気づかないが、Cloudflare側では`dependencies`のみが対象。Astroのintegrationなど実行時に必要なものは`dependencies`に入れる
- ローカルのdevモードでは正常に動いても、Cloudflareのproductionビルドで初めて発覚するエラーがある。`@astrojs/sitemap`の`site`オプション未設定エラーがその一つで、devモードではスキップされる。全てのプラグインのドキュメントにある「Required for production」の項目は最初から確認しておくべきだった
- 2年前のChrome記事のUIスクリーンショットが現在のCloudflareと全然違っていた。「Workers」と「Pages」が統合されて「Workers & Pages」になったのが2023年頃で、古い記事では「Pages」が独立メニューに見えていた。GitHubやCloudflare関連のチュートリアルは記事の日付を必ず確認してから参考にする

## 関連記事

- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
## より詳しく学びたい方へ

この記事の内容をさらに深掘りした実践ガイドをZennで公開しています。

[VPS・GitHub Actions・Cloudflare 実践構築ガイド](https://zenn.dev/errnotes/books/6ec5fb4840cea2)
