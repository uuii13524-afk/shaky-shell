---
title: 'Cloudflare PagesのGitHub自動デプロイが動かない時の対処法'
date: '2026-05-04'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'git pushしてもCloudflare Pagesに変更が反映されない原因と解決方法を解説。GitHub連携の確認やビルドコマンドの見直しポイントを紹介します。'
---

## 症状

git pushしてもCloudflare Pagesに変更が反映されない。
Deploymentsタブに新しいデプロイが来ない。

```
This project is disconnected from your Git account.
This may cause deployments to fail.
```

## 環境

- Cloudflare Pages
- GitHub
- Astro

## 原因1：CloudflareとGitHubの接続が切れている

### 解決方法

1. 「Git repository」の「Manage」をクリック
2. GitHubアカウントを再認証する
3. 空のコミットをpushして強制デプロイ

```
git commit --allow-empty -m "force deploy"
git push
```

## 原因2：古いコミットがデプロイされている

```
git commit --allow-empty -m "force deploy"
git push
```

## 原因3：ビルドエラーが発生している

Deploymentsタブ→「View build logs」でエラー内容を確認する。

## ハマったポイント

- 空のコミットpushが最も確実な強制デプロイ方法
- ビルドログを最初に確認する習慣をつける

そもそもAstroをCloudflare Pagesに繋いでいない場合は[AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)を参考に初期設定を確認してほしい。環境変数が足りていてビルドが失敗している場合は[Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)も参照。

## 関連記事

- [Cloudflare PagesがGitHubと切断された時の対処法](/posts/cloudflare-github-disconnect)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)

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
