---
title: 'AstroをCloudflare Pagesにデプロイする手順'
date: '2026-05-03'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'AstroサイトをCloudflare Pagesにデプロイする手順を解説。GitHubとの連携設定・ビルドコマンドの指定・カスタムドメインの設定方法までわかりやすく紹介します。'
---

## やりたかったこと

Astroで作ったブログサイトをCloudflare Pagesで公開しようとした。Vercelは使ったことがあったが、Cloudflare PagesのUIが違いすぎて最初どこから設定するのかわからなかった。特に「Workers & Pages」からPagesの設定に入る導線が見つけにくくて詰まった。

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3
- GitHub（リポジトリ作成済み）
- Cloudflare Pages（Freeプラン）

## 試したこと・うまくいかなかったこと

最初、Cloudflareのダッシュボードにログインして「Workers & Pages」→「Create application」を押したらWorkers用の画面が出てきた。「Create Worker」のボタンしか見当たらず、Pagesの設定がどこにあるのかわからなかった。Workers用の画面でAstroのリポジトリを繋ごうとしたが、そもそもPages用の設定項目がなかった。

「Pages」という名前のメニュー項目があるかと左側のサイドバーを全部見たが見つからず、「Workers & Pages」が両方を兼ねた画面だとわかるまで10分くらいかかった。

ビルドコマンドを手動で入力しようとして`npm run build`と入れたところ、Framework presetで「Astro」を選ぶと自動的に設定されることを後から知った。手動入力のまま進めると環境変数が足りなくてビルドが失敗することがあった。

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
3. **画面下部**にある「Looking to deploy Pages? Get started」をクリック（ここが見つけにくい）
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

### 4. デプロイ完了後の確認

`*.pages.dev` のURLが発行される。このURLでサイトが表示されれば成功。

カスタムドメインを設定したい場合は[XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)を参照。環境変数が必要な場合は[Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)も参考になる。

## ハマったポイント

- 「Create application」を押すとWorkers用の画面が出る。Pages用は**画面下部**の「Looking to deploy Pages? Get started」から入る。上部だけ見ていると絶対に見つからない
- Framework presetで「Astro」を選ぶとビルド設定が自動入力される。手動で`npm run build`と`dist`を入れても動くが、presetを使う方が確実
- GitHubの認証ページで「All repositories」ではなく「Only select repositories」を選ぶと、後から追加したリポジトリが一覧に出てこないことがある。その場合はGitHub側のOAuth設定でリポジトリを追加する
- 初回デプロイのビルドが失敗した場合、エラーメッセージはDeploymentsタブ→「View build logs」で確認できる。「Build failed」の赤いアイコンをクリックしてからログを展開する手順がわかりにくかった
- `npm run build`でローカルは通るのに、Cloudflare側でビルドエラーになるのはNode.jsのバージョン違いが原因のことが多い。ビルド設定の「Environment variables」で`NODE_VERSION=20`を指定すると直った

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
