---
title: 'Cloudflare Pagesで環境変数を設定する方法'
date: '2026-05-13'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'Cloudflare Pagesのダッシュボードで環境変数（APIキーなど）を設定する手順を解説。本番環境とプレビュー環境への設定方法も紹介します。'
---

## 設定手順

1. Cloudflareダッシュボード→プロジェクト→「Settings」→「Variables and Secrets」
2. 「Add variable」→変数名と値を入力して保存

## コードから参照する

```javascript
// Astroの場合
const apiKey = import.meta.env.MY_API_KEY;
```

## 開発環境（ローカル）

`.env` ファイルを作成する。

```
MY_API_KEY=ローカル用のキー
```

`.env` は `.gitignore` に追加する。

## ハマったポイント

- 環境変数を追加したら再デプロイが必要
- `.env` をGitHubにpushしないよう注意

## 関連記事

- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
- [GitHub ActionsでSecretsを使って秘密情報を管理する方法](/posts/github-actions-secrets)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
