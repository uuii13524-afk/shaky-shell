---
title: 'AstroをCloudflare Pagesにデプロイする手順'
date: '2026-05-03'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'AstroサイトをCloudflare Pagesにデプロイする手順を解説。GitHubとの連携設定・ビルドコマンドの指定・カスタムドメインの設定方法までわかりやすく紹介します。'
---

## やりたかったこと

Astroで作ったブログサイトをCloudflare Pagesで公開しようとした。これまでVercelしか使ったことがなかったが、Cloudflareの方がCDNの速度が良いと聞いて移行を考えた。Cloudflare PagesのUIがVercelと全然違って、最初どこから設定を始めればいいのかわからなかった。

「Workers & Pages」を開いたらWorkers用の画面しか見当たらず、Pagesの設定に入る場所が見つけにくくて詰まった。Vercelだと「New Project」を押してGitHubリポジトリを選ぶだけで全部繋がるのに、Cloudflareは同じノリでやったら全然違う画面が出てきた。結果的に最初のデプロイ完了まで3時間近くかかったが、2回目以降は5分でできるようになった。

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3
- GitHub（リポジトリ作成済み）
- Cloudflare Pages（Freeプラン）

## 試したこと・うまくいかなかったこと

最初、Cloudflareのダッシュボードにログインして「Workers & Pages」→「Create application」を押したら、「Create a Worker」という画面が出てきた。「Connect to Git」のようなボタンが見当たらず、Pagesの設定がどこにあるのかわからなかった。Workersの設定画面でAstroのリポジトリを繋ごうと右往左往した。

左側のサイドバーをすべて確認したが、「Pages」という独立したメニューはなかった。「Workers & Pages」が両方を兼ねているとわかるまで10分以上かかった。「Create application」を押した後の画面に**小さく**「Looking to deploy Pages? Get started here」というリンクがあって、それをクリックしないとPages用の画面に入れない作りだった。このリンクは画面の下の方にあって、上部だけ見ていると絶対に気づかない。

ビルドコマンドの設定で手動入力しようとして`npm run build`と`dist`を入れたが、Framework presetで「Astro」を選べば自動で入力されることを後から知った。手動でも問題ないが、Astroのpresetを使わないと`NODE_VERSION`などの推奨環境変数が設定されず、Cloudflare側のNode.jsバージョンが古くてビルドが失敗することがあった。

最初のビルドが`Error: Cannot find module`で失敗したが、ログをよく見たら`node_modules`が正しくインストールされていなかった。ローカルでは`npm install`済みなのに、Cloudflareは毎回クリーンな状態からビルドするのでリポジトリの`package.json`に書かれた依存が正しくないと失敗する。ローカルで`npm run build`が通るからCloudflareでも通ると思っていたが、Node.jsのバージョンが違うと同じコードでもエラーになることがあった。

```
Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'sharp'
```

このエラーが出た時は`sharp`を`dependencies`ではなく`devDependencies`に入れていたのが原因だった。本番ビルドでは`devDependencies`はインストールされないので、使うパッケージは必ず`dependencies`に入れる必要があった。

さらに詰まったのが、Cloudflare PagesのGitHub認証画面で「Only select repositories」を選んでいたこと。後から新しいリポジトリを別に作ってCloudflareに接続しようとしたら、リポジトリの一覧に出てこなかった。「All repositories」に変更するか、GitHubのSettings → Applications → Cloudflare Pages → Repositoriesから個別に追加する必要があった。

## 解決策

### 1. Astroをインストールして動作確認

```bash
npm create astro@latest
cd プロジェクト名
npm run dev
```

`http://localhost:4321` でAstroの画面が出れば成功。

### 2. GitHubにpush

GitHubへの初回pushが初めての場合は、[GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)も参考に。

```bash
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
```

pushする前に`.gitignore`に`node_modules/`と`.env`が含まれているか確認しておく。`node_modules`をpushしてしまうとCloudflareのビルドに時間がかかる上、ローカルとCloudflare側の環境差異で意図しない動作になることがある。

### 3. Cloudflare PagesにGitHubリポジトリを接続する

1. Cloudflareダッシュボードで「Workers & Pages」を開く
2. 「Create application」ボタンを押す
3. **画面下部**にある「Looking to deploy Pages? Get started here」をクリック（これを見落としやすい）
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

```
[@astrojs/sitemap] No `site` option is set in your Astro config.
```
→ `astro.config.mjs`に`site`プロパティがない。`site: 'https://yourdomain.com'`を追加する。

```
Build exceeded the time limit of 20 minutes
```
→ ビルド時間超過。画像の最適化処理が重い場合に起きやすい。`sharp`による画像変換を無効にするか、ビルドするページ数を絞る。

環境変数を設定したい場合はSettings → Environment variablesで追加する。`NODE_VERSION=20`は最初から設定しておくと安定する。

### 5. デプロイ完了後の確認

Deploymentsタブで「Success」になったら`*.pages.dev`のURLが発行される。ブラウザで開いてサイトが表示されれば成功。

カスタムドメインを設定したい場合は[XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)を参照。環境変数が必要な場合は[Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)も参考になる。

### 6. プレビューデプロイの活用

Cloudflare Pagesは`main`ブランチ以外のpushに対しても自動でプレビューURLを発行する。`feature/`ブランチでコードを書いてpushすると、本番とは別の`xxxxxxxx.プロジェクト名.pages.dev`という形のURLでプレビューが確認できる。

```bash
git checkout -b feature/add-new-section
# 変更を加えた後
git push origin feature/add-new-section
```

プレビューURLはDeploymentsタブの該当ビルドから確認できる。本番デプロイ前に見た目を確認できるので、大きな変更時に使うと安心だった。

### 7. 以降のpushの流れ

一度設定が完了すれば、あとは`git push`するだけで自動デプロイが走る。

```bash
# 記事を追加・編集した後
git add src/pages/posts/new-post.md
git commit -m "add new post"
git push
```

pushから1〜2分でDeploymentsタブに新しいビルドが来て、2〜3分でデプロイ完了する。ビルドが来ない場合は[Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)を確認する。

## ハマったポイント

- 「Create application」を押すとWorkers用の画面が出る。Pages用は**画面下部**の「Looking to deploy Pages? Get started here」という目立たないリンクから入る。ページの上部だけ見ていると絶対に見つからない。Vercelとは全く違うUI設計だった
- Framework presetで「Astro」を選ぶとビルド設定が自動入力されるだけでなく、推奨のNode.jsバージョンも適用される。手動で`npm run build`と`dist`を入れても一応動くが、Node.jsのバージョン差異でビルドが失敗しやすい。最初から「Astro」を選んでおけば避けられる失敗だった
- GitHubの認証ページで「Only select repositories」を選ぶと、後から新しいリポジトリを追加した時にCloudflareの一覧に出てこない。その場合はGitHubのSettings → Applications → Cloudflare Pages → Repositoriesから追加できる。「なぜ新しいリポジトリが出てこないのか」と20分悩んだことがあった
- ローカルで`npm run build`が通るのに、Cloudflare側で失敗するのはNode.jsのバージョン違いが多い。ローカルはNode.js 20でもCloudflareのデフォルトが16や18の可能性がある。Environment variablesで`NODE_VERSION=20`を指定すると一致させられた
- `devDependencies`に入れたパッケージはCloudflareの本番ビルドでインストールされない。ローカルでは`npm install`で全部入っているので気づかないが、Cloudflare側では`dependencies`のみが対象。Astroのintegrationなど実行時に必要なものは`dependencies`に入れる
- デプロイ後に`*.pages.dev`のURLが発行されるが、ブラウザでアクセスしたら「522 Connection timed out」が出ることがある。数分待ってからリロードすると直った。デプロイ直後はまだDNSが伝播中のことがある。5分待っても出ない場合はDeploymentsタブのビルドログを再確認する
- `npm run build`で生成される`dist/`フォルダの中身を確認すると、Cloudflareに転送されるファイルを把握できる。`ls dist/`でファイル構成を確認してから、意図しないファイルが含まれていないかチェックする習慣が付いた

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
