---
title: 'AstroをCloudflare Pagesにデプロイする手順'
date: '2026-05-03'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'AstroサイトをCloudflare Pagesにデプロイする手順を解説。GitHubとの連携設定・ビルドコマンドの指定・カスタムドメインの設定方法までわかりやすく紹介します。'
---

## やりたかったこと

Astroで作ったブログサイトをCloudflare Pagesで公開しようとした。これまでVercelしか使ったことがなかったが、Cloudflareの方がCDNの速度が良いと聞いて移行を考えた。Cloudflare PagesのUIがVercelと全然違って、最初どこから設定を始めればいいのかわからなかった。「Workers & Pages」を開いたらWorkers用の画面しか見当たらず、Pagesの設定に入る場所が見つけにくくて詰まった。

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3
- GitHub（リポジトリ作成済み）
- Cloudflare Pages（Freeプラン）

## 試したこと・うまくいかなかったこと

最初、Cloudflareのダッシュボードにログインして「Workers & Pages」→「Create application」を押したら、「Create a Worker」という画面が出てきた。「Connect to Git」のようなボタンが見当たらず、Pagesの設定がどこにあるのかわからなかった。Workersの設定画面でAstroのリポジトリを繋ごうと右往左往した。

左側のサイドバーをすべて確認したが、「Pages」という独立したメニューはなかった。「Workers & Pages」が両方を兼ねているとわかるまで10分以上かかった。「Create application」を押した後の画面に**小さく**「Looking to deploy Pages?」というリンクがあって、それをクリックしないとPages用の画面に入れない作りだった。

ビルドコマンドの設定で手動入力しようとして`npm run build`と`dist`を入れたが、Framework presetで「Astro」を選べば自動で入力されることを後から知った。手動でも問題ないが、Astroのpresetを使わないと`NODE_VERSION`などの推奨環境変数が設定されず、Cloudflare側のNode.jsバージョンが古くてビルドが失敗することがあった。

最初のビルドが`Error: Cannot find module`で失敗したが、ログをよく見たら`node_modules`が正しくインストールされていなかった。ローカルでは`npm install`済みなのに、Cloudflareは毎回クリーンな状態からビルドするのでリポジトリの`package.json`に書かれた依存が正しくないと失敗する。

## 解決策

### 1. Astroをインストールして動作確認

```bash
npm create astro@latest
cd プロジェクト名
npm run dev
```

`http://localhost:4321` でAstroの画面が出れば成功。

### 2. GitHubにpush

GitHubへの初回pushが初めての場合は、[GitHubへの初回pushの手順](/posts/github-first-push)も参考に。

```bash
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
```

### 3. Cloudflare PagesにGitHubリポジトリを接続する

1. Cloudflareダッシュボードで「Workers & Pages」を開く
2. 「Create application」ボタンを押す
3. **画面下部**にある「Looking to deploy Pages? Get started」をクリック（これを見落としやすい）
4. 「Import an existing Git repository」→「Get started」
5. GitHubアカウントを認証してリポジトリを選択
6. ビルド設定でFramework presetを「**Astro**」に変更する

Framework presetでAstroを選ぶと以下が自動入力される。

```
Build command: npm run build
Build output directory: dist
```

7. 「Save and Deploy」でデプロイ開始

初回ビルドは2〜3分かかる。Deploymentsタブでビルドログをリアルタイムで確認できる。

### 4. ビルドが失敗した時の対処

初回デプロイでビルドエラーになる場合は、Deploymentsタブ→該当ビルド→「View build logs」でエラー内容を確認する。

よくあるエラー：

```
Error: Cannot find module 'sharp'
```
→ `package.json`のdependenciesに`sharp`が入っているか確認する。`devDependencies`に入れてしまうと本番ビルドで読み込めない。

```
error: No matching version found for node@xx.x.x
```
→ Node.jsのバージョン不一致。Settings → Environment variablesで`NODE_VERSION`を`20`に指定する。

```
Build failed: 'astro' is not recognized
```
→ `npm install`が失敗している可能性。`package.json`の内容をローカルと比較して依存が正しいか確認する。

### 5. デプロイ完了後の確認

Deploymentsタブで「Success」になったら`*.pages.dev`のURLが発行される。ブラウザで開いてサイトが表示されれば成功。

カスタムドメインを設定したい場合は[XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)を参照。環境変数が必要な場合は[Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)も参考になる。

## ハマったポイント

- 「Create application」を押すとWorkers用の画面が出る。Pages用は**画面下部**の「Looking to deploy Pages? Get started」という目立たないリンクから入る。ページの上部だけ見ていると絶対に見つからない
- Framework presetで「Astro」を選ぶとビルド設定が自動入力されるだけでなく、推奨のNode.jsバージョンも適用される。手動で`npm run build`と`dist`を入れても一応動くが、Node.jsのバージョン差異でビルドが失敗しやすい
- GitHubの認証ページで「Only select repositories」を選ぶと、後から新しいリポジトリを追加した時にCloudflareの一覧に出てこない。その場合はGitHubのSettings → Applications → Cloudflare Pages → Repositoriesから追加できる
- ローカルで`npm run build`が通るのに、Cloudflare側で失敗するのはNode.jsのバージョン違いが多い。ローカルはNode.js 20でもCloudflareのデフォルトが違う可能性がある。Environment variablesで`NODE_VERSION=20`を指定すると一致させられた
- 「Build failed」の赤いアイコンをクリックした後にビルドログを展開する操作がわかりにくかった。Deploymentsタブ→ビルドのリンクをクリック→「Build logs」タブという手順で確認できる
- デプロイ後に`*.pages.dev`のURLが発行されるが、ブラウザでアクセスしたら「522 Connection timed out」が出ることがある。数分待ってからリロードすると直った。デプロイ直後はまだDNSが伝播中のことがある

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
